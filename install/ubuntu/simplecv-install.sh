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
sudo apt-get install -y --force-yes git git python-dev python-numpy python-nose python-scipy ipython python-pygame
#may have to reboot after installing libraries

#Download SimpleCV
cd ~/Code/
git clone git://git.code.sf.net/p/simplecv/git.git simplecv
cd ~/Code/simplecv
#Install SimpleCV
sudo python setup.py install
