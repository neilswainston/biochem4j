#! /bin/bash

DIR=$(cd "$(dirname "$0")"; pwd)

export PYTHONPATH=/path/to/my/library:$DIR

python sbcdb/build.py $DIR/neo4j/data/databases/graph.db