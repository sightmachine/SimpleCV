+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
HOWTO install SimpleCV on the BeagleBone
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

======================================
==      With SimpleCV Disk Img      ==
======================================

1) Download the image

user@machine:~$ wget http://url_to_sourceforge/

2) Transfer image to disk (replace /dev/sdb with your card name):

user@machine:~$ zcat ubuntu_12.04_simplecv_beaglebone.image.gz | sudo dd bs=1M of=/dev/sdb

======================================
==    Without SimpleCV Disk Img     ==
======================================

1) Install necessary tools for building and transferring.

user@machine:~$ sudo apt-get install uboot-mkimage wget pv dosfstools btrfs-tools parted

2) Insert the SD / MMS card and unmount from the file system.

user@machine:~$ unmount /dev/db1
              $ unmount /dev/db2

3) Download the preconfigured Ubuntu 12.04 image, and uncompress it.

user@machine:~$ wget http://rcn-ee.net/deb/rootfs/precise/ubuntu-12.04-r1-minimal-armhf.tar.xz
              $ tar xf ubuntu-12.04-r1-minimal-armhf.tar.xz
              $ cd ubuntu-12.04-r1-minimal-armhf

4) Run the installation script provided and wait for it to complete
   (replace /dev/sdb with your card name).

user@machine:~$ sudo ./setup_sdcard.sh --mmc /dev/sdb --uboot "bone"

======================================
==        After Booting Board       ==
======================================

1) After transfer completes, insert sd card and power up beaglebone.
   Wait about one minute for the board to boot up, and login to the shell.

user@machine:~$ screen /dev/ttyUSB0 115200

2) Device may or may not prompt for username. After shell is connected,
   type in "ubuntu" for the username and press return. The board will
   prompt for password, type "temppwd".

3) You are now logged in to the board. The next step is to get connected
   to the ethernet. Connect your BeagleBone to a router via ethernet. Next
   we need to edit the network configuration files. Replace addresses as 
   necessary

ubuntu@omap:~$ sudo nano /etc/network/interfaces

  auto lo
  iface lo inet loopback

  # The primary network interface
  # modify "address" and "gateway"
  # as necessary.

  auto eth0
  iface eth0 inet static
  address 10.0.0.110 
  netmask 255.255.255.0
  gateway 10.0.0.1

ubuntu@omap:~$ sudo nano /etc/resolvconf/resolv.conf.d/tail

  domain localdomain
  search localdomain
  nameserver 10.0.0.1

4) Restart the networking service for the changes to take effect.

ubuntu@omap:~$ sudo /etc/init.d/networking restart

5) Ping Google to make sure internet is alive. Verify that you get a response
   from the server and the packets do not fail to send.

ubuntu@omap:~$ ping www.google.com

6) The disk image provided already has SimpleCV installed, but in the event of 
   an installation from scratch, run the following commands.

ubuntu@omap:~$ sudo apt-get update
             $ sudo apt-get install ipython python-opencv python-scipy python-numpy python-pygame python-setuptools python-pip
             $ sudo pip install https://github.com/ingenuitas/SimpleCV/zipball/master

7) After allowing those commands to run for a while (it is going to take a while, go
   grab a drink), SimpleCV should be all set up. Connect a compatible camera to the
   board's usb input and open up the simplecv shell

ubuntu@omap:~$ simplecv

SimpleCV:1> c = Camera()
VIDIOC_QUERYMENU: Invalid argument
VIDIOC_QUERYMENU: Invalid argument
VIDIOC_QUERYMENU: Invalid argument
VIDIOC_QUERYMENU: Invalid argument
VIDIOC_QUERYMENU: Invalid argument
VIDIOC_QUERYMENU: Invalid argument
VIDIOC_QUERYMENU: Invalid argument

SimpleCV:2> c.getImage()
SimpleCV:2: <SimpleCV.Image Object size:(640, 480), filename: (None), at memory location: (0x1335850)>\

SimpleCV:3> exit()

8) Congratulations, BeagleBone is now running SimpleCV!



