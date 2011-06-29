#!/usr/bin/python 

import time, webbrowser
from SimpleCV import *

#create JPEG streamers
js = JpegStreamer(8080)
cam = Camera(1)

cam.getImage().save(js)
webbrowser.open("http://localhost:8080", 2)

while (1):
  i = cam.getImage()
  i.colorDistance(i[300,200]).save()
  
  time.sleep(0.01) #yield to the webserver
