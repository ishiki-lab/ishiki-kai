# lushroom-display Dockerfile

# in order to run this, a bind mount to the /media/usb directory must be created
# so that the display program can access the logo and background images
# docker run -it --name lushroom-display -v /media/usb:/media/usb lushdigital/lushroom-display:latest

FROM lushdigital/lushroom-base:latest

RUN [ "cross-build-start" ]

#RUN apt-get install -y python3-pygame
RUN apt-get install -y libasyncns0 libcaca0 libflac8 libfluidsynth1 libglib2.0-0 libice6 \
  libjack-jackd2-0 libmad0 libmikmod3 libopenal-data libopenal1 libpng12-0 \
  libportmidi0 libpulse0 libsamplerate0 libsdl-image1.2 libsdl-mixer1.2 \
  libsdl-ttf2.0-0 libsdl1.2debian libslang2 libsm6 libsndfile1 libsndio6.1 \
  libwrap0 libx11-xcb1 libxi6 libxtst6 x11-common

# copy files to container
COPY requirements.txt requirements.txt
COPY display_status.py display_status.py

# install dependencies
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# run the display command
CMD ["python3", "display_status.py"]

RUN [ "cross-build-end" ]

