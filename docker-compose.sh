#!/bin/bash

docker rm -f `docker ps -aq -f name=SNResistance*`

set -a
source .environment

cat .compose.yml | envsubst | docker-compose -f - up -d
