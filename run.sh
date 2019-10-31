PORT=5000

docker run -it --rm -p $PORT:$PORT -v "$(pwd)"/flask:/opt/code/flask:ro -v /media/usb:/media/usb --entrypoint "/bin/bash" --env PLAYER_PORT=8080 \
--network host  \
lushdigital/lushroom-scentroom:staging  