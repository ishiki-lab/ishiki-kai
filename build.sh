# lushroom-scentroom Dockerfile
ENV=staging

sudo docker build -t lushdigital/lushroom-scentroom:$ENV .
sudo docker images
sudo docker tag lushdigital/lushroom-scentroom:$ENV lushdigital/lushroom-scentroom:$ENV
sudo docker push lushdigital/lushroom-scentroom:$ENV