# camera-test.py

import cv2
import time
import imutils


def findCameras():
    available_cameras = []
    for index in range(0, 20):
        stream = cv2.VideoCapture(index)
        if stream.isOpened():
            available_cameras.append(str(index))   # using string for convenience
        stream.release()
    return available_cameras

def getResolutions(cam):
    resolution = []                  # Note: needs to be ordered in size to support later comparisons
    resolution.append([2048, 1080])  # Default
    resolution.append([1920, 1800])
    resolution.append([1640, 1232])
    resolution.append([1280, 720])
    resolution.append([800, 600])
    resolution.append([720, 480])
    resolution.append([640, 480])
    resolution.append([320, 240])
    allowed_formats = ('BGR3', 'YUY2', 'MJPG','JPEG', 'H264', 'IYUV')   

    available_resolutions = []
    available_resolutions_str = []
    print('\n Scanning for available resolutions and formats -- this can take some time ...')

    #stream = cv2.VideoCapture(int(cam))

    for res in resolution:
        width = res[0]
        height = res[1]
        for form in allowed_formats:
            stream = cv2.VideoCapture(int(camera)) # Make sure we have a new clean connection
            if not stream.isOpened:
                print('Could not open camera: ' + str(camera))
                stream.release()
                break
            stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            fourcc = cv2.VideoWriter_fourcc(*form)
            stream.set(cv2.CAP_PROP_FOURCC, fourcc)
            # Now try to read back
            camwidth = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            camheight = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cc = stream.get(cv2.CAP_PROP_FOURCC)
            camformat = "".join([chr((int(cc) >> 8 * i) & 0xFF) for i in range(4)])
            reported_resolution = [camwidth, camheight, camformat]
            if reported_resolution not in available_resolutions and camformat in allowed_formats:
                available_resolutions.append(reported_resolution)
                available_resolutions_str.append(str(camwidth) + 'x' + str(camheight) + '(' + camformat + ')  ')
            stream.release()
    resolutions_str = ''.join(available_resolutions_str)
    return resolutions_str, available_resolutions 


def display(cam, res):
    if auto is False:
        print('\n\nPress Enter to display next resolution...')
        input()
    print('Will attempt to display this resolution for 10 seconds\n')
    print('Any keypress will close the display\n')

    print('################################################')
    print(res)
    print('################################################')
    print('\n')
    time.sleep(1)

    cap = cv2.VideoCapture(cam)
    if not cap.isOpened:
        print('Could not open camera: ' + str(cam))
        cap.release()
        return
    else:
        print('Opened camera: ' + str(cam))
    
    framerate = 15
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
    format = res[2]
    fourcc = cv2.VideoWriter_fourcc(*format)
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    cap.set(cv2.CAP_PROP_FPS, framerate)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Just to keep things tidy and small
    windowname = 'Camera ' + str(cam) + ' ' + str(res[0]) + ' x ' + str(res[1]) + ' format ' + str(res[2])
    #cv2.namedWindow(windowname, cv2.WINDOW_NORMAL)

    timeout = 0
    starttime = time.time()
    while  time.time() - starttime < 10:  #Display for ~10 sec 
        time.sleep(1/framerate)
        ret, frame = cap.read()
        if ret is False:
            print('No Frame')
            timeout = timeout +1
            if timeout > 1:
                print('Connection timed out')
                break
        else:
            if frame is False:
                print('No frame')
            newwidth = 640     
            resized = imutils.resize(frame, width=newwidth, inter=cv2.INTER_LINEAR)    
            cv2.imshow(windowname, resized)
        if cv2.waitKey(1) != -1:
            break

    cap.release() 
    cv2.destroyAllWindows()
    return

def testCamera(cam):
    
    resolution_str, resolutions = getResolutions(int(cam))
    print('\n\nThe following resolutions are available from camera:  ' + str(cam) + '\n\n' + resolution_str)

    for res in resolutions:
        display(int(cam), res)

## Start of program

keypress=''
while keypress not in ['a', 'm', 'q']:        
    print('\nSelect an option and press enter\n')
    print('(a) - automatic, will cycle through all combinations')
    print('(m) - manual, changes combinations on keypress')
    print('(q) - quit')
    keypress = input()
   
auto = False
if keypress == 'a':
    auto = True
elif keypress == 'q':
    sys.exit(0)

cameras = findCameras()
if len(cameras) == 0:
    print('No cameras were found')
    sys.exit(1)
print('\n')
keypress=''
while keypress not in cameras and keypress != 'a':
    for camera in cameras:
        print('Found camera with index: ' + str(camera))
    print('\nSelect which camera(s) to test and press enter\n')
    print('(a) - will cycle through all cameras')
    print('(n) - "n" is a camera index')
    keypress = input()
camera = ''    
if keypress == 'a':
    pass
else:
    camera = keypress
if camera == '':
    for camera in cameras:
        testCamera(camera)
else:
    testCamera(camera)