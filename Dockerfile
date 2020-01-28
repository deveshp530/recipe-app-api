FROM python:3.9.0a2-alpine3.10
MAINTAINER Devesh Patel

ENV PYTHONUNBUFFERED 1

# copy requirements file in recipe folder to docker image '/requirements.txt'
COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

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
