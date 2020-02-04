FROM python:3.9.0a2-alpine3.10
MAINTAINER Devesh Patel

ENV PYTHONUNBUFFERED 1

# copy requirements file in recipe folder to docker image '/requirements.txt'
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps gcc libc-dev linux-headers postgresql-dev

RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

# creates empty folder called app
RUN mkdir /app
# switches to default directory
WORKDIR /app
# copies app folder from local machine to app folder to docker image
COPY ./app /app

# creates user -D used for running applications
RUN adduser -D user
# switches docker to user we created
USER user
