#!/usr/bin/env bash

sudo pip install libchebipy
sudo pip install synbiochem-py --ignore-installed six

DIR=$(cd "$(dirname "$0")"; pwd)
export PYTHONPATH=$PYTHONPPATH:$DIR

python sbcdb/build.py $DIR/neo4j/data/databases/graph.db