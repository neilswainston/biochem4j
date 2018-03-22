FROM python:2.7

# Make current directory visible inside Docker container:
COPY . /biochem4j
WORKDIR /biochem4j

# Install / update relevant ubuntu packages:
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential unzip wget libgmp3-dev python-pip

# Download and install glpk:
RUN mkdir /usr/local/glpk \
	&& curl http://ftp.gnu.org/gnu/glpk/glpk-4.39.tar.gz \
	| tar xvzC /usr/local/glpk --strip-components=1 \
	&& cd /usr/local/glpk \
	&& ./configure \
	&& make \
	&& make install

# Install requirements:
RUN pip install --upgrade pip \
	&& pip install -r requirements.txt

# Update paths:
ENV LD_LIBRARY_PATH /usr/local/lib:${LD_LIBRARY_PATH}
ENV PYTHONPATH $PYTHONPATH:.

# Run:
ENTRYPOINT ["python", "-u", "sbcdb/build.py"]