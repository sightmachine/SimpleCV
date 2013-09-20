Installing SimpleCV on the Raspberry Pi
=======================================

1) Power up the raspberry pi and log in. Connect the 
   board to ethernet.

::

	Username: pi
	Password: raspberry

2) Network should be up and running with dhcp, if not
   you must manually configure the network settings.

3) Run the following command to install the necessary dependancies

::

	sudo apt-get install ipython python-opencv python-scipy python-numpy python-setuptools python-pip

4) SimpleCV should now be ready to install. Download SimpleCV from github 
   and install from the source.

::

	sudo pip install https://github.com/sightmachine/SimpleCV/zipball/master

Alternatively, you can install SimpleCV from source.

::

	mkdir ~/Code
	cd ~/Code
	git clone git://github.com/sightmachine/SimpleCV.git
	cd SimpleCV
	sudo pip install -r requirements.txt
	sudo python setup.py develop
	
5) After allowing those commands to run for a while (it is going to take a while, go
   grab a drink), SimpleCV should be all set up. Connect a compatible camera to the
   board's usb input and open up the simplecv shell

::

	raspberry@pi:~$ simplecv

	SimpleCV:1> c = Camera()
	VIDIOC_QUERYMENU: Invalid argument
	VIDIOC_QUERYMENU: Invalid argument
	VIDIOC_QUERYMENU: Invalid argument
	VIDIOC_QUERYMENU: Invalid argument
	VIDIOC_QUERYMENU: Invalid argument
	VIDIOC_QUERYMENU: Invalid argument
	VIDIOC_QUERYMENU: Invalid argument

	SimpleCV:2> c.getImage()
	SimpleCV:2: <SimpleCV.Image Object size:(640, 480), filename: (None), at memory location: (0x1335850)>

	SimpleCV:3> exit()

6) Congratulations, your RaspberryPi is now running SimpleCV!
