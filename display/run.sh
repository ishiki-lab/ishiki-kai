# lushroom-rclone Dockerfile

# in order to run this, a bind mount to the /media/usb directory must be created
# so that the display program can access the logo and background images
# docker run -it --name lushroom-display -v /media/usb:/media/usb lushdigital/lushroom-display:latest
# the container must also be run in privileged mode and the framebuffer and touchscreen devices must be bind-mounted

#docker run -it --rm --name lushroom-display -v /media/usb:/media/usb lushdigital/lushroom-display:latest
docker run --privileged -it --rm --name lushroom-display --network host \
    -v /media/usb:/media/usb \
    -v /dev/fb0:/dev/fb0 \
    -v /dev/input/event0:/dev/input/event0 \
    -e HOSTNAME=$HOSTNAME \
    -e SENTRY_URL=https://47ba8b60e8994fd1a5979cad36185cad@sentry.io/1391137 \
    lushdigital/lushroom-display:latest
