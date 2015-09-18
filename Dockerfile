FROM kbastani/docker-neo4j

MAINTAINER Neil Swainston <neil.swainston@manchester.ac.uk>

RUN apt-get update && apt-get install -y \
	python \
	python-dev \
	python-pip

RUN pip install py2neo

ADD . /src
WORKDIR /src