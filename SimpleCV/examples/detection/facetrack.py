#!/usr/bin/python 
import time
from SimpleCV import *

cam = Camera() #initialize the camera

hc = HaarCascade("../../Features/HaarCascades/face.xml")
# Loop forever
while True:
    image = cam.getImage().flipHorizontal().scale(320, 240) # get image, flip it so it looks mirrored, scale to speed things up
    faces = image.findHaarFeatures(hc) # load in trained face file
    if faces:
        bb = faces[-1].boundingBox()
        image = image.pixelize(10,region=(bb[0],bb[1],bb[2],bb[3]))
    image.show() #display the image
    time.sleep(0.01) # Let the program sleep for 1 millisecond so the computer can do other things
