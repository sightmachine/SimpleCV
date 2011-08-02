#!/usr/bin/python 
import time
from SimpleCV import *

cam = Camera() #initialize the camera

# Loop forever
while True:
    image = cam.getImage().flipHorizontal().scale(320, 240) # get image, flip it so it looks mirrored, scale to speed things up
    faces = image.findHaarFeatures("facetrack-training.xml") # load in trained face file
    if faces: faces.draw()
    image.show() #display the image
    time.sleep(0.01) # Let the program sleep for 1 millisecond so the computer can do other things
