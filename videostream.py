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
    parser.add_argument('-width', type=int, nargs=1, default=[0], help='image width.')
    parser.add_argument('-height', type=int, nargs=1, default=[0], help='image height.')
    args = vars(parser.parse_args())

    global host, port, rotate, camera, width, height

    host = args['host'][0]
    port = args['port'][0]
    rotate = args['rotate'][0]
    camera = args['camera'][0]
    width = abs(args['width'][0])
    height = abs(args['height'][0])

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
                print(
                    '\nRemoved client from ' + str(self.client_address) + ' with error ' + str(e))
        elif self.path == '/terminate':
            self.send_response(200)
            self.end_headers()
            shut_down()
        else:
            self.send_error(404)
            self.end_headers()

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
        stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        stream.set(cv2.CAP_PROP_FPS, 24)
        # Find default width of camera
        ret, buffer = stream.read()
        camheight = buffer.shape[0]
        camwidth = buffer.shape[1]
        print('\nThe default camera resolution is: ' + str(camwidth) + ' x ' + str(camheight) + ' pixels')
        if (width == 0 and height != 0) or (width != 0 and height == 0):
            print('\nIf -width or -height are specified - BOTH must be specified')
            print('Using the default camera resolution')
        elif(width != 0 and height != 0):
            print('\nSetting the camera resolution to: ' + str(width) + ' x ' + str(height) + ' pixels')
            stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
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
