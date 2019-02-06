#!/bin/sh

sleep 2
echo "bootstrap starting"
python3 /opt/lushroom/bootstrap.py

if [ -f /opt/lushroom/resize_once.txt ]; then
    echo "resizing and rebooting"
    rm /opt/lushroom/resize_once.txt
    raspi-config --expand-rootfs
    reboot now
    exit 0
fi

if [ -f /media/usb/docker-compose.yaml ]; then
    echo "docker compose up"
    docker-compose -f /media/usb/docker-compose.yaml pull
    docker-compose -f /media/usb/docker-compose.yaml up --force-recreate -d
fi

echo "monitoring usb"
python3 /opt/lushroom/monitor.py
exit 0