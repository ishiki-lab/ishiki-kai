# sample build command: sudo docker build -t mw_rclone .
# sample run command: sudo docker run -d -p 80:80 arupiot/media_warrior_base:develop
# running resin.io rpi image on ubuntu with qemu
# (but) resin images have qemu built in anyway...
# sudo docker run -v /usr/bin/qemu-arm-static:/usr/bin/qemu-arm-static --rm -ti resin/rpi-raspbian

# get media warrior rpi image. (QEMU/Python/dbus/etc)
FROM lrpi_rpi_base:local

RUN mkdir -p /media/usb/tracks

RUN [ "cross-build-start" ]
# ADD media-warrior-07dec249ae7a.json /opt/GCP
# ADD rclone1.43.1_expect.sh /
# install everything needed to set up the 'Pi as a hotspot
# install expect/rclone
# get gdrive service account details from usb stick
# set up gdrive remote
# creates a remote called arupiot-expect
# && \ /opt/media_warrior/mw_serve/docker/rclone/rclone_expect.sh
# sync with gdrive
# sample mlp are in mlp_samples_test
# RUN rclone lsf arupiot-expect:mlp_samples_test
# Sync songs from the gdrive

WORKDIR /opt/media_warrior/mw_rclone
RUN mkdir -p /media/usb/rclone
COPY rclone.conf /root/.rclone.conf
COPY lush-rooms-stage-global-f0347a1c7551.json /media/usb/lush-rooms-stage-global-f0347a1c7551.json

RUN apt-get install man && \
    apt-get install p7zip-full

RUN curl -L https://rclone.org/install.sh | bash && \
    rclone --version

RUN rclone sync lush-gsuite-drive:Tracks/00_Test/ /media/usb/tracks -v -P

# TODO:
# set up rclone cron job
# set up rclone chronjob (updated every evening?)


RUN [ "cross-build-end" ]