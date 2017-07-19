#!/usr/bin/env bash

DIR=$(cd "$(dirname "$0")"; pwd)

docker run \
--detach \
--publish=80:7474 \
--publish=7687:7687 \
--volume=$DIR/neo4j/data:/data \
-e NEO4J_AUTH=none \
-e EXTENSION_SCRIPT=/data/extension/extension_script.sh \
neo4j:3.2