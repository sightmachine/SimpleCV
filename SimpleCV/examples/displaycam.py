#!/usr/bin/python 

import time
from SimpleCV import *
from SimpleCV.Display import Display, pg

display = Display(resolution = (800, 600)) #create a new display to draw images on
cam = Camera() #initialize the camera
done = False # setup boolean to stop the program

lasttime = time.time() # add a timer for the thread to sleep

# Loop until not needed
while not display.isDone():
    cam.getImage().flipHorizontal().save(display) # get image, flip it so it looks mirrored, save to display
    time.sleep(0.01) # Let the program sleep for 1 millisecond so the computer can do other things
    if display.mouseLeft:
        display.done = True #if the left arrow is pressed, close the program
