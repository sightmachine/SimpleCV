Installation
================
Note: There are also video tutorials located online at:
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

Note: We originally tried to bundle all Mac dependencies in a superpack.  This turned out to be extremely difficult with the many differences between versions of Mac OS.  Now, with Mac, you must build from source and we will try and make it as easy as possible.  Please report a bug if you have issues.

Steps:

#. Install Xcode http://itunes.apple.com/us/app/xcode/id448457090?mt=12 and then run the Xcode installer. 
#. Install homebrew https://github.com/mxcl/homebrew/wiki/installation
#. Use homebrew to install opencv, git, and the python imaging library (PIL needs the ARCHFLAGS tweak)
#  Homebrew puts the libraries in /usr/local/lib/, which by default isn't in the python sys.path -- either add it, or link the files
#. Install scipy superpack for Mac OSX http://fonnesbeck.github.com/ScipySuperpack/
#. Install pygame using the installer appropriate for Lion or Snow Leopard (not the pure python packages, the mpkg.zip files)
#. clone simplecv and python setup.py install

Before you do these you must install XCode from the App Store and run the installer!  I'd also run these someplace you don't mind dumping a little code:

Commands (for Lion)::

    mkdir ~/Code
    cd ~/Code
    /usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"
    brew install opencv
    brew install git
    brew install wget  
    ARCHFLAGS="-arch i386 -arch x86_64" brew install PIL 
    ln -s /usr/local/lib/python2.7/site-packages/cv.so /Library/Python/2.7/site-packages/cv.so
    sudo ln -s /usr/local/lib/python2.7/site-packages/PIL /Library/Python/2.7/site-packages/PIL
    sudo ln -s /usr/local/lib/python2.7/site-packages/cv2.so /Library/Python/2.7/site-packages/cv2.so
    sudo ln -s /usr/local/lib/python2.7/site-packages/cv.py /Library/Python/2.7/site-packages/cv.py
    sudo easy_install pip
    curl -sO https://raw.github.com/fonnesbeck/ScipySuperpack/master/install_superpack.sh | source install_superpack.sh
    wget http://www.pygame.org/ftp/pygame-1.9.2pre-py2.7-macosx10.7.mpkg.zip
    unzip pygame-1.9.2pre-py2.7-macosx10.7.mpkg.zip && open pygame-1.9.2pre-py2.7-macosx10.7.mpkg
    pip install https://github.com/ingenuitas/SimpleCV/zipball/master 

Commands (for Snow Leopard)::

    mkdir ~/Code
    cd ~/Code
    /usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"
    brew install opencv
    brew install git
    brew install wget  
    ARCHFLAGS="-arch i386 -arch x86_64" brew install PIL 
    ln -s /usr/local/lib/python2.6/site-packages/cv.so /Library/Python/2.6/site-packages/cv.so
    sudo ln -s /usr/local/lib/python2.6/site-packages/PIL /Library/Python/2.6/site-packages/PIL
    sudo ln -s /usr/local/lib/python2.6/site-packages/cv2.so /Library/Python/2.6/site-packages/cv2.so
    sudo ln -s /usr/local/lib/python2.6/site-packages/cv.py /Library/Python/2.6/site-packages/cv.py
    sudo easy_install pip
    curl -sO https://raw.github.com/fonnesbeck/ScipySuperpack/master/install_superpack.sh | source install_superpack.sh
    wget http://www.pygame.org/ftp/pygame-1.9.2pre-py2.6-macosx10.6.mpkg.zip 
    unzip pygame-1.9.2pre-py2.6-macosx10.6.mpkg.zip && open pygame-1.9.2pre-py2.6-macosx10.6.mpkg 
    pip install https://github.com/ingenuitas/SimpleCV/zipball/master 



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
