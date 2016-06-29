#! /bin/bash

sed -i 's/#dbms.read_only=false/dbms.read_only=true/g' conf/neo4j.conf
sed -i 's/#dbms.directories.data=data/dbms.directories.data=\/data/g' conf/neo4j.conf