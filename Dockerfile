FROM lushdigital/lushroom-base:latest
RUN mkdir /opt/code 
COPY requirements.txt /opt/code
RUN pip install flask
RUN pip install -r /opt/code/requirements.txt