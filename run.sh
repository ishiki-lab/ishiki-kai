# Run bash with only the usb stick mounted
docker run -it --rm -p 5000:5000 -v "$(pwd)"/flask:/opt/code/flask:ro -v /media/usb:/media/usb --entrypoint "/bin/bash" lushdigital/lushroom-scentroom:staging  