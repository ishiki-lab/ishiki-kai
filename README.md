# Lushroom bootstrap

This directory includes all the files to be used to bootstrap the installation of the Raspberry Pi SD card image 
for the Lushroom cloud connected sound and light player.

## Raspian Base Image

* Get the [latest raspian image](https://downloads.raspberrypi.org/raspbian_lite_latest)
* Get [Etcher](https://www.balena.io/etcher/) to burn it with
* Burn image to mini SD card for use in Pi

## Configure Pi for ssh access

Set up the Raspberry Pi before prepping the card can be done with raspi-config
Login to Raspberry Pi as "pi" with password "raspberry" then:

* "sudo raspi-config"
* Network Options > Wi-fi <enter country, SSID & passphrase>
* Interfacing Options > SSH > Yes
* Finish
* use ifconfig to check the ip address once connected
* "sudo reboot now"

## Prepare image with Fabric

* Create python 2.7 virtualenv
* Install requirements.txt
* Copy `certs` folder from secrets and place next to the root of this repo
* Duplicate `config_local_template.py` as a new file called `config_local.py` and update it with the ip-address of the Pi and user info
* Run fab `prepare_card` to create basic image. You will be asked for the password to set for the new user `lush`
* If you plan to copy and distribute this image log in and remove your wifi credentials from `/etc/wpa_supplicant/wpa_supplicant.conf`
