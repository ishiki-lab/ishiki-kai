#!/bin/sh
flash --hostname lushroom \
      --userdata lr-user-data.yaml \
      --bootconf lr_config.txt \
      hypriotos-rpi-v1.9.0.img
