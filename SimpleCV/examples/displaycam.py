#!/usr/bin/python 

import time
from SimpleCV import *
from SimpleCV.Display import Display, pg

d = Display(resolution = (800, 600))
cam = Camera()
done = False

lasttime = time.time()

while not d.isDone():
    cam.getImage().flipHorizontal().save(d)
    time.sleep(0.01)
    if d.mouseLeft:
      d.done = True
