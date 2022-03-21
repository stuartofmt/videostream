**There are several issues with Debian Bullsey on Raspberry Pi WITH THE PI CAMERA**

**As of mid Jan 2022 - I have not got a satisfactory working system.**

**Notes on Debian Bulleye with Raspberry Pi 3B+ and Pi V2 Camera**

The following are notes are NOT a recipe for success!!!  They are simply an outline of the latest "almost there" steps.


Debian Bullseye uses a new and different set of drivers for the Raspberry Pi cameras.
USB cameras do not seem to be affected

Release 1.1.4 of videostream does not fully support Raspberry Pi cameras.

There are two issues:

(1) Raspberry Pi recognizing the camera

(2) A change to the way camera cababilities are reported and handled by the opencv library used by videostream.

**Issue 1**

Apparently - The Rapberry Pi cameras work correctly on the Pi4 but may not work on earlier versions.

To get the pi camera to work requires:

(1) changes to the file /boot/cmdline.txt

(2) enable Glamor

This is the relevent section of /boot/cmdline.txt for a raspberry pi 3B+ using the V2 pi camera.

Note the dtoverlay= setting depends on the type of pi camera and taken from the table in this post:

https://www.raspberrypi.com/documentation/accessories/camera.html

[all]

dtoverlay=vc4-kms-v3d

dtoverlay=imx219

gpu_mem=128

[pi4]

#dtoverlay=vc4-fkms-v3d


To enable Glamor perform the following steps:

sudo raspi-config

6 Advance Options --> A8 Glamor --> Enable 

then reboot

The Pi camera can then be tested with the command:
libcamera-hello

**Issue 2**

The camera capabilities being reported by opencv (for the Pi camera) do not work as expected.
The display video captured by opencv is not properly rendered.
