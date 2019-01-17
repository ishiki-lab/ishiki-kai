# sample build command: sudo docker build -t lrpi_player .
# running resin.io rpi image on ubuntu with qemu
# (but) resin images have qemu built in anyway...
# sudo docker run -v /usr/bin/qemu-arm-static:/usr/bin/qemu-arm-static --rm -ti resin/rpi-raspbian
# Sample run command with kernel/usb stick links
# docker run -it --rm -v /opt/vc:/opt/vc -v /media/usb:/media/usb --device /dev/vchiq:/dev/vchiq --device /dev/fb0:/dev/fb0 lrpi_player

# get base image (based itself on a resin image). Has QEMU built in
FROM lushdigital/lushroom-base:latest

RUN [ "cross-build-start" ] 

# make dirs

RUN mkdir /opt/code
RUN mkdir -p /media/usb

# copy lrpi_player repo

RUN git clone --single-branch -b lplay-2 --depth 5 https://github.com/LUSHDigital/lrpi_player.git /opt/code && \
    pip3 install -r /opt/code/requirements.txt

# serve Flask from 80
WORKDIR /opt/code/flask

ENTRYPOINT ["python3"]
CMD ["Server.py"]

EXPOSE 80

RUN [ "cross-build-end" ]