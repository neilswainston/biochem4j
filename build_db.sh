#! /bin/bash

DIR=$(cd "$(dirname "$0")"; pwd)

python sbcdb/build.py $DIR/neo4j/data/databases/graph.db