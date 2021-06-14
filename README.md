# Video-Streamer

This is a simple video streamer for use with the usb and integrated Cameras including the Pi Camera.  It streams video in jpg format.
It is particularly useful when you want to same video feed to be consumed by more than one application.  For example a timelapse recording application and to also monitor in real time.


Its written using Python3

**Installation:**
Download to a directory of your choice.

`wget https://github.com/stuartofmt/Video-Streamer/raw/main/videostream.py  -O videostream.py`

then make it executable

`chmod 744 videostream.py`

**Startup:**

python3 videostream.py -port [-camera] [-rotate] [-size] [-host]

Specifying a port is mandatory.

-camera
May be omitted if there is only one camera available.
If there is more than one camera then the camera identifier needs to be specified.
**Note that camera identifiers begin at 0 (zero) for the first camera.**

If the video from the camera does not have the right orientation or size  - this can be fixed with -rotate and / or -size.
-rotate
Defaults to 0 (zero).  Common settings wil be 0, 90, 180, 270
-size
Defaults to your camera's settings. Available settings are:
640 (sets the size to 640 x 480)
1080 (sets the size to 1080 x 760)

Usually -host **will not need to be specified** - it defaults machine you are running the code on.


**Example:**

Start videostream.py and have it stream video on port 8081 rotated 180 deg using the only (default) camera

`python3 ./videostream.py -port 8082 -rotate 180`

Start videostream.py and have it stream video on port 8081 rotated 90 deg using the second camera (identifier 1)

`python3 ./videostream.py -port 8082 -camera 1 -rotate 90`

At startup console messages are printed to confirm correct operation.
There may be some error messages that look like this:
VIDEOIO ERROR: V4L: can't open camera by index 1
These can be safely ignored.

**Accessing the video stream**

The video is accessed using a http link (e.g. using a browser).
The url is of the form:
http://[ ip address]:port/stream

Terminating the program:
The program can be terminated using:
http://[ ip address]:port/terminate
