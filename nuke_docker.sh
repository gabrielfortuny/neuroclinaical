#!/bin/bash

# Stop all running containers
docker stop $(docker ps -aq) 2>/dev/null

# Remove all containers
docker rm -f $(docker ps -aq) 2>/dev/null

# Remove all images
docker rmi -f $(docker images -q) 2>/dev/null

# Remove all volumes
docker volume rm -f $(docker volume ls -q) 2>/dev/null

# Remove all user-defined networks (excluding bridge, host, none)
docker network rm $(docker network ls | grep -vE 'bridge|host|none' | awk 'NR>1 {print $1}') 2>/dev/null

# Remove build cache
docker builder prune -af

# Optional deep cleanup (catches remaining unused stuff)
docker system prune -a --volumes -f

echo "docker cooked"
