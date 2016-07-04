#! /bin/bash

PORT=7474

DIR=$(cd "$(dirname "$0")"; pwd)

eval "$(docker-machine env default)"

DOCKER_ID=$(sudo docker run \
--detach \
--publish=$PORT:7474 \
--publish=7687:7687 \
--volume=$DIR/neo4j/data:/data \
-e NEO4J_AUTH=none \
-e EXTENSION_SCRIPT=/data/extension/extension_script.sh \
neo4j:3.0)

echo "DOCKER_ID="$DOCKER_ID
echo "URL=http://"$(docker-machine ip)":"$PORT