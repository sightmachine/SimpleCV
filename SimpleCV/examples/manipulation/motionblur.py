#!/usr/bin/python
'''
This program does basic motion blurring.  It averages the number of
maxframes that are set using some basic image math
'''
print __doc__
from operator import add
from SimpleCV import *

js = JpegStreamer(8080)
#create JPEG streamers

cam = Camera() #initialize the camera

#the number of frames
maxframes = 3
frames = []
frames.append(cam.getImage())
frames[0].show()

while (1):
    frames.append(cam.getImage())
    #add the next frame to the end of the set

    if len(frames) > maxframes:
        frames.pop(0)  #remove the earliest frame if we're at max

    pic = reduce(add, [i / float(len(frames)) for i in frames])
    #add the frames in the array, weighted by 1 / number of frames

    pic.show()
