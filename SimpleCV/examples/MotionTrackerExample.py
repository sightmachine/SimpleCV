#!/usr/bin/python 
import sys, time, socket
from SimpleCV import *


#Create the camera
cam = Camera(threaded=False)

#settings for the project
Warning = "Warning! Warning! Warning Dr. Smith!" #Lost in space reference
min_size = 0.1*cam.getProperty("width")*cam.getProperty("height") #Change threshold
thresh = 10 # frme diff threshold

lastImg = cam.getImage();
count = 0;
while(1):
  newImg = cam.getImage()
  trackImg = newImg-lastImg # diff the images
  blobs =  trackImg.findBlobs(thresh,min_size) #do we have blobs that match our criteria
  if blobs: #if we got blobs
      print Warning  # print the warning
      newImg.save("foobar"+str(count)+".jpg") # save the results
  lastImg = newImg # update the image
  count = count + 1
  time.sleep(0);
  
exit(0)
