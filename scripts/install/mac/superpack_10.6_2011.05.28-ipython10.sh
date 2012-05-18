#!/bin/sh

#this is a modified copy from http://stronginference.com/scipy-superpack/

PYTHON=/usr/bin/python
SERVER=http://dl.dropbox.com/u/233041/PyMC

echo 'Would you like to install gFortran (required if not already installed)? (y/n)'
read install
if  [ "$install" == "y" ] || [ "$install" == "Y" ]; then
  echo 'Downloading gFortran ...'
  curl -o gfortran-42-5664.pkg http://r.research.att.com/gfortran-42-5664.pkg
  echo 'Installing gFortran ...'
  sudo installer -pkg 'gfortran-42-5664.pkg' -target '/'
elif [ "$install" == "n" ] || [ "$install" == "N" ]; then
  echo 'Skipping gFortran install.'
else
  echo 'Did not recognize input. Exiting'
  exit 0
fi
echo 'Downloading ez_setup ...'
curl -o ez_setup.py http://peak.telecommunity.com/dist/ez_setup.py
echo 'Installing ez_setup ...'
sudo python ez_setup.py
echo 'Installing numpy ...'
sudo "${PYTHON}" -m easy_install -Z ${SERVER}/numpy-2.0.0.dev_3071eab_20110527-py2.6-macosx-10.6-universal.egg
echo 'Installing matplotlib ...'
sudo "${PYTHON}" -m easy_install -Z ${SERVER}/matplotlib-1.1.0-py2.6-macosx-10.6-universal.egg
echo 'Installing scipy ...'
sudo "${PYTHON}" -m easy_install -Z ${SERVER}/scipy-0.10.0.dev_20110527-py2.6-macosx-10.6-universal.egg
echo 'Installing pymc ...'
sudo "${PYTHON}" -m easy_install -Z ${SERVER}/pymc-2.2alpha-py2.6-macosx-10.6-universal.egg
echo 'Installing readline ...'
sudo "${PYTHON}" -m easy_install -Z readline
echo 'Installing ipython ...'
#sudo "${PYTHON}" -m easy_install -Z ${SERVER}/ipython-0.11.dev-py2.6.egg
sudo "${PYTHON}" -m easy_install -Z http://ipython.scipy.org/dist/0.10.2/ipython-0.10.2-py2.6.egg 
echo 'Installing nose ...'
sudo "${PYTHON}" -m easy_install -Z nose
echo 'Installing DateUtils'
sudo "${PYTHON}" -m easy_install -Z DateUtils
echo 'Done'
