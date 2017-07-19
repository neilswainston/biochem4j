#!/usr/bin/env bash
docker build -t biochem4j-build .
docker run -d biochem4j-build