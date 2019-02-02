#!/bin/sh

sleep 2
echo "bootstrap starting"
python3 /opt/lushroom/bootstrap.py

if [ -f /media/usb/docker-compose.yaml ]; then
    echo "docker compose up"
    docker-compose -f /media/usb/docker-compose.yaml pull
    docker-compose -f /media/usb/docker-compose.yaml up --force-recreate
fi

echo "monitoring usb"
python3 /opt/lushroom/monitor.py
exit 0