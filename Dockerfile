FROM python:3.7.2-stretch
LABEL maintainer "ricardobchaves6@gmail.com"

WORKDIR /api

COPY . /api

RUN pip install --upgrade pip && \
    pip install -r requirements.txt
