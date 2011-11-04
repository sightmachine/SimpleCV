#!/usr/bin/python 

import time, webbrowser
from SimpleCV import *

#create JPEG streamers
js = JpegStreamer(8080)
cam = Kinect()

cam.getDepth().save(js)
webbrowser.open("http://localhost:8080", 2)

while (1):
  d = cam.getDepth().edges()
  i = cam.getImage()
  i = d + i 
  i.save(js)
  time.sleep(0.01) #yield to the webserver
