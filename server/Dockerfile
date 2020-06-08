FROM python:3.8-alpine

RUN apk update && apk add build-base python3-dev py-pip jpeg-dev zlib-dev openssl-dev gcc libffi-dev postgresql-dev
ENV LIBRARY_PATH=/lib:/usr/lib

WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /usr/src/app

RUN python ./backend/manage.py collectstatic --noinput