#!/usr/bin/env bash

DIR=$(cd "$(dirname "$0")"; pwd)

docker build -t biochem4j-build .
docker run -d -v $DIR/neo4j:/biochem4j/neo4j biochem4j-build neo4j/input | True