FROM python:3
RUN mkdir /code 
COPY requirements.txt /code
RUN pip install flask
RUN pip install -r /code/requirements.txt