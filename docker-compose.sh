#!/bin/bash

docker rm -f `docker ps -aq -f name=SNResistance*`

source .environment; rm -rf docker-compose.yml; envsubst < ".compose.yml" > "docker-compose.yml"
docker-compose up -d