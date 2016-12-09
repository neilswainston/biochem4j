#!/usr/bin/env bash
docker build --build-arg GUROBI_KEY=$1 -t synbiochem-db-build .
docker run -d synbiochem-db-build