# lrpi_record

## Installation

### Python 3

Python 3 is required to run lrpi_dmxrecord and lrpi_play.

A simple way to install Python 3 is to install the [Miniconda Python distribution version 3.7](https://conda.io/miniconda.html).

### Tinkerforge brick daemon

Install brick daemon and optionally brick viewer from [https://www.tinkerforge.com/en/doc/Downloads.html](https://www.tinkerforge.com/en/doc/Downloads.html)

### Python pre-requisites

```
$ curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
$ sudo python get-pip.py
$ sudo pip3 install -r requirements.txt
```

### Record DMX stream


### Edit .srt files


#### Sound and light format\

```
HUE#(hue,sat,bri,transitiontime)
```

where:

1. *#* is the number of the Philips Hue lamp
2. *hue* is a number between 0 and 65535. Programming 0 and 65535 would mean that the light will resemble the color red, 21845 for green and 43690 for blue.
3. *sat* is a number between 0 (white light) and 255 (saturated colour)
4. *bri* The brightness value to set the light to. Brightness is a scale from 1 (the minimum the light is capable of) to 254 (the maximum). Note: a brightness of 1 is not off.
5. *transitiontime* is the duration of the transition from the light’s current state to the new state. This is given as a multiple of 100ms and defaults to 4 (400ms). For example, setting transitiontime:10 will make the transition last 1 second.



### Play sound and light

When playing, it is possible to pause and resume the sound and light stream, however on MacOS X it is necessary to either:

1. Run the process as root.
2. Get the Terminal application white listed under Enable access for assistive devices.

This is because recent versions of Mac OSX restrict monitoring of the keyboard for security reasons. For that reason, one of the following must be true:
