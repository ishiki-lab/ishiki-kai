#!/bin/sh

sleep 2
export GOOGLE_APPLICATION_CREDENTIALS=/media/usb/lushroom-rclone.json
echo "bootstrap starting"
python3 -u /opt/lushroom/bootstrap.py

if [ -f /opt/lushroom/resize_once.txt ]; then
    echo "resizing and rebooting"
    rm /opt/lushroom/resize_once.txt
    raspi-config --expand-rootfs
    reboot now
    exit 0
fi

systemctl stop dhcpcd

if [ -f /media/usb/docker-compose.yaml ]; then
    echo "docker compose up"
    docker-compose -f /media/usb/docker-compose.yaml pull
    docker-compose -f /media/usb/docker-compose.yaml up --force-recreate -d
fi

sleep 5
systemctl start dhcpcd

echo "monitoring usb"
python3 /opt/lushroom/monitor.py
exit 0