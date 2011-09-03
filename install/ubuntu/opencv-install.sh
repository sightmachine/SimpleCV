#!/bin/sh
#
# This script is used to install SimpleCV very quickly on
# 	* Ubuntu 10.10
#		*(Other versions may work)
#
# !Warning: Please review this script, you are responsible for anything
# it does to your system. You should be able to run these from the
# command line manually if desired.  If you are running into issues
# please visit the mailing list at:
# http://www.simplecv.org
#

#download all libraries needed for SimpleCV
sudo apt-get install -y --force-yes build-essential swig gfortran cmake gcc pkg-config libjpeg62-dev libtiff4-dev libpng12-dev libopenexr-dev libavformat-dev libswscale-dev liblapack-dev python-dev python-setuptools boost-build libboost-all-dev
#may have to reboot after installing libraries

#Download OpenCV
mkdir ~/Code
cd ~/Code
wget http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.2/OpenCV-2.2.0.tar.bz2
bunzip2 ~/Code/OpenCV-2.2.0.tar.bz2
tar xf ~/Code/OpenCV-2.2.0.tar
cd ~/Code/OpenCV-2.2.0

#Build OpenCV
mkdir ~/Code/OpenCV-2.2.0/build
cd ~/Code/OpenCV-2.2.0/build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_PYTHON_SUPPORT=ON -D WITH_TBB=ON ..
make
sudo make install

#Fix the wrong path that OpenCV installs it in:
sudo cp /usr/local/lib/python2.6/site-packages/cv.so /usr/local/lib/python2.6/dist-packages/cv.so
