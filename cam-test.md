# cam-test

This is a simple test program to determine what cameras are available, what common resolutions and formats are supported and to display the output.

It has been tested on linux but not windows but should work if the version of opencv supports cv2.imshow.

## Installation


cd to a directory of your choice.

```
wget https://github.com/stuartofmt/videostream/raw/master/cam-test.py

chmod 744 cam-test.py
```

This program uses opencv which can create a lot of "noisy" output.  It is usually going to be more convenient to run it using the following form (i.e. with 2>/dev/null):

```
python3 ./cam-test.py 2>/dev/null
```

If this is being run on a Raspberry Pi with Bullseye.  Use the following form:

```
libcamerify python3 ./cam-test.py 2>/dev/null
```