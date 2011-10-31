#!/usr/bin/python 

import time, webbrowser
from operator import add
from SimpleCV import BlobMaker
from SimpleCV import Color, ColorCurve, Kinect, Image, pg, np
from SimpleCV.Display import Display

d = Display(flags = pg.FULLSCREEN)
#create video streams

cam = Kinect()
#initialize the camera

compositeframe = Image((640, 480))
#populate the compositeframe

offtime = 5.0
laststroke = time.time()
lower = 100
x = -30
y = 12
w = 640
h = 480
bm = BlobMaker()
c = Color.RED
while not d.isDone():
  
  img = cam.getImage()
  img = img.warp([(0-x,0-y),(w-x,0-y),(w-x,h-y),(0-x,h-y)])
  imgscene = img.copy()
  depth = cam.getDepth()
  depth = depth.invert().binarize(thresh=lower).invert()
  #depth = depth.dilate(iterations=3).erode(iterations=3)
  fs = bm.extractFromBinary(depth,img)

   
  depth = depth.invert()+img.invert();
  depth = depth.invert()
  
  for f in fs:
    imgscene.dl().polygon(f.mConvexHull,color=c,width=3)
    #imgscene.dl().polygon(f.mContour,color=Color.HOTPINK,width=3)
  
  imgscene.dl().circle((d.mouseX,d.mouseY),3,color=Color.WHITE,filled=True)
  #imgscene.dl().setFontSize(30)
  #imgscene.dl().text(myStr,location =(40,10),color=Color.HOTPINK)
  imgscene.save(d) #show in browser
  if d.mouseLeft:
      c = Color.BLUE
  if d.mouseRight:
      c = Color.HOTPINK
      
  time.sleep(0.01) #yield to the webserver
  
