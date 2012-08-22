# SimpleCV
--------------------------

Make computers see with SimpleCV, the Open Source Framework for Vision

SimpleCV is a framework for Open Source Machine Vision, using OpenCV and the Python programming language.    
It provides a concise, readable interface for cameras, image manipulation, feature extraction, and format conversion.  Our mission is to give casual users a comprehensive interface for basic machine vision functions and an elegant programming interface for advanced users.

We like SimpleCV because:

* Even beginning programmers can write simple machine vision tests
* Cameras, video files, images, and video streams are all interoperable
* Information on image features can be extracted, sorted and filtered easily
* Manipulations are fast, with easy to remember names
* Linear algebra is strictly optional

Here is the simplecv "hello world":

    import SimpleCV
    camera = SimpleCV.Camera()
    image = camera.getImage()
    image.show()

For more code snippets, we recommend the [SimpleCV examples website](http://examples.simplecv.org) or looking at our example scripts in [SimpleCV/examples](http://github.com/ingenuitas/SimpleCV/tree/master/SimpleCV/examples)

---------------------------
## Installation

The easiest way to install SimpleCV is with the packages for your distribution (Windows, Mac, Linux) included on the website (http://www.simplecv.org).  Although it is tested on many platforms there maybe scenarios where it just won't work with the package installer. Below is instructions on how to install, if you have problems please see the troubleshooting section at the end of this README file.

### Ubuntu 12.04
	sudo apt-get install ipython python-opencv python-scipy python-numpy python-pygame python-setuptools python-pip 
	sudo pip install https://github.com/ingenuitas/SimpleCV/zipball/master

then just run 'simplecv' from the shell.

### Virtualenv

This is how to install SimpleCV under a python virtual environment [virtualenv] (http://www.virtualenv.org).  This maybe useful in cases where you want to keep your system libraries clean and not install extra libraries.  This method has only been tested on Ubuntu 12.04, it maybe possible to port to other operating systems.

Run the following commands:

    sudo apt-get install python-opencv python-setuptools python-pip gfortran g++ liblapack-dev libsdl1.2-dev libsmpeg-dev mercurial
    sudo pip install virtualenv
    virtualenv venv
    cd venv
    mkdir src
    ln -s /usr/local/lib/python2.7/dist-packages/cv2.so lib/python2.7/site-packages/cv2.so
    ln -s /usr/local/lib/python2.7/dist-packages/cv.py lib/python2.7/site-packages/cv.py
    ./bin/pip install https://github.com/numpy/numpy/zipball/master
    ./bin/pip install https://github.com/scipy/scipy/zipball/master
    ./bin/pip install PIL
    ./bin/pip install ipython
    mkdir src
    wget -O src/pygame.tar.gz https://bitbucket.org/pygame/pygame/get/6625feb3fc7f.tar.gz
    cd src
    tar zxvf pygame.tar.gz
    cd ..
    ./bin/python src/pygame-pygame-6625feb3fc7f/setup.py -setuptools install
    ./bin/pip install https://github.com/ingenuitas/SimpleCV/zipball/master
  





### Arch Linux
    pacman -S python2-numpy opencv2.3.1_a-4 python-pygame python2-setuptools ipython2 python2-pip
    pip install https://github.com/ingenuitas/SimpleCV/zipball/master

### Mac OS X (10.6 and above)

Note: We originally tried to bundle all Mac dependencies in a superpack.  This turned out to be extremely difficult with the many differences between versions of Mac OS.  Now, with Mac, you must build from source and we will try and make it as easy as possible.  Please report a bug if you have issues.

Steps:

* Install Xcode https://developer.apple.com/xcode/ and then run the Xcode installer. 
* Install homebrew https://github.com/mxcl/homebrew/wiki/installation
* Use homebrew to install opencv, git, and the python imaging library (PIL needs the ARCHFLAGS tweak), plus the SDL dependencies for pygame
*  Homebrew puts the libraries in /usr/local/lib/, which by default isn't in the python sys.path -- either add it, or link the files
* Install scipy superpack for Mac OSX http://fonnesbeck.github.com/ScipySuperpack/
* easy_install pip and use pip install pygame
* clone simplecv and python setup.py install

Before you do these you must install XCode from the App Store and run the installer!  I'd also run these someplace you don't mind dumping a little code:

Commands (for Lion)::

    mkdir ~/Code
    cd ~/Code
    /usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"
    brew install opencv
    brew install git
    brew install sdl sdl_image sdl_mixer sdl_ttf smpeg portmidi 
    ARCHFLAGS="-arch i386 -arch x86_64" brew install PIL 
    ln -s /usr/local/lib/python2.7/site-packages/cv.so /Library/Python/2.7/site-packages/cv.so
    sudo ln -s /usr/local/lib/python2.7/site-packages/PIL /Library/Python/2.7/site-packages/PIL
    sudo ln -s /usr/local/lib/python2.7/site-packages/cv2.so /Library/Python/2.7/site-packages/cv2.so
    sudo ln -s /usr/local/lib/python2.7/site-packages/cv.py /Library/Python/2.7/site-packages/cv.py
    sudo easy_install pip
    sudo pip install hg+http://bitbucket.org/pygame/pygame
    curl -sO https://raw.github.com/fonnesbeck/ScipySuperpack/master/install_superpack.sh && source install_superpack.sh
    pip install https://github.com/ingenuitas/SimpleCV/zipball/master 

Commands (for Snow Leopard)::

    mkdir ~/Code
    cd ~/Code
    /usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"
    brew install opencv
    brew install git
    brew install sdl sdl_image sdl_mixer sdl_ttf smpeg portmidi 
    ARCHFLAGS="-arch i386 -arch x86_64" brew install PIL 
    ln -s /usr/local/lib/python2.6/site-packages/cv.so /Library/Python/2.6/site-packages/cv.so
    sudo ln -s /usr/local/lib/python2.6/site-packages/PIL /Library/Python/2.6/site-packages/PIL
    sudo ln -s /usr/local/lib/python2.6/site-packages/cv2.so /Library/Python/2.6/site-packages/cv2.so
    sudo ln -s /usr/local/lib/python2.6/site-packages/cv.py /Library/Python/2.6/site-packages/cv.py
    sudo easy_install pip
    sudo pip install hg+http://bitbucket.org/pygame/pygame
    curl -sO https://raw.github.com/fonnesbeck/ScipySuperpack/master/install_superpack.sh | source install_superpack.sh
    pip install https://github.com/ingenuitas/SimpleCV/zipball/master 



### Windows 7/Vista
If you want a streamlined install which gives you all the dependencies, we
recommend using the Windows Superpack, available at <http://www.simplecv.org/download/>

If you already have Python, OpenCV or SciPy installed and want to keep things the way you like them, follow the directions below


#### Install Prerequisties if they aren't already installed on your system:

* Install Python 2.7: http://www.python.org/ftp/python/2.7.3/python-2.7.3.msi
* Install Python Setup Tools for Windows: http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11.win32-py2.7.exe
* Install the SciPy superpack: http://sourceforge.net/projects/scipy/files/scipy/0.9.0rc5/scipy-0.9.0rc5-win32-superpack-python2.7.exe/download
* Install the NumPy superpack: http://sourceforge.net/projects/numpy/files/NumPy/1.6.2/numpy-1.6.2-win32-superpack-python2.7.exe/download
* Install Pygame for windows: http://pygame.org/ftp/pygame-1.9.1.win32-py2.7.msi



#### Install OpenCV:
* Download OpenCV 2.3 Superpack: http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.3.1/OpenCV-2.3.1-win-superpack.exe/download
* Run the executable file and when it ask where to extract to use::

    C:\OpenCV2.3\


* (OPTIONAL) Install MinGW for optional files and building openCV from source.  Make sure to include C/C++ Compiler and msys package.  (http://sourceforge.net/projects/mingw/files/Automated%20MinGW%20Installer/)

Once these are installed you need to add Python to your Path, open a command line (start->run->cmd)::

    SETX PATH C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.3/opencv/build/x86/vc10/bin/;%PATH%
    SETX PYTHONPATH C:/OpenCV2.3/opencv/build/python/2.7/;%PYTHONPATH%

Exit the command line and reopen so it loads the updated python paths, then run::

    easy_install pyreadline
    easy_install PIL
    easy_install cython
    easy_install pip
    pip install ipython
    pip install https://github.com/ingenuitas/SimpleCV/zipball/1.3

---------------------------
## SimpleCV Interactive Shell, or how to run SimpleCV


Once you have SimpleCV installed, you can use it in a specialized [IPython](http://ipython.org)
shell.  This pre-loads all the symbols and gives you some extra functions
and macros for using SimpleCV.

To run the SimpleCV shell, from the installation directory type:

	simplecv

If for some reason the shell doesn't start, you can always do so manually by running:

	python -c "import SimpleCV.Shell;SimpleCV.Shell.main()"


To run SimpleCV within an ipython notebook (ipython-notebooks are required to be installed):

  simplecv notebook
  

---------------------------    
## Videos - Tutorials and Demos

Video tutorials and demos can be found at:
<http://www.simplecv.org/learn/>

-------------------------------
## Getting Help

You can always head over to the SimpleCV help forums to ask questions:
(SimpleCV Help Forums) - <http://help.simplecv.org> 

--------------------
## Troubleshooting installation problems.

If for some reason the standard installation methods do not work you may have to manually install some or all of the dependencies required by SimpleCV.

### Required Libraries
The installation instructions below should explain more on how to install.  They can also be installed manually.

* Python 2.6+ (<http://www.python.org>)
* SciPy (<http://www.scipy.org>)
* NumPy (<http://numpy.scipy.org>)
* Pygame (<http://www.pygame.org>)
* OpenCV 2.3+ (<http://opencv.org>)
* IPython 10+ (<http://ipython.org>)
* PIL 1.1.7+ (<http://www.pythonware.com/products/pil/>)


### Optional Libraries
These libraries are NOT required to run or use SimpleCV but are needed for some of the examples if they are ran.  Some of these may be included in your systems software manager or app store.

* PIP
* BeaufitulSoup
* webm 
* freenect (<http://openkinect.org>)
* python nose
* pyfirmata
* cherrypy
* flask
* simplejson
* werkzeug
* webkit
* gtk
* zbar (<http://zbar.sourceforge.net/>)
* Tesseract (<http://code.google.com/p/tesseract-ocr/>)
* python-tesseract (<http://code.google.com/p/python-tesseract/>)
* Orange (<http://orange.biolab.si>)


    

