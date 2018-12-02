FROM arupiot/lushroom-base:latest

RUN mkdir -p /opt/lushroom
RUN cd /opt/lushroom && git clone https://github.com/arupiot/deskcontrol.git
RUN pip install -r /opt/lushroom/deskcontrol/requirements.txt
ADD config_local.py /opt/lushroom/deskcontrol/deskcontrol

WORKDIR /opt/lushroom

CMD ["python", "-u", "deskcontrol/deskcontrol/controller.py"]
