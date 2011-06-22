#!/usr/bin/python 

import time, webbrowser
from operator import add
from SimpleCV import *

vs = VideoStream("foo.avi")
js = JpegStreamer()
#create video streams

cam = Kinect()
#initialize the camera

cam.getDepth().save(js)
webbrowser.open(js.url())
#launch the webbrowser

compositeframe = Image(cam.getImage().getEmpty())
#populate the compositeframe

offtime = 3.0
paintstate = False
laststroke = time.time()

while (1):
  depth = cam.getDepth().invert().binarize(100)
  #perform a binary threshold of the inverted depth map
  
  if np.average(depth.getMatrix()) > 1:
    paintstate = True
    laststroke = time.time()
    compositeframe = compositeframe + depth
    #we're painting -- keep adding to the composite frame
  else:
    paintstate = False
    #not painting
    if (time.time() - laststroke > offtime):
      #if we're not painting for a certain amount of time, reset
      compositeframe = Image(cam.getImage().getEmpty())

  frame = ((cam.getImage() - compositeframe) + compositeframe.splitChannels(False)[0]).flipHorizontal()
  #subtract our composite frame from our camera image, then add it back in in red. False = Show red channel as red, [0] = first (red) channel
  frame.save(js) #show in browser
  frame.save(vs) #save in file
  time.sleep(0.01) #yield to the webserver
