# SimpleCV
--------------------------

Make computers see with SimpleCV, the Open Source Framework for Vision

SimpleCV is an framework for Open Source Machine Vision, using OpenCV and the Python programming language.    
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

### Arch Linux
    pacman -S python2-numpy opencv2.3.1_a-4 python-pygame python2-setuptools ipython2 python2-pip
    pip install https://github.com/ingenuitas/SimpleCV/zipball/master

### Mac OS X (10.6 and above)

Note: We originally tried to bundle all Mac dependencies in a superpack.  This turned out to be extremely difficult with the many differences between versions of Mac OS.  Now, with Mac, you must build from source and we will try and make it as easy as possible.  Please report a bug if you have issues.

Steps:

* Install Xcode http://itunes.apple.com/us/app/xcode/id448457090?mt=12 and then run the Xcode installer. 
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


Steps:

* (OPTIONAL) Install MinGW for optional files and building openCV from source.  Make sure to include C/C++ Compiler and msys package.  http://sourceforge.net/projects/mingw/files/Automated%20MinGW%20Installer/ 
* Install Python 2.7 http://www.python.org/getit/releases/2.7.1/
* Install Python Setup Tools for Windows http://pypi.python.org/packages/2.7/s/setuptools/ (See: http://stackoverflow.com/questions/309412/how-to-setup-setuptools-for-python-2-6-on-windows) 
* Install the SciPy superpack: http://sourceforge.net/projects/scipy/files/scipy/0.9.0rc5/scipy-0.9.0rc5-win32-superpack-python2.7.exe/download 
* Install OpenCV: http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.2/ (See: http://luugiathuy.com/2011/02/setup-opencv-for-python/)
* easy_install.exe simplecv (See: http://blog.sadphaeton.com/2009/01/20/python-development-windows-part-2-installing-easyinstallcould-be-easier.html)


---------------------------
## SimpleCV Interactive Shell, or how to run SimpleCV


Once you have SimpleCV installed, you can use it in a specialized [IPython](http://ipython.org)
shell.  This pre-loads all the symbols and gives you some extra functions
and macros for using SimpleCV.

To run the SimpleCV shell, from the installation directory type:

	simplecv

If for some reason the shell doesn't start, you can always do so manually by running:

	python -c "import SimpleCV.Shell;SimpleCV.Shell.main()"


To run SimpleCV within an ipython notebook:

	from SimpleCV import Display, Image
	display = Display(displaytype='notebook')
	image = Image('simplecv')
	image.save(display)
  

---------------------------    
## Videos - Tutorials and Demos

Video tutorials and demos can be found at:
<http://www.simplecv.org/demos/>

-------------------------------
## Getting Help

You can always head over to the SimpleCV help forums to ask questions:
(SimpleCV Help Forums) - <http://help.simplecv.org> 

--------------------
## Troubleshooting installation problems.

If for some reason the standard installation methods do not work you may have to manually install some or all of the dependencies required by SimpleCV.

### Required Libraries
The installation instructions below should explain more on how to install.  They can also be installed manually.

* Python 2.6+
* SciPy
* NumPy
* Pygame
* OpenCV 2.3+
* IPython 10+
* PIL 1.1.7+


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
* zxing (<http://code.google.com/p/zxing/>)
* python-zxing (<https://github.com/oostendo/python-zxing>)
* Tesseract (<http://code.google.com/p/tesseract-ocr/>)
* python-tesseract (<http://code.google.com/p/python-tesseract/>)
* Orange (<http://orange.biolab.si>)


    

