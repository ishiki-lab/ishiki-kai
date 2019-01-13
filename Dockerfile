# lushroom-display Dockerfile

# in order to run this, a bind mount to the /media/usb directory must be created
# so that the display program can access the logo and background images
# docker run -it --name lushroom-display -v /media/usb:/media/usb lushdigital/lushroom-display:latest

FROM lushdigital/lushroom-base:latest

RUN [ "cross-build-start" ]

# copy files to container
COPY requirements.txt requirements.txt
COPY display_status.py display_status.py

# install dependencies
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# run the display command
CMD ["python3", "display_status.py"]

RUN [ "cross-build-end" ]

