# lrpi_record

## lrpi_vezer2srt.py Usage

### On a Mac

To use this script from the command line, you _must_ run the command from the directory. Otherwise the `.srt`s generate will appear in unexpected places...

- open a Finder window
- navigate to your lrpi_record installation directory (where lrpi_vezer2srt.py is)
- (if they don't already exist!)
    - make an xml directory
    - put your xml files into the directory
- open a terminal window
- `cd` into the installation directory ('cd' stands for 'change directory')
    - type `cd ` (plus a space!)
    - click and drag the folder icon of the installation directory from finder into the terminal
    - hit enter 
- In the terminal, run `./lrpi_vezer2srt.py -x <name of file>.xml` -> the full stop and forward slash are important!
    - type `./lrpi_vezer2srt.py -x ` (plus a space!)
    - From Finder, click and drag the file from the xml/ directory into the terminal
    - hit enter
- The script will start running, there will be lots of 'd's
- the output `.srt`s should appear in the same directory as the script
- file your srts accordingly
- upload them to google drive! 

## Installation

### Python 3

Python 3 is required to run lrpi_dmxrecord and lrpi_play.

A simple way to install Python 3 is to install the [Miniconda Python distribution version 3.7](https://conda.io/miniconda.html).

### Install git and get the source code

If you don't have it already, [download and install git](https://git-scm.com/downloads) for your operating system.

Then clone the lrpi_record repository.

```
git clone https://github.com/LUSHDigital/lrpi_record.git
```


### Tinkerforge brick daemon

Install brick daemon and optionally brick viewer from [https://www.tinkerforge.com/en/doc/Downloads.html](https://www.tinkerforge.com/en/doc/Downloads.html)

### Python pre-requisites

```
cd lrpi_record
curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
sudo python get-pip.py
sudo pip3 install -r requirements.txt
```

### Record DMX stream

TODO

### Edit .srt files

TODO

#### Sound and light format\

TODO

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

TODO

When playing, it is possible to pause and resume the sound and light stream, however on MacOS X it is necessary to either:

1. Run the process as root.
2. Get the Terminal application white listed under Enable access for assistive devices.

This is because recent versions of Mac OSX restrict monitoring of the keyboard for security reasons. For that reason, one of the following must be true:
