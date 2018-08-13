#!/bin/bash

source .configuration; rm -rf docker-compose.yml; envsubst < ".compose.yml" > "docker-compose.yml"
sudo docker rm -f $(sudo docker ps -q -f name=SNResistance); docker-compose up -d