#!/bin/bash

# Script to run the bomb lab in a Docker container

set -e

echo "Building Docker container for bomb lab..."
sudo docker build -t bomb39 .

echo "Starting container..."
sudo docker run -it --rm \
    --name bomb39-container \
    -v "$(pwd):/bomb" \
    -w /bomb \
    bomb39 /bin/bash

echo "Container stopped."
