--------------------------
# SimpleCV
--------------------------

[![Build Status](https://travis-ci.org/sightmachine/SimpleCV.png?branch=develop)](https://travis-ci.org/sightmachine/SimpleCV)


Quick Links:

 * [About](#about)
 * [Installation](#installation)
    * [Docker] (#docker)
    * [Ubuntu](#ubuntu-1204)
    * [Virtual Environment](#virtualenv)
    * [Arch Linux](#arch-linux)
    * [Fedora](#fedora)
    * [MacOS](#mac-os-x-106-and-above)
    * [Windows](#windows-7vista)
    * [Raspberry Pi](#raspberry-pi)
 * [SimpleCV Shell](#simplecv-interactive-shell-or-how-to-run-simplecv)
 * [Videos & Tutorials](#videos---tutorials-and-demos)
 * [SimpleCV on Mobile - Android](#simplecv-on-mobile-android)
 * [Help](#getting-help)
 * [Troubleshooting Installation](#troubleshooting-installation-problems)
    * [Required Libraries](#required-libraries)
    * [Optional Libraries](#optional-libraries)


<a id="about"></a>
## About
---------------------------
Make computers see with SimpleCV, the Open Source Framework for Computer Vision

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

For more code snippets, we recommend the [SimpleCV examples website](http://examples.simplecv.org) or looking at our example scripts in [SimpleCV/examples](http://github.com/sightmachine/SimpleCV/tree/master/SimpleCV/examples)

---------------------------
<a id="installation"></a>
## Installation

The easiest way to install SimpleCV is with the packages for your distribution (Windows, Mac, Linux) included on the website (http://www.simplecv.org).  Although it is tested on many platforms there maybe scenarios where it just won't work with the package installer. Below is instructions on how to install, if you have problems please see the troubleshooting section at the end of this README file.

<a id="docker"></a>
### Docker
This is the recommended way of installing SimpleCV as you can be sure the environment will be setup the same exact way as it's suppose to be on your machine.

*WARNING*: Using docker does not allow the webcam to work, it also doesn't work with Image.show(), so essentially requires you to use simplecv within an IPython notebook.

The first step is to install docker on your machine if you have not, this should work for Windows, Mac, and Linux, please follow instructions at:
<a href="https://docs.docker.com/installation/">https://docs.docker.com/installation/</a>

Once docker is installed you can run simplecv as easy as (may have to run as sudo, depending on OS):

    docker pull sightmachine/simplecv

It will probably take a little while to download, but once done just run (may need to run as sudo, depending on OS):

    docker run -p 54717:8888 -t -i sightmachine/simplecv

Then just open your web browser and go to:

    http://localhost:54717
    
**NOTE**: If you are using a Mac or Windows it will be a little different since you will be boot2docker to run.  When you run boot2docker up it should show the ip address of the docker service.  It could be something like 192.168.59.103, but this will change as it's random.  Once you know that ip you will just go to that IP address with the correct port instead:

    http://192.168.59.103:54717

You will get a Ipython notebook inteface, start a new notebook and enter the following:

    from SimpleCV import *
    disp = Display(displaytype='notebook')
    img = Image('simplecv')
    img.save(disp)

You should now see the simplecv logo and now have a full simplecv environment setup to start playing around.

<a id="ubuntu-1204"></a>
### Ubuntu 12.04
Install with pip

	sudo apt-get install ipython python-opencv python-scipy python-numpy python-pygame python-setuptools python-pip
	sudo pip install https://github.com/sightmachine/SimpleCV/zipball/develop

Install using clone of SimpleCV repository

    sudo apt-get install ipython python-opencv python-scipy python-numpy python-pygame python-setuptools git
    git clone https://github.com/sightmachine/SimpleCV.git
    cd SimpleCV/
    sudo pip install -r requirements.txt
    sudo python setup.py install

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
    ./bin/pip install -r requirements.txt
    mkdir src
    wget -O src/pygame.tar.gz https://bitbucket.org/pygame/pygame/get/6625feb3fc7f.tar.gz
    cd src
    tar zxvf pygame.tar.gz
    cd ..
    ./bin/python src/pygame-pygame-6625feb3fc7f/setup.py -setuptools install
    ./bin/pip install https://github.com/sightmachine/SimpleCV/zipball/develop





<a id="archlinux"></a>
### Arch Linux
Install using pip

    pacman -S python2-numpy opencv2.4.4_1 python-pygame python2-setuptools ipython2 python2-pip
    pip install https://github.com/sightmachine/SimpleCV/zipball/develop

Install using clone of SimpleCV repository

    pacman -S python2-numpy opencv2.4.4_1 python-pygame python2-setuptools ipython2
    git clone https://github.com/sightmachine/SimpleCV.git
    cd SimpleCV/
    sudo python setup.py install

Install development version using aur

    yaourt -S simplecv-git

<a id="fedora"></a>
### Fedora
#### Fedora 20 and above

    sudo yum -y install python-SimpleCV

#### Fedora 18
Install with pip

    sudo yum -y install python-ipython opencv-python scipy numpy pygame python-setuptools python-pip
    sudo python-pip install https://github.com/sightmachine/SimpleCV/zipball/develop

Install using clone of SimpleCV repository

    sudo yum -y install python-ipython opencv-python scipy numpy pygame python-setuptools python-pip git
    git clone https://github.com/sightmachine/SimpleCV.git
    cd SimpleCV/
    sudo python setup.py install

<a id="macos">
### Mac OS X (10.6 and above)
</a>

**General OSX Overview**

Note: We originally tried to bundle all Mac dependencies in a superpack.  This turned out to be extremely difficult with the many differences between versions of Mac OS.  Now, with Mac, you must build from source and we will try and make it as easy as possible.  Please report a bug if you have issues.


---------------------------
**Explicit (as in every step) instructions compliments of JHawkins**

*These instructions are geared towards people who are just getting started with python development on OSX. They will walk you through setting up all the tools you need to build SimpleCV from scratch. If you don't know which instructions you want, you probably want to use these.*

Install Xcode via App Store
Start Xcode and go to Xcode >> Preferences >> Downloads >> click Install across from Command Line Tools
If Terminal is already running, shut it down and reopen it
OS X's permissions on /usr/local are too restrictive and must be changed via:

    sudo chown -R `whoami` /usr/local

Install homebrew via Terminal using:

    ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"

Ignore the single warning that instructs you to install Xcode's CLI tools (you did that already)
To verify that homebrew is installed correctly and working, run:

    brew doctor

Address any errors before moving on. Remember, Google is your friend.
Note: If you run VM's on my via Parallels and run into multiple warnings related to "osxfuse" thi go to System Preferences >> FUSE for OS X >> Click Remove OSXFUSE. I can add it back later if needed.
Once the doctor tells you that you are 'raring to brew', run:

    brew update

followed by

    brew upgrade

Install OpenCV via homebrew by running:

    brew tap homebrew/science
    brew install opencv

Be sure to add the requested line to you ~/.bash_profile:

    export PYTHONPATH="/usr/local/lib/python2.7/site-packages:$PYTHONPATH"

Source your ~/.bash_profile file so that the changes take effect:

    source ~/.bash_profile

Install Git via homebrew by running:

    brew install git

Install SDL dependencies (can anyone clarify this?) via homebrew by running:

    brew install sdl sdl_image sdl_mixer sdl_ttf portmidi

Install XQuartz from https://xquartz.macosforge.org
Homebrew can't install smpeg at the time of this writing however there is a workaround:

    brew tap homebrew/headonly
    brew install --HEAD smpeg

If you get a connection refused error, wait a minute and try again.
Download PIL:

    curl -O -L http://effbot.org/media/downloads/Imaging-1.1.7.tar.gz

In the unpacked folder:

    python setup.py build --force
    sudo python setup.py install

Manually create a few PIL symlinks:

    sudo ln -s /usr/local/lib/python2.6/site-packages/cv.so /Library/Python/2.6/site-packages/cv.so
    sudo ln -s /usr/local/lib/python2.6/site-packages/PIL /Library/Python/2.6/site-packages/PIL
    sudo ln -s /usr/local/lib/python2.6/site-packages/cv2.so /Library/Python/2.6/site-packages/cv2.so
    sudo ln -s /usr/local/lib/python2.6/site-packages/cv.py /Library/Python/2.6/site-packages/cv.py

Install PIP by running:

    sudo easy_install pip

Install the Scipy Superpack from http://fonnesbeck.github.com/ScipySuperpack/
Install Mercurial via homebrew by running:

     brew install mercurial

Install pygame via PIP by running:

    sudo pip install hg+http://bitbucket.org/pygame/pygame

Install svgwrite by running:

    sudo pip install svgwrite

**Note:** SimpleCV's developers made a change (for the better) here that I am including, however everything up to this point is 100% guaranteed to work, because it's exactly what I did. Keeping true to that, I'll present both options. *We both suggest using the develop branch.*
**Developer's Instructions** Install SimpleCV from the git repo and then run setup.

    git clone https://github.com/sightmachine/SimpleCV.git
    cd SimpleCV/
    sudo python setup.py install

**JHawkins' Instructions** Install SimpleCV via PIP by running:

    sudo pip install https://github.com/sightmachine/SimpleCV/zipball/master

Test by running simplecv in the command line:

    simplecv

If it starts (it should!) be sure to check out:

     example()

--------------------------------
**Lion Take Two**

*This is the abridged set of the instructions. It assumes you have most of the common OSX developer tools installed like brew and pip.
If you don't know what Brew or Pip are you probably want to use the instructions above. For OSX Lion make sure you install Mercurial (aka hg - brew install hg). There may be errors in pygame associated with not installing X11,
if you encounter this problem please submit an issue on github.*

Before you begin installing SimpleCV make sure you have the folliwng tools installed.

* Install Xcode https://developer.apple.com/xcode/ and then run the Xcode installer.
* Install homebrew https://github.com/mxcl/homebrew/wiki/installation


Commands (for Lion)::

    mkdir ~/Code
    cd ~/Code
    /usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/gist/323731)"
    brew tap homebrew/science
	brew install opencv
    brew install git
    brew tap homebrew/headonly
    brew install --HEAD smpeg
    brew install sdl sdl_image sdl_mixer sdl_ttf portmidi
    ARCHFLAGS="-arch i386 -arch x86_64" brew install PIL
    ln -s /usr/local/lib/python2.7/site-packages/cv.so /Library/Python/2.7/site-packages/cv.so
    sudo ln -s /usr/local/lib/python2.7/site-packages/PIL /Library/Python/2.7/site-packages/PIL
    sudo ln -s /usr/local/lib/python2.7/site-packages/cv2.so /Library/Python/2.7/site-packages/cv2.so
    sudo ln -s /usr/local/lib/python2.7/site-packages/cv.py /Library/Python/2.7/site-packages/cv.py
    sudo easy_install pip
    brew install hg
    sudo pip install hg+http://bitbucket.org/pygame/pygame
    curl -sO https://raw.github.com/fonnesbeck/ScipySuperpack/master/install_superpack.sh && source install_superpack.sh
    pip install https://github.com/sightmachine/SimpleCV/zipball/master

Commands (for Snow Leopard)::

    mkdir ~/Code
    cd ~/Code
    ruby <(curl -fsSkL raw.github.com/mxcl/homebrew/go)
    brew tap homebrew/science
	brew install opencv
    brew install git
    brew install sdl sdl_image sdl_mixer sdl_ttf smpeg portmidi
    ARCHFLAGS="-arch i386 -arch x86_64" brew install PIL
    ln -s /usr/local/lib/python2.6/site-packages/cv.so /Library/Python/2.6/site-packages/cv.so
    sudo ln -s /usr/local/lib/python2.6/site-packages/PIL /Library/Python/2.6/site-packages/PIL
    sudo ln -s /usr/local/lib/python2.6/site-packages/cv2.so /Library/Python/2.6/site-packages/cv2.so
    sudo ln -s /usr/local/lib/python2.6/site-packages/cv.py /Library/Python/2.6/site-packages/cv.py
    sudo easy_install pip
    brew install hg
    sudo pip install https://bitbucket.org/pygame/pygame/get/6625feb3fc7f.zip
    curl -sO https://raw.github.com/fonnesbeck/ScipySuperpack/master/install_superpack.sh | source install_superpack.sh
    pip install https://github.com/sightmachine/SimpleCV/zipball/master


<a id="windows"></a>
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
    pip install https://github.com/sightmachine/SimpleCV/zipball/1.3

###Windows 8
 Step 1
 ------

http://www.simplecv.org/download  => Go to this page and download SimpleCV latest stable version Superpack . It will start downloading a file named SimpleCV-(version).msi .
This file will be around 192mb .

Step 2
 ------

After Downloading run the file . It will start an installation window along with a command prompt window. Give yes permission and press next . First it will install python 2.7.3 .
Then it will install numpy,scipy,Pygame,openCV and now all the normal installation windows will be closed and still there will be command prompt running . Leave it as such it will
download some other file like cython and when it is finished commandpromt will display a success message "SimpleCV installed successfully" "press any button in 10sec or will close
automatically " . Now just press any button or wait for the count down .

 Step 3
 ------

 This is the final step and here we are confirming our SimpleCV installation. To do this open Python IDLE . Type in any of these two commands :

      >>from SimpleCV import *
             or
      >>import SimpleCV

If this two commands works fine without any errors our installation was successfull. If some error occurs we should uninstall and restart or check
some forums.

NOTE:- If this error is shown: "AttributeError: 'module' object has no attribute 'csgraph_to_masked'  " . Before this they will be showing list of paths of scipy library .
The solution for this is to install latest stable version of scipy for windows . www.scipy.org/Download  => we can download latest stable version of scipy for windows here.



<a id="rasppi"></a>
#### RASPBERRY PI

* [Installation instructions can be found here.](https://github.com/sightmachine/SimpleCV/blob/develop/doc/HOWTO-Install%20on%20RaspberryPi.rst)

---------------------------
<a id="shell"></a>
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


to install ipython notebooks run the following:

	sudo pip install tornado
  sudo pip install pyzmq




---------------------------
<a id="videos"></a>
## Videos - Tutorials and Demos

Video tutorials and demos can be found at:
<http://www.simplecv.org/learn/>

---------------------------
<a id="mobile"></a>
## SimpleCV on Mobile (Android)

SimpleCV can in fact be used on a mobile device.  Although the processing requires a server to be setup that runs SimpleCV our 2012 Google Summer of Code
student had built, we have forked the project and instructions on how to set it up and run it can be found at:
<https://github.com/sightmachine/simplecv-mobile-camera>



-------------------------------
<a id="help"></a>
## Getting Help

You can always head over to the SimpleCV help forums to ask questions:
(SimpleCV Help Forums) - <http://help.simplecv.org>

--------------------
<a id="troubleshoot"></a>
## Troubleshooting installation problems.

If for some reason the standard installation methods do not work you may have to manually install some or all of the dependencies required by SimpleCV.

<a id="requirements"></a>
### Required Libraries
The installation instructions below should explain more on how to install.  They can also be installed manually.

* Python 2.6+ (<http://www.python.org>)
* SciPy (<http://www.scipy.org>)
* NumPy (<http://numpy.scipy.org>)
* Pygame (<http://www.pygame.org>)
* OpenCV 2.3+ (<http://opencv.org>)
* IPython 10+ (<http://ipython.org>)
* PIL 1.1.7+ (<http://www.pythonware.com/products/pil/>)

<a id="optional"></a>
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
* scikit-learn




