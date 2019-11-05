# lushroom-scentroom Dockerfile
BUILD_NAME=build-1

sudo docker build -t lushroom-scentroom . && \
sudo docker images && \
sudo docker tag lushroom-scentroom lushdigital/lushroom-scentroom:$BUILD_NAME && \
sudo docker push lushdigital/lushroom-scentroom:$BUILD_NAME