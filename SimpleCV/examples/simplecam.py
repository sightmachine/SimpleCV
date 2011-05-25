#!/usr/bin/python 

import sys, time, socket
sys.path.append("..")

from SimpleCV import *


#settings for the project
port_original = 8080  #port to view the camera viwe
port_processed = 8081 #port to look at the processed view

#create JPEG streamers
original_js = JpegStreamer(port_original)
processed_js = JpegStreamer(port_processed)
cam = Camera()


while (1):
  i = cam.getImage()
  i.save(original_js.framebuffer)
  i.save(processed_js.framebuffer)
  time.sleep(0.2) #yield to the webserver
