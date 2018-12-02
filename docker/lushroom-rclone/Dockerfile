# lushroom-rclone Dockerfile
# in order to run this, a bind mount to the /media/usb directory must be created
# so that the rclone config and service account files are visible to this
# docker container - see example below
# docker run -it --name lushroom-rclone -v /media/usb:/media/usb arupiot/lushroom-rclone:latest

FROM arupiot/lushroom-base:latest

RUN [ "cross-build-start" ]

# install dependencies
RUN apt-get update && apt-get -y install cron p7zip-full unzip

# install rclone
RUN mkdir -p /opt/rclone
WORKDIR /opt/rclone
RUN cd /opt/rclone ; wget --no-check-certificate https://raw.github.com/pageauc/rclone4pi/master/rclone-install.sh
RUN cd /opt/rclone ; chmod +x ./rclone-install.sh ; ./rclone-install.sh
RUN rclone --version

# add the rclone command crontab file in the cron directory
ADD rclone-cron /etc/cron.d/rclone-cron

# give execution rights to the crontab file
RUN chmod 0644 /etc/cron.d/rclone-cron

# apply the cron job
RUN crontab /etc/cron.d/rclone-cron

# create the log file
RUN touch /var/log/cron.log

# run an initial rclone update
RUN mkdir -p /opt/rclone/tracks
RUN rclone -vv --config /media/usb/rclone_lushrooms.conf sync /media/usb/tracks lushrooms:Tracks

# run the cron command
CMD cron && tail -f /var/log/cron.log

RUN [ "cross-build-end" ]
