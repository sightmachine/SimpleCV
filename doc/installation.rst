Installation
================

Ubuntu (10.4 or above)
-------------------------------------

Steps:

#. apt-get install dependencies
#. download, build and install the latest version of OpenCV
#. clone and install SimpleCV 

Commands::

    sudo apt-get install -y --force-yes build-essential swig gfortran cmake gcc pkg-config libjpeg62-dev libtiff4-dev libpng12-dev libopenexr-dev libavformat-dev libswscale-dev liblapack-dev python-dev python-setuptools boost-build libboost-all-dev
    wget http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.2/OpenCV-2.2.0.tar.bz2
    bunzip2 ~/Code/OpenCV-2.2.0.tar.bz2
    tar xf ~/Code/OpenCV-2.2.0.tar
    cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_PYTHON_SUPPORT=ON ..
    make
    sudo make install
    sudo cp /usr/local/lib/python2.6/site-packages/cv.so /usr/local/lib/python2.6/dist-packages/cv.so
    sudo apt-get install -y --force-yes git git python-dev python-numpy python-nose python-scipy ipython
    git clone git://git.code.sf.net/p/simplecv/git.git simplecv
    sudo python setup.py install

Mac OS X (10.5.8 and above)
-----------------------------

Steps:

#. Install Xcode http://developer.apple.com/technologies/xcode.html
#. Install homebrew https://github.com/mxcl/homebrew/wiki/installation
#. Use homebrew to install opencv and git
#. Install scipy superpack, but with ipython 0.10.2 http://stronginference.com/scipy-superpack/ (download from http://ingenuitas.com/misc/superpack_10.6_2011.05.28-ipython10.sh)
#. Install python imaging library (10.6 needs ARCHFLAGS tweak)
#. clone simplecv and python setup.py install

Commands::

    ruby -e "$(curl -fsSLk https://gist.github.com/raw/323731/install_homebrew.rb)"
    wget http://ingenuitas.com/misc/superpack_10.6_2011.05.28-ipython10.sh 
    sh superpack_10.6_2011.05.28-ipython10.sh
    brew install opencv
    ln -s /usr/local/lib/python2.6/site-packages/cv.so /Library/Python/2.6/site-packages/cv.so
    brew install git
    ARCHFLAGS="-arch i386 -arch x86_64" brew install PIL 
    git clone git://git.code.sf.net/p/simplecv/git.git simplecv
    cd simplecv
    python setup.py install


Windows 7/Vista
------------------------------------

Steps:

#. (OPTIONAL) Install MinGW for optional files and building openCV from source.  Make sure to include C/C++ Compiler and msys package.  http://sourceforge.net/projects/mingw/files/Automated%20MinGW%20Installer/ 
#. Install Python 2.7 http://www.python.org/getit/releases/2.7.1/
#. Install Python Setup Tools for Windows http://pypi.python.org/packages/2.7/s/setuptools/ (See: http://stackoverflow.com/questions/309412/how-to-setup-setuptools-for-python-2-6-on-windows) 
#. Install the SciPy superpack: http://sourceforge.net/projects/scipy/files/scipy/0.9.0rc5/scipy-0.9.0rc5-win32-superpack-python2.7.exe/download 
#. Install OpenCV: http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.2/ (See: http://luugiathuy.com/2011/02/setup-opencv-for-python/)
#. easy_install.exe simplecv (See: http://blog.sadphaeton.com/2009/01/20/python-development-windows-part-2-installing-easyinstallcould-be-easier.html)
