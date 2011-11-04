#!/usr/bin/python 

import time, webbrowser
from operator import add
from SimpleCV import *

js = JpegStreamer(8080)
#create JPEG streamers

cam = Camera()

#initialize the camera

#the number of frames
maxframes = 3 

frames = []
frames.append(cam.getImage())
frames[0].save(js)
#grab the first frame and put it in the jpegstreamer

webbrowser.open("http://localhost:8080", 2)
#launch the users browser

while (1):
  frames.append(cam.getImage())
  #add the next frame to the end of the set

  if len(frames) > maxframes:
    frames.pop(0)  #remove the earliest frame if we're at max

  pic = reduce(add, [i / float(len(frames)) for i in frames])
  #add the frames in the array, weighted by 1 / number of frames

  pic.save(js)
  #save to the jpeg stream

  time.sleep(0.01) #yield to the webserver
