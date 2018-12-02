sudo docker build -t lushroom-rclone .
sudo docker images
sudo docker tag lushroom-rclone arupiot/lushroom-rclone:latest
sudo docker push arupiot/lushroom-rclone
