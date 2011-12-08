Installation
================
* Note: There are also video tutorials located online at:
<http://simplecv.org>


or on the youtube channel:
<http://www.youtube.com/user/IngenuitasOfficial>


Ubuntu 10.4 or 10.11
-------------------------------------

You can now download a .deb file from SourceForge -- look at http://sourceforge.net/projects/simplecv/files for an easier install.  

Ubuntu 11.4
------------------------------------
You can upgrade your OpenCV from 2.1 to 2.2 with the following command::

    sudo add-apt-repository https://launchpad.net/~gijzelaar/+archive/opencv2 && sudo apt-get update

Then install the debian package

Ubuntu 11.10 
-------------------------------------
To upgrade from OpenCV 2.1 to OpenCV 2.3 run the following command:
   
    sudo add-apt-repository ppa:gijzelaar/cuda && sudo add-apt-repository ppa:gijzelaar/opencv2.3 && sudo apt-get update

Then install the debian package

Here is the manual method for installation:


Steps:

#. apt-get install dependencies
#. download, build and install the latest version of OpenCV
#. clone and install SimpleCV 

Commands::

    sudo apt-get install -y --force-yes build-essential swig gfortran cmake gcc pkg-config libjpeg62-dev libtiff4-dev libpng12-dev libopenexr-dev libavformat-dev libswscale-dev liblapack-dev python-dev python-setuptools boost-build libboost-all-dev
    wget http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.2/OpenCV-2.2.0.tar.bz2
    bunzip2 OpenCV-2.2.0.tar.bz2
    tar xf OpenCV-2.2.0.tar
    mkdir build
    cd build
    cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_PYTHON_SUPPORT=ON ..
    make
    sudo make install
    sudo cp /usr/local/lib/python2.6/site-packages/cv.so /usr/local/lib/python2.6/dist-packages/cv.so
    sudo apt-get install -y --force-yes git git python-dev python-numpy python-nose python-scipy ipython
    git clone git://git.code.sf.net/p/simplecv/git.git simplecv
    sudo python setup.py install

Mac OS X (10.6 and above)
-----------------------------

Note: While not required, it is strongly recommended that you install XCode from Apple: http://itunes.apple.com/us/app/xcode/

If you want to keep control of your usr/local or are adept at building for Unix, you may want to use the directions below.  Otherwise, we recommend using our Superpack, which contains everything you need in a single package:  http://sourceforge.net/projects/simplecv/files/ 

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

If you want a streamlined install which gives you all the dependencies, we
recommend using the Windows Superpack, available at http://sourceforge.net/projects/simplecv/files/

If you already have Python, OpenCV or SciPy installed and want to keep things the way you like them, follow the directions below


Steps:

#. (OPTIONAL) Install MinGW for optional files and building openCV from source.  Make sure to include C/C++ Compiler and msys package.  http://sourceforge.net/projects/mingw/files/Automated%20MinGW%20Installer/ 
#. Install Python 2.7 http://www.python.org/getit/releases/2.7.1/
#. Install Python Setup Tools for Windows http://pypi.python.org/packages/2.7/s/setuptools/ (See: http://stackoverflow.com/questions/309412/how-to-setup-setuptools-for-python-2-6-on-windows) 
#. Install the SciPy superpack: http://sourceforge.net/projects/scipy/files/scipy/0.9.0rc5/scipy-0.9.0rc5-win32-superpack-python2.7.exe/download 
#. Install OpenCV: http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.2/ (See: http://luugiathuy.com/2011/02/setup-opencv-for-python/)
#. easy_install.exe simplecv (See: http://blog.sadphaeton.com/2009/01/20/python-development-windows-part-2-installing-easyinstallcould-be-easier.html)
