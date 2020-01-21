# lushroom-scentroom Dockerfile
if [ $# -eq 0 ]; then
    echo "Please specific build tag as your first argument"
    echo "e.g. ./build.sh latest"
    echo "e.g. ./build.sh staging"
    exit 1
fi

sudo docker build -t lushroom-scentroom . && \
sudo docker images && \
sudo docker tag lushroom-scentroom lushdigital/lushroom-scentroom:"$1" && \
sudo docker push lushdigital/lushroom-scentroom:"$1"

