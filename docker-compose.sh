#!/bin/bash

source .configuration; rm -rf docker-compose.yml; envsubst < ".compose.yml" > "docker-compose.yml"
docker rm -f $(docker ps -q -f name=SNResistance); docker-compose up -d