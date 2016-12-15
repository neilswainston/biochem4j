#!/usr/bin/env bash
DIR=$(cd "$(dirname "$0")"; pwd)

cd $DIR

pip install --upgrade pip
pip install --upgrade numpy
pip install --upgrade -r requirements.txt

if [ ! -d gurobi652 ]; then
    curl http://packages.gurobi.com/6.5/gurobi6.5.2_linux64.tar.gz --output gurobi6.5.2_linux64.tar.gz
	tar -xvf gurobi6.5.2_linux64.tar.gz
	cd gurobi652/linux64
	python setup.py install
fi

export GUROBI_HOME=$DIR/gurobi652/linux64
export PATH=$PATH:$GUROBI_HOME/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$GUROBI_HOME/lib

if [ $# -eq 1 ]
	then
		cd $DIR/gurobi652/linux64/bin
		./grbgetkey $1
		cd $DIR
fi

export PYTHONPATH=$PYTHONPATH:$DIR

python sbcdb/build.py /neo4j/data/databases/graph.db