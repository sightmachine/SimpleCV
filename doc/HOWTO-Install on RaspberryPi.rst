++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Instructions on how to install SimpleCV on the RaspberryPi
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

======================================
==      With SimpleCV Disk Img      ==
======================================

1) Download the image

	user@machine:~$ wget http://url_to_sourceforge/

2) Transfer image to disk (replace /dev/sdb with your card name):

	user@machine:~$ zcat squeeze_simplecv_pi.image.gz | sudo dd bs=1M of=/dev/sdb

======================================
==    Without SimpleCV Disk Img     ==
======================================

1) Power up the raspberry pi and log in. Connect the 
   board to ethernet.

	Username: pi
	Password: raspberry

2) Network should be up and running with dhcp, if not
   you must manually configure the network settings.

3) There is a firmware update available for the pi, and
   it is necessary for Camera use in SimpleCV.

	Follow instructions at:
	http://blog.pixelami.com/2012/06/raspberry-pi-firmware-update-for-debian-squeeze/

4) We need to build python-pygame from source next. Download the dev tools for
   Python 2.6.

	raspberry@pi:~$ sudo apt-get update
	raspberry@pi:~$ sudo apt-get install libpython2.6 python-dev python2.6-dev build-essential
	raspberry@pi:~$ wget http://www.pygame.org/ftp/pygame-1.8.1release.tar.gz
	raspberry@pi:~$ tar -xvzf pygame-1.8.1release.tar.gz
	raspberry@pi:~$ cd pygame-1.8.1release
	raspberry@pi:~$ ./configure
	raspberry@pi:~$ make
	raspberry@pi:~$ make install

5) SimpleCV should now be ready to install. Download SimpleCV from github 
   and install from the source.

	raspberry@pi:~$ sudo apt-get install ipython python-opencv python-scipy python-numpy python-pygame python-setuptools python-pip
	raspberry@pi:~$ sudo pip install https://github.com/ingenuitas/SimpleCV/zipball/master
	
6) After allowing those commands to run for a while (it is going to take a while, go
   grab a drink), SimpleCV should be all set up. Connect a compatible camera to the
   board's usb input and open up the simplecv shell

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

8) Congratulations, your RaspberryPi is now running SimpleCV!
