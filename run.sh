# Run bash with only the usb stick mounted
docker run -it --rm -p 80:80 -v /media/usb:/media/usb --entrypoint "/bin/bash" flask  