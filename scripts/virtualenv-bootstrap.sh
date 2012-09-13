#!/bin/bash

reset
echo "This Script Creates a python virtual environment for SimpleCV"
echo ""
echo ""
read -p "Continue [Y/n]? " -n 1
if [[ $REPLY =~ ^[Nn]$ ]]
then
		echo ""
    exit 1
fi

read -p "Install System Level Dependencies [y/N]? " -n 1
if [[ $REPLY =~ ^[Yy]$ ]]
then
		echo ""
		echo "Installing System Dependencies....."
    sudo apt-get install python-opencv python-setuptools python-pip gfortran g++ liblapack-dev libsdl1.2-dev libsmpeg-dev
fi


echo "Creating Virtual Environment"
virtualenv --distribute venv
echo "Entering Virtual Environment"
cd venv
echo "Symbolic Linking OpenCV"
ln -s /usr/local/lib/python2.7/dist-packages/cv2.so lib/python2.7/site-packages/cv2.so
ln -s /usr/local/lib/python2.7/dist-packages/cv.py lib/python2.7/site-packages/cv.py
echo "Installing dependencies"
./bin/pip install https://github.com/numpy/numpy/zipball/master
./bin/pip install https://github.com/scipy/scipy/zipball/master
./bin/pip install PIL
./bin/pip install ipython
echo "Downloading pygame"
mkdir src
wget -O src/pygame.tar.gz https://bitbucket.org/pygame/pygame/get/6625feb3fc7f.tar.gz
cd src
tar zxvf pygame.tar.gz
cd ..
echo "Running setup for pygame"
./bin/python src/pygame-pygame-6625feb3fc7f/setup.py -setuptools install
./bin/pip install https://github.com/ingenuitas/SimpleCV/zipball/master

reset
echo "SimpleCV should now be installed in the virtual environment"
echo "to run just type:"
echo ""
echo "cd venv"
echo "source bin/activate"
echo "simplecv"
echo ""

