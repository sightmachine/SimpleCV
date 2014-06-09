How to setup virtual environment for SimpleCV:
==============================================


This is so you can run SimpleCV under a virtualenv.  It helps with the setup
of OpenCV and no longer requires installing and then symlinking shared library
files as had been done previously.

This code and instructions have been directly nabbed from:
http://stackoverflow.com/questions/11184847/running-opencv-from-a-python-virtualenv/24112175#24112175



Instructions:
-------------------
Here is the cleanest way, using pyenv and the virtualenv plug-in.

Install Python with shared library support (so we get a libpython2.7.dylib on Mac OS X or libpython2.7.so on Linux).

env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install -v 2.7.6
Create the virtualenv, based on the version of python we just installed.

pyenv virtualenv 2.7.6 myvirtualenv
Activate the virtualenv.

pyenv shell myvirtualenv
pyenv rehash
Install numpy. Otherwise opencv will fail to link itself to Python correctly.

pip install numpy
Set the prefix of the python install.

PREFIX_MAIN=`pyenv virtualenv-prefix`
Set the prefix of the environment. (sic! The name of these pyenv commands are a bit deceptive!)

PREFIX=`pyenv prefix`
Now configure and install opencv. Notice that the opencv binaries and packages will be installed in our virtualenv while the dynamic library and includes of the Python install is used.
