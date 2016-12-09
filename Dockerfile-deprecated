FROM python:2.7.10

ARG GUROBI_KEY

ENV HOME_DIR /home/docker_user

RUN mkdir -p $HOME_DIR && \
	groupadd -r docker_group && \
	useradd -r -g docker_group -d $HOME_DIR docker_user

COPY . $HOME_DIR
WORKDIR $HOME_DIR

RUN pip install --upgrade pip && \
	pip install numpy && \
	pip install -r requirements.txt

RUN cd $HOME_DIR && \
	curl http://packages.gurobi.com/6.5/gurobi6.5.2_linux64.tar.gz --output gurobi6.5.2_linux64.tar.gz && \
	tar -xvf gurobi6.5.2_linux64.tar.gz && \
	cd gurobi652/linux64 && \
	python setup.py install && \
	chown -v -R docker_user:docker_group $HOME_DIR
	
ENV GUROBI_HOME $HOME_DIR/gurobi652/linux64
ENV PATH $PATH:$GUROBI_HOME/bin
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:$GUROBI_HOME/lib

USER docker_user

RUN cd ~/gurobi652/linux64/bin && \
	./grbgetkey $GUROBI_KEY && \
	cd ~

ENV PYTHONPATH $PYTHONPATH:$HOME_DIR

ENTRYPOINT ["python"]
CMD ["-u", "sbcdb/build.py", "/neo4j/data/databases/graph.db"]