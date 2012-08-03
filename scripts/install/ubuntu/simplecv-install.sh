#!/bin/sh
#
# This script is used to install SimpleCV very quickly on
# * Ubuntu 12.04
# *(Other versions may work)
#
# !Warning: Please review this script, you are responsible for anything
# it does to your system. You should be able to run these from the
# command line manually if desired. If you are running into issues
# please visit the mailing list at:
# http://www.simplecv.org
#
echo "Install SimpleCV"
echo "Installing pre-reqisites"
sleep 1
#echo "Installing OpenCV..."
#sudo apt-get install libopencv-*
#sudo apt-get install python-opencv
#echo "OpenCV installed"
echo "Installing numpy and scipy"
sudo apt-get install python-numpy python-scipy
echo "numpy and scipy installed"
echo "Installing pygame"
sudo apt-get install python-pygame
echo "pygame installed"
echo "Installing python-setuptools"
sudo apt-get install python-setuptools
echo "setuptools installed"
echo "Installing ipython and ipython notebook"
sudo apt-get install ipython ipython-notebook
echo "ipython installed"
ehco "Downloading SimpleCV"
git clone https://github.com/ingenuitas/SimpleCV.git
echo "Installing SimpleCV"
cd SimpleCV/
sudo python setup.py install
echo "SimpleCV Installation finished"
echo "For more info go to http://simplecv.org/"
echo "$ simplecv"
