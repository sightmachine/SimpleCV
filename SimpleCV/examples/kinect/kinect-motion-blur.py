#!/usr/bin/python

from operator import add
from SimpleCV import * 
from SimpleCV.Display import Display

d = Display(flags = pg.FULLSCREEN)
#create video streams

cam = Kinect()
#initialize the camera
frames_to_blur = 4
frames = ImageSet()

depth = cam.getDepth().stretch(0,200)
while True:
   new_depth = cam.getDepth().stretch(0,200)
   img = cam.getImage()
   diff_1 = new_depth - depth
   diff_2 = depth - new_depth
   diff = diff_1 + diff_2
   img_filter = diff.binarize(0)

   motion_img = img - img_filter 
   motion_img_open = motion_img.morphOpen()
   
   frames.append(motion_img_open)
   if len(frames) > frames_to_blur:
      frames.pop(0)

   pic = reduce(add, [i / float(len(frames)) for i in frames])
   pic.show() 
   depth = new_depth
