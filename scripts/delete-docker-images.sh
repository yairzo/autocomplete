#!/bin/bash

#Remove docker images

sudo docker ps -a | grep autocomplete_elasticsearch | docker rm -f `awk '{print $1}'`

sudo docker images | grep autocomplete_elasticsearch | docker rmi -f `awk '{print $3}'`

sudo docker ps -a | grep api-service | docker rm -f `awk '{print $1}'`

sudo docker images | grep api-service | docker rmi -f `awk '{print $3}'`



