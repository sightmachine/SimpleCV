#!/usr/bin/python 

import time
from SimpleCV import *
from SimpleCV.Display import Display, pg

#create JPEG streamers
d = Display(flags = 0)
cam = Camera()

while (1):
  d.writeFrame(cam.getImage().edges().flipHorizontal())
  time.sleep(0.01)
