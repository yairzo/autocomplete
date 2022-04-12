# autocomplete

How to run:

scripts/run-local-docker.sh

Notice: 
 
 you might need to change the DOCKER_MACHINE_IP in docker-compose-dev.yml to you local machine ip
 
 you may use postman json in scripts/Autocomplete.postman_collection.json to test the end points


Technology descisions:


Python with Flask as the framework for the api

Docker to be able to use it as a micro-sevice which can autoscale

Elasticsearch for the autocomplete which can also perform in high scales
