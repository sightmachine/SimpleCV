#!/usr/bin/python 
import time
from SimpleCV import *

#create JPEG streamers
cam = Camera()

while (1):
  i = cam.getImage()
  i.show()
  time.sleep(0.01) #yield to the webserver
