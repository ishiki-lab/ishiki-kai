#!/bin/sh

sleep 2
echo "start.sh running bootstrap"
python3 /opt/lushroom/monitor.py
# docker-compose -f /media/usb/docker-compose.yaml pull
# docker-compose -f /media/usb/docker-compose.yaml up --force-recreate
exit 0