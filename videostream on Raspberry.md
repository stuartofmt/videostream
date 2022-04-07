### videostream on raspberry Pi

- As of the start of 2022 - Raspberry Pi's "go forward" release is based on Debian Bullseye.  This includes a new set of libraries (libcamera) for embedded cameras.
- opencv is a general purpose set of libraries used with python for connecting to and managing cameras.
- opencv supported previous releases of Raspberry Pi (buster and earlier).
- libcamera is being actively developed and is not yet fully supported by opencv.

For these reasons - videostream supports two methods - one using opencv the other using libcamera.

**Before trying videostream it is HIGHLY recommended consulting these notes and performing the Resolution Testing.**

https://github.com/stuartofmt/Pi-Notes


### Selecting method
The methods are automatically selected based on the options used to start videostream.

The option -pires selects the method.
- If -pires is not specified, opencv method is used.
- If -pires is specified libcamera method is used

The general guidance on which method to use described below.
    
#### Raspberry Pi on Buster and Earlier
Use the opencv method.
For example:

```
python3 ./videostream.py -port 8082 -rotate 180 -size 5 2>/dev/null
```

#### Raspberry Pi on Bullseye and later

The libcamera method is recommended (invoked because of the use of -pires)

For example:
```
python3 ./videostream.py -port 8082 -camera 0 -rotate 180 -debug  -pires "--width 800 --height 600"`
```

It is POSSIBLE to use the opencv method but results are currently (early 2022) quite variable.  To use the opencv method requires invoking python and videostream using the libcamerify command.

For example:

```
libcamerify python3 ./videostream.py -port 8082 -camera 0 -rotate 180 -debug  -pires "--width 800 --height 600"`
```
