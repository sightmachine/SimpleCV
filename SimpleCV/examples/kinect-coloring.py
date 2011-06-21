#!/usr/bin/python 

import time, webbrowser
from operator import add
from SimpleCV import *

#vs = VideoStream("foo.avi")
vs = JpegStreamer()
#create JPEG streamers

cam = Kinect()
#initialize the camera

cam.getDepth().save(vs)
webbrowser.open(vs.url())

compositeframe = Image(cam.getImage().getEmpty())
cv.Rectangle(compositeframe.getBitmap(), (0,0), (compositeframe.width-1, compositeframe.height-1), (0,0,0))
offtime = 3.0
paintstate = False
laststroke = time.time()


while (1):
  depth = cam.getDepth().invert().binarize(100)
  
  if np.average(depth.getMatrix()) > 1:
    paintstate = True
    laststroke = time.time()
    compositeframe = compositeframe + depth
  else:
    paintstate = False
    if (time.time() - laststroke > offtime):
      compositeframe = Image(cam.getImage().getEmpty())
      cv.Rectangle(compositeframe.getBitmap(), (0,0), (compositeframe.width-1, compositeframe.height-1), (0,0,0))

      
  
  ((cam.getImage() - compositeframe) + compositeframe.splitChannels(False)[0]).save(vs)
  time.sleep(0.01) #yield to the webserver
