FROM arupiot/lushroom-base:latest

RUN mkdir -p /opt/lushroom

RUN cd /opt/lushroom && git clone https://github.com/LUSHDigital/lrpi_commands.git

RUN pip3 install -r /opt/lushroom/lrpi_commands/requirements.txt

WORKDIR /opt/lushroom

CMD ["python", "-u", "lrpi_commands/main.py"]
