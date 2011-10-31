#!/usr/bin/python 
import sys, time, socket
from SimpleCV import *
#setup the camera
cam = Camera()

#settings for the project
min_size = 0.1*cam.getProperty("width")*cam.getProperty("height") #Change threshold
thresh = 10 # frme diff threshold

lastImg = cam.getImage();
lastImg.drawText("Move around to get the party started!", 5,5, fontsize=12)
lastImg.show()
while(True):
  newImg = cam.getImage()
  trackImg = newImg - lastImg # diff the images
  blobs =  trackImg.findBlobs(-1, threshblocksize=99) #use adapative blob detection
  if blobs:
      blobs.draw(autocolor=True)
      trackImg.show()
  lastImg = newImg # update the image
  time.sleep(0.01);

