FROM python:3.7.0-alpine



MAINTAINER Yaroslav <hello@unimarijo.me>

ADD . SNResistance/
WORKDIR SNResistance
ENV PYTHONPATH "$PYTHONPATH:$(pwd)"

RUN apk add --update build-base
RUN pip install virtualenv --no-cache-dir && virtualenv venv -p $(which python3)
RUN venv/bin/python -m pip install -r requirements/requirements.txt

ENTRYPOINT venv/bin/python run.py
