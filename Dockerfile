# Build with
# sudo docker -t="simplecv" .
# Run with
# sudo docker run -p 54717:8888 -t -i simplecv

FROM ubuntu:12.04

MAINTAINER Anthony Oliver <anthony@sightmachine.com>

# Install system dependencies
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y unzip
RUN apt-get install -y wget
RUN apt-get install -y clang
RUN apt-get install -y cmake
RUN apt-get install -y python2.7
RUN apt-get install -y python2.7-dev
RUN apt-get install -y python-setuptools
RUN wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py -O - | python

# SimpleCV Specific
RUN apt-get install -y libopencv-*
RUN apt-get install -y python-opencv
RUN apt-get install -y python-numpy 
RUN apt-get install -y python-scipy
RUN apt-get install -y python-pygame
# RUN pip install PIL
RUN pip install ipython
RUN pip install pyzmq
RUN pip install jinja2
RUN pip install tornado

# SimpleCV Install
RUN wget https://github.com/sightmachine/SimpleCV/archive/master.zip
RUN unzip master
RUN cd SimpleCV-master; pip install -r requirements.txt; python setup.py install

# Use clang
ENV CC clang
ENV CXX clang++

# Environment setup
EXPOSE 8888
ENV USER docker
WORKDIR /home/docker

# Setup the notebook
RUN echo 'ipython notebook --ip=0.0.0.0 --port=8888 --no-browser'  >> start.sh
RUN chmod +x start.sh
CMD bash -C '/home/docker/start.sh';'bash'