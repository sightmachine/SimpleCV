#!/usr/bin/python 

import sys, time, socket
sys.path.append("..")

from SimpleCV import *

#settings for the project
port_original = 8080  #port to view the camera viwe

#create JPEG streamers
original_js = JpegStreamer(port_original)
cam = Camera()


while (1):
  i = cam.getImage()
  i.save(original_js.framebuffer)
  time.sleep(0.01) #yield to the webserver
