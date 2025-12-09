#!/bin/bash
# Script to run tests in the Docker container

# Check if container is running
if [ "$(docker ps -q -f name=luftdaten-update)" ]; then
    echo "Running tests in existing container..."
    docker exec -it $(docker ps -q -f name=luftdaten-update) pytest "$@"
elif [ "$(docker ps -aq -f name=luftdaten-update)" ]; then
    echo "Starting container and running tests..."
    docker-compose run --rm app pytest "$@"
else
    echo "Building and running tests..."
    docker-compose run --rm app pytest "$@"
fi

