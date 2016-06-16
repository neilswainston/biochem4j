#! /bin/bash

sed -i 's/#dbms.read_only=false/dbms.read_only=true/p' conf/neo4j.conf