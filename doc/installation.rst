Installation
================

Ubuntu (10.4 or above)
-------------------------------------

Steps:

#. apt-get install dependencies
#. download, build and install the latest version of OpenCV
#. clone and install SimpleCV 

Commands::

    sudo apt-get install git python-dev python-numpy python-nose python-scipy ipython
    wget http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.2/OpenCV-2.2.0.tar.bz2
    bunzip2 OpenCV-2.2.0.tar.bz2
    tar xf OpenCV-2.2.0.tar
    cd OpenCV-2.2.0
    mkdir build
    cd build
    cmake -D CMAKE_BUILD_TYPE=RELEASE -D BUILD_PYTHON_SUPPORT=ON ..
    make
    sudo make install
    git clone git://git.code.sf.net/p/simplecv/git.git simplecv 
    cd simplecv
    sudo setup.py install

Mac OS X (10.5.8 and above)
-----------------------------

Steps:

#. Install Xcode http://developer.apple.com/technologies/xcode.html
#. Install homebrew https://github.com/mxcl/homebrew/wiki/installation
#. Use homebrew to install opencv and git
#. Install scipy superpack http://stronginference.com/scipy-superpack/
#. clone simplecv and python setup.py install

Commands::

    ruby -e "$(curl -fsSLk https://gist.github.com/raw/323731/install_homebrew.rb)"
    wget http://idisk.mac.com/fonnesbeck-Public/superpack_10.6_2011.03.25.sh
    sh superpack_10.6_2011.03.25.sh
    brew install opencv
    ln -s /usr/local/lib/python2.6/site-packages/cv.so /Library/Python/2.6/site-packages/cv.so
    brew install git
    git clone git://git.code.sf.net/p/simplecv/git.git simplecv
    cd simplecv
    python setup.py install



