#!/usr/bin/python 

import time, webbrowser
from SimpleCV import *

#create JPEG streamers
js = JpegStreamer(8080)
cam = Camera(threaded=false)

cam.getImage().save(js)
webbrowser.open("http://localhost:8080", 2)

while (1):
  i = cam.getImage()
  i.save(js)
  time.sleep(0.01) #yield to the webserver
