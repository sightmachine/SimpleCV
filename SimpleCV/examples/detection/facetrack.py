#!/usr/bin/python
'''
This program basically does face detection an blurs the face out
'''
print __doc__

import time
from SimpleCV import *

cam = Camera() #initialize the camera

haarcascade = HaarCascade("face")
# Loop forever
while True:
    image = cam.getImage().flipHorizontal().scale(0.5)# get image, flip it so it looks mirrored, scale to speed things up
    faces = image.findHaarFeatures(haarcascade) # load in trained face file
    if faces:
        bb = faces[-1].boundingBox()
        image = image.pixelize(10,region=(bb[0],bb[1],bb[2],bb[3]))
    image.show() #display the image

