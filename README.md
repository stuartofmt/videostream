# videostream

This is a simple video streamer for use with the usb and integrated cameras including the Pi camera.  It streams video in jpg format from a url.
It is particularly useful when you want to same video feed to be consumed by more than one application.  For example a timelapse recording application and to also monitor in real time.

<br>videostream is designed to run continuously and can accept a http command to terminate the program.  Typically, you would use a browser but curl or other means can be used.<br>


### Version 1.0.0

[1]  Initial version

### Version 1.1.0

[1]  Improved the detection of size and formats

[2]  Can now select a preferred format

[3]  Improved the fallback to a lower size if the selected size is not available.

[4]  If the preferred format is not available an available format will be used. 

### Version 1.1.4

[1]  Improved the ability to handle multiple clients

[2]  Added option -framerate (defaults to 24)

[3]  Added some error checking for empty frames.

### Version 2.0.0

[1]  Added support for Raspberry Pi Bullseye / Libcamera libraries See notes below.

[2]  Added three new options specific to support libcamera -pires, -pistream and -debug

[3]  Added support for additional resolutions and formats (depends on camera)


## General Description

The main capabilities include:
1.  Automatically scans for available cameras and determines the resolutions it / they support.
2.  Supports USB cameras (most should work).
3.  Supports integrated Pi Camera and likely other integrated cameras (e.g. from a laptop).
4.  Is light in its use of system resources
5.  Allows camera selection if more than one camera is available.
6.  Allows video size selections.
7.  Allows video rotation.
8.  Allows video format selection

## Requirements 

* Python3 (should be accessible without specifying the path)
* Linux OS,  Windows 10, Windows Subsystem Linux (WSL) tested
* Certain python libraries.  The program will complain if they are missing. **In particular OpenCV needs to be V3.4 or later.**

*** Note ***
- testing is usually done on a Raspberry Pi 3B+ and on Win 11.
- videostream supports two methods for connecting to cameras: opencv and libcamera.
- the opencv method supports USB cameras on most platforms and in certain cases Raspberry Pi embedded cameras.
- the libcamera method only supports Raspberry Pi embedded cameras.

The option -pires selects the method.
- If -pires is not specified, opencv method is used.
- If -pires is specified libcamera method is used

- If using a Raspberry Pi - see these notes
https://github.com/stuartofmt/videostream/blob/master/videostream%20on%20Raspberry.md


---

### Installing python libraries

Usually, python libraries can be installed using the following command (other forms of the command can also be used):

```
python3 -m pip install [library name]
```

One of the needed libraries is OpenCV **V3.4 or later**.  This library exists in several forms and can be confusing to install.  The following form is recomended for most computers except the Raspberry Pi: 
```
python3 -m pip install opencv-contrib-python
```
Due to dependencies not included in some OS versions on the Raspberry Pi - the simple command above can fail. Below is a sequence of commands that should work (Verified on Pi 3b+ with Debian Buster).
They are taken from this article:  https://pyshine.com/How-to-install-OpenCV-in-Rasspberry-Pi/

 **THIS DID NOT WORK ON DEBIAN BULLSEYE - For bullseye, follow the instructions here https://singleboardbytes.com/647/install-opencv-raspberry-pi-4.htm and create a virtual environment. The location of python3 for the virtual environment is now /{path to virtual environemnt}/bin/python3 so systemctl unit files or command line invocation will need to change**

```
sudo apt-get install libhdf5-dev libhdf5-serial-dev

sudo apt-get install python3-h5py

sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5

sudo apt-get install libatlas-base-dev

sudo apt-get install libjasper-dev

sudo apt-get install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test

sudo pip3 install opencv-contrib-python==3.4.4.19
```


## Installation

For Linux:<br>

cd to a directory of your choice.  It is usually simpler if your chosen directory is only used for videostream.

```
wget https://github.com/stuartofmt/videostream/raw/master/videostream.py

chmod 744 videostream.py
```


For windows<br>
Follow the instructions from one of the web sources to install python3 - for example:<br>
https://docs.python.org/3/using/windows.html 

Take note of editing the path variable(s) so that python3 and its libraries / modules can be found during execution.


## Starting
Once installation is complete - you will normally start videostream in one of the following ways.

videostream requires a port number using the -port option  This is mandatory.<br>
Other options for startup are described in the ##Startup Options## section below.

videostream can be started from the command line or, more usually using systemctl (not available on Win10 or WSL) or equivalent
.<br>
It is usually run in the background.<br>
A sample service file for use with systemctl is included  here:<br>
https://github.com/stuartofmt/videostream/blob/master/videostream.service
<br>Instructions for using are here:<br>
https://github.com/stuartofmt/videostream/blob/master/system-unit-file.md


Example command line for running videostream in the background (linux)
```
python3 ./videostream.py -port 8090 &
```
or if you plan to close the command console - use nohup

```
nohup python3 ./videostream.py -port 8090 &
```

On Windows things are slightly different - note the use of pythonw
which will run python in the background (tested with python 3.9)

Note the use of pythonw and the output files to check if everything was successful

```
pythonw videostream.py -port 8090 > videostream.log 2>&1

```

If the program is run in foreground it can be shutdown using CTRL+C (on linux) or CTRL+Break (on Windows).<br>
If the program is run in background it can be stopped using http with /terminate (see the section on **Usage** below).<br>

**Note that the http listener will stop responding if videostream is run from a command console that is then closed.
This will happen even if started in background.<br>
To avoid this - use nohup (linux) or start with pythonw (on Windows)<br>
An alternative if you are on Win10 is to use  Windows Subsystem for Linux (WSL) and run videostream as a linux application inside WSL.<br>**

### Usage

**Accessing the video stream**

The video is accessed using a http link (e.g. using a browser).
The url is of the form:
```
http://<ipaddress>:<port>/stream]
```
---

**Terminating the program**

The program can be terminated using:

```
http://<ipaddress>:<port>/terminate]
```
---
### Startup Options
From the directory where videostream.py is installed:<br>

Options can be viewed with
```
python3 ./videostream.py -h  # For Linux

python3 videostream.py -h  # For Windows
```

The response will give the version number at the top.

----

videostream supports startup options in the form:

python3 ./videostream.py -port [-camera] [-rotate] [-size] [-format][-host][-framerate]

Each option is preceded by a dash - without any space between the dash and the option. Some options have parameters described in the square brackets.   The square brackets are NOT used in entering the options. If an option is not specified, the default used.
Not all options are applicable to both the opencv and libcamera methods.  Those which are not are marked.

#### -port [port number]
**Mandatory - This is a required option.** <br>
If the selected port is already in use the program will not start

Example
```
-port 8090      #Causes internal http listener to start and listen on port 8090<br>
```

#### -camera [number]
For opencv - may be omitted if there is only one camera available.
For libcamera - may be omitted for -camera 0
If there is more than one camera then the camera number needs to be specified.
**Note that camera numbers begin at 0 (zero) for the first camera.**

Example
```
-camera 2      #Causes the program to use the third camera it detects
```  

#### -rotate [number]
Defaults to 0 (zero).
If the video from the camera does not have the right orientation the video can be rotated with this option.
Allowed settings are 0, 90, 180, 270

Example
```
-rotate 180      #Causes the program to rotate the video 180 deg
```

#### -size [number] (opencv only)
If omitted - the program will try to determine the highest resolution your camera supports.<br>
The available resolutions are from the list below.

If you specify the -size (with a number from 0 to 6) - the program will try to use the corresponding resolution.<br>
If your camera does not support that resolution, the program will set the next lowest resolution that your camera does support.

**Note: Some cameras may report that it supports a resolution when, in fact, it does not.**  In such cases, try other settings.

**List of supported resolutions:**

0 -->    3280 x 2464

1 -->    2048 x 1080

2 -->    1920 x 1800

3 -->    1640 x 1232

4 -->    1280 x  720

5 -->     800 x  600

6 -->     720 x  480

7 -->     640 x  480

8 -->     320 x  240

Example
```
-size 6      #Causes the program to try to use a resolution of 720 x 480
```

#### -format [option] (opencv only)
If omitted - the program will try to use MJPG.<br>
The available formats are from the list below.
**Note that these are the formats from the camera.  The program streams jpeg images**


BGR3, YUY2, MJPG, JPEG

If you specify the -format  - the program will try to use that format.<br>
If your camera does not support that format, the program will select one of the available formats that are supported.

**Note: Some cameras may report that it supports a format when, in fact, it does not.**  In such cases, try other settings.

Example
```
-format BGR3      #Causes the program to try to use the BGR3 format
```

#### -host [ip address]
If omitted the default is 0.0.0.0<br>
Generally this can be left out (default) as it will allow connection to the http listener from localhost:<port> (locally) or from another machine with network access using <actual-ip-address-of-server-running-DuetLapse3><port>.

Example
```
-host 192.168.86.10      #Causes internal http listener (if active) to listen at ip address 192.168.86.10<br>
```

#### -framerate [number]
If omitted the default is 24<br>
Generally this can be left out (default).

Example
```
-framerate 30      #  Streams at 30 fps<br>
```

#### -pires [string] (libcamera only)
If used - invokes the libcamera method.
Specifies libcamera options.  Usually --width --height and possibly --mode will be the minimum required.  Other options may also be used.
It is highly recommended to determine an appropriate set by testing using these notes. What is and is not supported can vary by camera type.
Note the use of double quotes.

Example
```
-pires host 192.168.86.10      #Causes internal http listener (if active) to listen at ip address 192.168.86.10<br>
```

#### -pistream [string] (libcamera only)
If omitted the default is tcp://0.0.0.0:5000
Generally this can be left out (default).

Example
```
-pistream "tcp://0.0.0.0:5050  #streams the camera on internal tcp port 5050
```

#### -debug (libcamera only)
If omitted the default is False which restricts debug messages from libcamera.

Example
```
-debug      #Outputs debug messages
```

### Examples of use

**opencv method**

Start videostream.py and have it stream video on port 8081 rotated 180 deg using the only (default) camera at a resolution of 800x600

```
python3 ./videostream.py -port 8082 -rotate 180 -size 5
```
Same as above but without debug information

```
python3 ./videostream.py -port 8082 -rotate 180 -size 5 2>/dev/null
```

**libcamera method**

Start videostream.py and have it stream video on port 8081 rotated 180 deg using camera 0 at a resolution of 800x600

```
python3 ./videostream.py -port 8082 -camera 0 -rotate 180 -pires -pires "--width 800 --height 600"`
```
Same as above without debug information

```
python3 ./videostream.py -port 8082 -camera 0 -rotate 180 -debug  -pires "--width 800 --height 600"`
```

  ### Error Messages
  
At startup console messages are printed to confirm correct operation.

There may be some error messages that look like this:
VIDEOIO ERROR: V4L: can't open camera by index 1
These can be safely ignored as they are an artifact of one of the underlying libraries.

Some errors in operation can be related to available memory and buffer sizes (e.g. Empty Frame Detected).  These can often be fixed by reducing the resolution of images (i.e. using the -size option) or reducing the frame rate (i.e. using the -framerate option).
  
