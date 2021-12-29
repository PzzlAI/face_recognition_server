FROM python:3.8

RUN apt-get update
RUN apt-get -y install libgl1

ADD . /app

WORKDIR /app

RUN mkdir tmp

RUN pip install -r requirements.txt