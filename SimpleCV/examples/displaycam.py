#!/usr/bin/python 

import time
from SimpleCV import *
from SimpleCV.Display import Display, pg

#create JPEG streamers
  
d = Display()
cam = Camera()
done = False


while not d.isDone():
  cam.getImage().flipHorizontal().save(d)
  time.sleep(0.01)