FROM lushdigital/lushroom-base:latest
RUN mkdir /opt/code 
COPY . /opt/code
RUN pip3 install flask
RUN pip3 install -r /opt/code/requirements.txt