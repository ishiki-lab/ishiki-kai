FROM resin/rpi-raspbian:stretch

ENTRYPOINT []

RUN [ "cross-build-start" ]

RUN apt-get update && apt-get upgrade

RUN apt-get install -y --no-install-recommends \
  build-essential gcc make git apt-utils wget ntp ifmetric man

RUN apt-get install -y libfreetype6 dbus dbus-*dev libsmbclient libssh-4 \
  libpcre3 fonts-freefont-ttf \

RUN apt-get -y install fbset omxplayer \
    python3-dev python3-pip python-imaging python-numpy

RUN apt-get clean

RUN pip3 install rpi.gpio
RUN pip3 install pycrypto
RUN pip3 install requests
RUN pip3 install tinkerforge
RUN pip3 install pillow
RUN pip3 install rdflib
RUN pip3 install influxdb
RUN pip3 install colour

RUN [ "cross-build-end" ]


# build command: sudo docker build -t lushroom-base .
# get resin.io stretch raspbian image. Has QEMU built in
# lrpi_base Dockerfile
# Resin.io (balena) base image
# python3-dev
# python3-pip
# dbus dev libraries
# ifmetric
# ntp
# tinkerforge
