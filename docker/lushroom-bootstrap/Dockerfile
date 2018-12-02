FROM arupiot/lushroom-base:latest

RUN mkdir -p /opt/lushroom
ADD lushroom-bootstrap /opt/lushroom/lushroom-bootstrap

WORKDIR /opt/lushroom

CMD ["python", "lushroom-bootstrap/main.py"]
