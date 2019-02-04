# Lushroom bootstrap

This directory includes all the files to be used to bootstrap the installation of the Raspberry Pi SD card image 
for the Lushroom cloud connected sound and light player.

## Install using prepared image

### Get and burn OS image

* Get the latest image from lush_sd_images in the secrets folder
* Get [Etcher](https://www.balena.io/etcher/) to burn it with
* Burn image to a mini SD card for use in Pi

### Get settings and prepare USB

* Work out the number of the Lushroom you want to prepare
* Equip yourself with a USB flash drive
* Get the correct settings file from `usbstick_settings`  in the secrets folder and copy onto the usb drive.
* Add `Images` `tracks` `lushroom-rclone.json` to the usb too
* Add the `docker-compose.yaml` (yaml NOT yml) to the USB too

### Boot it up

* Put the sd card in the pi
* Plug the USB drive into the pi
* Turn pi on
* Wait
* You might need to restart it the first time if it doesn't find the wifi


## Create a Fresh Raspian Base Image

### Get and burn OS image

* Get the [latest raspian image](https://downloads.raspberrypi.org/raspbian_lite_latest)
* Get [Etcher](https://www.balena.io/etcher/) to burn it with
* Burn image to mini SD card for use in Pi

### Configure Pi for wifi/ssh access

Raspian has some built in magic to help configure sd cards directly.
Mount the flashed SD card on your PC and add two files to the boot folder

* An empty file called `ssh`, this will turn on sshd
* Copy the `wpa_supplicant.conf` file from the `boot` folder of this repo and update it with the ssis and psk of your local wifi.
* Determine the ip address of the pi, either by booting with a screen attatched,
working on a network where the host broadcast works or other devious means.


### Install stuff with Fabric script

* Clone this repo locally
* Create python 2.7 virtualenv
* Install requirements.txt
* Copy `config_local.py` from secrets into the root of the repo
* Edit your new local `config_local.py` to add the ip address of the pi
* Copy the whole folder `lrpi_access_keys` in secrets next to the root of this repo
* Run fab `prepare_card_1`. You will be asked for the password to set for the new user `lush`,
this should be set to the value from the secrets `config_local.py`.
You will aslo be asked for a `Y` by the screen drivers. It will reboot on its own.
* Wait for pi to reboot and settle down
* Run fab `prepare_card_2`. You might be asked for a `y`
* Wait for pi to finish installing things and shut itself down
* Remove the sd card from pi and take a copy of the image with `dd` something,
 like `sudo dd if=/dev/rdisk2 of=/Users/paul/Documents/lush_prod.img bs=1m` but with a path on your machine
