#!/bin/sh

if [ "$DEV_CONTAINER" = "1" ]; then
    echo "This script can not berun in the dev container"
    exit 1
fi

# remove containers for theis project
CONTAINERS=$(docker ps -a | grep "libreoffice_python_devcontainer" | cut -d' ' -f1)
if [ -n "$CONTAINERS" ]; then
    for container in $CONTAINERS
    do
        docker rm -f $container
    done
fi

# Build the Docker Compose project
docker rmi -f $(docker images -f "dangling=true" -q)

if [ -n $(docker images 'libreoffice_python_devcontainer-app' -q -a) ]; then
    docker rmi $(docker images 'libreoffice_python_devcontainer-app' -q -a)
fi
if [ -n $(docker images 'libreoffice_python_devcontainer-libreoffice' -q -a) ]; then
    docker rmi $(docker images 'libreoffice_python_devcontainer-libreoffice' -q -a)
fi
docker compose build --no-cache \
&& docker rmi -f $(docker images -f "dangling=true" -q)
# && docker tag devcontainer-app:latest libreoffice_python_devcontainer-app:latest \
# && docker tag devcontainer-libreoffice:latest libreoffice_python_devcontainer-libreoffice:latest \
# && docker rmi $(docker images 'devcontainer-app' -a -q) \
# && docker rmi $(docker images 'devcontainer-libreoffice' -a -q)
