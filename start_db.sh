#!/usr/bin/env bash

DIR=$(cd "$(dirname "$0")"; pwd)

docker run \
--detach \
--user neo4j \
--publish=80:7474 \
--publish=7687:7687 \
--volume=$DIR/neo4j/input:/input \
-e NEO4J_AUTH=none \
-e EXTENSION_SCRIPT=/input/extension_script.sh \
neo4j