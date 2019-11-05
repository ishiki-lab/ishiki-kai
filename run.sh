PORT=80
PLAYER_PORT=8080

sudo docker run -it --rm --network host -p $PORT:$PORT \
-v /media/usb:/media/usb \
--env PLAYER_PORT=$PLAYER_PORT \
--env PORT=$PORT \
--entrypoint /usr/bin/python3 lushdigital/lushroom-scentroom:staging  FlaskFileUploader.py