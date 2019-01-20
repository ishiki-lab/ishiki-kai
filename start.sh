#!/bin/sh

python /opt/lushroom/wifi.py
docker pull arupiot/lrpi_base:latest
#docker run --privileged -v /etc/opt/lushroom:/etc/opt/lushroom --rm lushroom/lushroom-bootstrap:latest
docker-compose -f /etc/opt/lushroom/docker-compose.yml pull
docker-compose -f /etc/opt/lushroom/docker-compose.yml up -d --force-recreate
