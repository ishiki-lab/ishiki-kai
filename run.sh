# lushroom-rclone Dockerfile

# in order to run this, a bind mount to the /media/usb directory must be created
# so that the display program can access the logo and background images
# docker run -it --name lushroom-display -v /media/usb:/media/usb lushdigital/lushroom-display:latest

docker run -it --rm --name lushroom-display -v /media/usb:/media/usb lushdigital/lushroom-display:latest
