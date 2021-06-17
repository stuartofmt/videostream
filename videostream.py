# Web streaming


# Modified by Stuartofmt
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT
# Updated to use threadingHTTPServer and SimpleHTTPhandler

import argparse
import cv2
import imutils
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import sys
import socket
import os
import time
import signal

streamVersion = '1.0.0'


def init():
    # parse command line arguments
    parser = argparse.ArgumentParser(
            description='Streaming video http server. V' + streamVersion,
            allow_abbrev=False)
    # Environment
    parser.add_argument('-host', type=str, nargs=1, default=['0.0.0.0'],
                        help='The ip address this service listens on. Default = 0.0.0.0')
    parser.add_argument('-port', type=int, nargs=1, default=[0],
                        help='Specify the port on which the server listens. Default = 0')
    parser.add_argument('-rotate', type=str, nargs=1, default=['0'], help='Rotation. Default = 0')
    parser.add_argument('-camera', type=str, nargs=1, default=[''], help='camera index.')
    parser.add_argument('-size', type=int, nargs=1, default=[0], help='image resolution')
    args = vars(parser.parse_args())

    global host, port, rotate, camera, size

    host = args['host'][0]
    port = args['port'][0]
    rotate = args['rotate'][0]
    camera = args['camera'][0]
    size = abs(args['size'][0])


class StreamingHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global rotate, stream
        if 'favicon.ico' in self.path:
            return
        if self.path == '/stream':
            print('\nStreaming started')
            self.send_response(200)
            self.send_header('Age', '0')
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()

            try:
                while True:
                    ret, buffer = stream.read()
                    width = buffer.shape[1]
                    if rotate != '0':
                        buffer = imutils.rotate(buffer, int(rotate))
                    _, frame = cv2.imencode(".jpg", buffer)
                    try:
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', str(len(frame)))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                    except Exception as e:
                        print('\nClient Disconnected')
                        break
            except Exception as e:
                print('\nRemoved client from ' + str(self.client_address) + ' with error ' + str(e))
        elif self.path == '/terminate':
            self.send_response(200)
            self.end_headers()
            shut_down()
        else:
            self.send_error(404)
            self.end_headers()

def getResolution(size):
    global stream
    resolution = []  #  Note: needs to be ordered in size to support later comparisons
    resolution.append([2048, 1080])  # Default
    resolution.append([1920, 1800])
    resolution.append([1280, 720])
    resolution.append([800, 600])
    resolution.append([720, 480])
    resolution.append([640, 480])
    resolution.append([320, 240])

    available_resolutions = []
    available_resolutions_str = []
    for res in resolution:
        width = res[0]
        height = res[1]
        # Try setting
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        #  See what is reported back
        camwidth = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        camheight = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        reported_resolution = [camwidth, camheight]
        if reported_resolution not in available_resolutions:
            available_resolutions.append(reported_resolution)
            available_resolutions_str.append(str(camwidth) + 'x' + str(camheight))
    print('The following resolutions are available from the camera: ' + '  '.join(available_resolutions_str))

    if size > len(resolution)-1: # Make sure the index is within bounds
        size = len(resolution)-1

    requested_resolution =  resolution[size]
    if requested_resolution in available_resolutions:
        print('Requested Resolution is available')
        return requested_resolution[0], requested_resolution[1]
    else:
        for res in available_resolutions:
            if res[0] <= requested_resolution[0] and res[1] <= requested_resolution[1]:
                print('The requested resolution: ' + str(requested_resolution[0]) + 'x' + str(requested_resolution[1]) + ' is not available')
                print('Using a lower, available resolution')
                return res[0], res[1]

        fallback_resolution = resolution[len(resolution)-1]
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('There was no resolution match available')
        print('Trying the lowest resolution: ' + str(fallback_resolution[0]) + 'x' + str(fallback_resolution[1]))
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        return fallback_resolution[0], fallback_resolution[1]

def setResolution(size):
    width, height = getResolution(size)
    global stream
    print('Setting the camera resolution to: ' + str(width) + 'x' + str(height))
    stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    stream.set(cv2.CAP_PROP_FPS, 24)  #  Should be a reasonable number

def checkIP():
    #  Start the web server
    if (port != 0):
        #  Get the local ip address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))  # doesn't even have to be reachable
            ip_address = s.getsockname()[0]
        except Exception:
            ip_address = '[ip address]'  # If not available - assume the user knows
        finally:
            s.close()

        try:
            sock = socket.socket()
            if sock.connect_ex((host, port)) == 0:
                print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print('Port ' + str(port) + ' is already in use.')
                print('Terminating the program')
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                sys.exit(2)

            print('\nThe video stream can be access from:')
            print('http://' + str(ip_address) + ':' + str(port) + '/stream')
            print('\nIf on the same computer as the camera - you can also try the following:')
            print('localhost:' + str(port) + '/stream')
            print('127.0.0.1:' + str(port) + '/stream')
        finally:
            pass
    else:
        print('\nNo port number was provided - terminating the program')
        shut_down()

def shut_down():
    time.sleep(1)  # give pending actions a chance to finish
    print('\nThe program has been terminated by a user request')
    os.kill(thisinstancepid, 9)


def quit_gracefully(*args):
    print('\n!!!!!! Stopped by SIGINT or CTL+C  !!!!!!')
    shut_down()


"""
Main Program
"""
if __name__ == "__main__":

    signal.signal(signal.SIGINT, quit_gracefully)

    global host, port, rotate, camera, thisinstancepid, stream, camwidth

    thisinstancepid = os.getpid()

    init()

    # What cameras are available
    available_cameras = []
    print('\nScanning for available Cameras')
    for index in range(10):
        stream = cv2.VideoCapture(index)
        if stream.isOpened():
            available_cameras.append(str(index)) # using string for convenience
            stream.release()
    print('\n')

    if len(available_cameras) < 1:
        print('No camera was found')
        print('Verify that the camera is connected and enabled')
        print('Terminating the program')
        sys.exit(2)

    if len(available_cameras) == 1 and camera == '':
        print('No camera was specified but one camera was found and will be used')
        camera = available_cameras[0] # If nothing specified - try the only available camera

    if camera in available_cameras:
        print('\nOpening camera with identifier: '+ camera)
        stream = cv2.VideoCapture(int(camera))
        setResolution(size)
    else:
        if camera == '':
            print('You did not specify a camera and more than one was found.')
        else:
            print('The camera with identifier ' + camera + ' is not available')
        cameralist = ",".join(available_cameras)
        print('The following cameras were detected: ' + cameralist)
        print('Terminating the program')
        sys.exit(2)
    checkIP()
    try:
        server = ThreadingHTTPServer((host, port), StreamingHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
