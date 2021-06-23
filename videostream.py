# Web streaming


# Modified by Stuartofmt
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT
# Updated to use threadingHTTPServer and SimpleHTTPhandler

videostream_version = '1.1.0'

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
    parser.add_argument('-format', type=str, nargs=1, default=['MJPG'], help='Preferred format')
    args = vars(parser.parse_args())

    global host, port, rotate, camera, size, format, allowed_formats

    host = args['host'][0]
    port = args['port'][0]
    rotate = args['rotate'][0]
    camera = args['camera'][0]
    size = abs(args['size'][0])

    format = args['format'][0]
    allowed_formats = ('BGR3', 'YUY2', 'MJPG','JPEG')
    if format not in allowed_formats:
        print(format + 'is not an allowed format')
        format = 'MJPG'
        print('Setting to ' + format)

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
    resolution = []  #  Note: needs to be ordered in size to support later comparisons
    resolution.append([2048, 1080])  # Default
    resolution.append([1920, 1800])
    resolution.append([1280, 720])
    resolution.append([800, 600])
    resolution.append([720, 480])
    resolution.append([640, 480])
    resolution.append([320, 240])
    allowed_formats = ('BGR3', 'YUY2', 'MJPG','JPEG')

    available_resolutions = []
    available_resolutions_str = []
    print('Scanning for available sizes and formats - be patient')
    for res in resolution:
        width = res[0]
        height = res[1]
        for form in allowed_formats:
            stream = cv2.VideoCapture(int(camera))
            stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            fourcc = cv2.VideoWriter_fourcc(*form)
            stream.set(cv2.CAP_PROP_FOURCC,fourcc)
            camwidth = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            camheight = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cc = stream.get(cv2.CAP_PROP_FOURCC)
            camformat = "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])
            reported_resolution = [camwidth, camheight, camformat]
            if reported_resolution not in available_resolutions and camformat in allowed_formats:
                available_resolutions.append(reported_resolution)
                available_resolutions_str.append(str(camwidth) + 'x' + str(camheight) + '(' + camformat + ')')
            stream.release()
    print('The following resolutions are available from the camera: ' + '  '.join(available_resolutions_str))

    if size > len(resolution)-1: # Make sure the index is within bounds
        size = len(resolution)-1
        print('Selected size is not available. Defaulting to the smallest size')

    requested_width = resolution[size][0]
    requested_height = resolution[size][1]
    requested_res = [requested_width, requested_height, format]
    print(requested_res)
    #  Test to see if we have a match in resolution
    test_res = [res for res in available_resolutions if requested_width == res[0] and requested_height == res[1]]
    print(test_res)
    if test_res:
        print('The requested size: ' + str(requested_width) + 'x' + str(requested_height) + ' is available')
        test_format = [form[2] for form in test_res if format == form[2]]
        if test_format:
            print('The requested format: ' + format + ' is available')
            return requested_res
        else:
            print('The requested format: ' + format + ' is not available')
            print('Using an alternative format')
        return test_res[0]

    #  Test for next available resolution
    for res in available_resolutions:
        if res[0] <= requested_width and res[1] <= requested_height:  # Get the first match
            lower_width = res[0]
            lower_height = res[1]
            print('The requested size was not available')
            print('Using a smaller size: ' + str(lower_width) + 'x' + str(lower_height))
            test_res = [res for res in available_resolutions if lower_width == res[0] and lower_height == res[1]]
            if test_res:
                test_format = [form[2] for form in test_res if format == form[2]]
                if test_format:
                    print('The requested format: ' +  format + ' is available')
                    alternate_res = [lower_width, lower_height, format]
                    return alternate_res
                else:
                    print('The requested format: ' + format + ' is not available')
                    print('Using an alternative format')
                    return test_res[0]

    # Nothing matches use lowest default value
    fallback_resolution = [resolution[len(resolution)-1][0], resolution[len(resolution)-1][1], 'YUY2']
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print('There was no resolution match available')
    print('Trying the lowest default: ' + str(fallback_resolution[0]) + 'x' + str(fallback_resolution[1]) + '(' + fallback_resolution[2] + ')')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    return fallback_resolution

def setResolution(size):
    global stream
    selected_format = getResolution(size)
    width = selected_format[0]
    height = selected_format[1]
    format = selected_format[2]
    global stream
    print('Setting the camera resolution to: ' + str(width) + 'x' + str(height) + '(' + format + ')')
    stream = cv2.VideoCapture(int(camera))
    stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    fourcc = cv2.VideoWriter_fourcc(*format)
    stream.set(cv2.CAP_PROP_FOURCC, fourcc)
    stream.set(cv2.CAP_PROP_FPS, 12)  #  Should be a reasonable number

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
    stream.release()
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

    global host, port, rotate, camera, size, format

    thisinstancepid = os.getpid()

    init()

    # What cameras are available
    available_cameras = []
    print('Version: ' + videostream_version)
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
        #stream = cv2.VideoCapture(int(camera))
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
