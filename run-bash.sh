PORT=8080

docker run -it --rm -p $PORT:$PORT \
-v /opt/vc:/opt/vc \
-v /media/usb:/media/usb \
-v /home/lush/devcode/lrpi_player/flask:/opt/code/flask \
--device /dev/vchiq:/dev/vchiq \
--device /dev/fb0:/dev/fb0 \
--entrypoint "/bin/bash" \
--network host \
--env PORT=8080 \
lushdigital/lushroom-player:staging  
