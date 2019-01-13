# lushroom-rclone Dockerfile

# in order to run this, a bind mount to the /media/usb directory must be created
# so that the rclone config and service account files are visible to this
# docker container - see example below

docker run -it --name lushroom-rclone -v /media/usb:/media/usb lushdigital/lushroom-rclone:latest
