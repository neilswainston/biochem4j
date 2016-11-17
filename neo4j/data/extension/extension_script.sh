#!/usr/bin/env bash

sed -i 's/#dbms.read_only=false/dbms.read_only=true/g' conf/neo4j.conf
sed -i 's/#dbms.directories.data=data/dbms.directories.data=\/data/g' conf/neo4j.conf
sed -i 's/#dbms.connector.http.address/dbms.connector.http.address/g' conf/neo4j.conf
sed -e '$a\browser.post_connect_cmd=style \/data\/layout\/synbiochem-db.grass' conf/neo4j.conf