#! /bin/bash

PORT=80

DIR=$(cd "$(dirname "$0")"; pwd)

docker run \
--detach \
--publish=$PORT:7474 \
--publish=7687:7687 \
--volume=$DIR/neo4j/data:/data \
--volume=$DIR/neo4j/extension:/var/lib/neo4j/extension \
-e NEO4J_AUTH=none \
-e EXTENSION_SCRIPT=extension/extension_script.sh \
neo4j:3.0

IP=$(docker-machine ip)
echo "http://"$IP":"$PORT