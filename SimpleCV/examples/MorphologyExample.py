#!/usr/bin/python
#
# This example rotates through a few of the image morphology examples
#
from SimpleCV import *
from numpy import linspace 
from scipy.interpolate import UnivariateSpline
import sys, time, socket
import time
from SimpleCV import *
from SimpleCV.Display import Display, pg

display = Display(resolution = (800, 600)) #create a new display to draw images on
cam = Camera() #initialize the camera
done = False # setup boolean to stop the program
max_threshold = 1 # this is used for the edge detection
threshold_step = 1 # this is the amount to adjust the threshold by each time the display is updated
threshold = max_threshold
example = 1

# Loop until not needed
while not display.isDone():
    image = cam.getImage() # get image (or frame) from camera
    flipped_image = image.flipHorizontal() # flip it so it looks mirrored

    print threshold
    # This just automatically cycles through threshold levels
    if(threshold >= 20):
        threshold = max_threshold
        if(example >= 4):
		        example = 1
        else:
		        example = example + 1

    else:
        threshold = threshold + threshold_step


    if(example == 1):
        image = image.erode(threshold)
        text = "Erode Morphology Example: img.erode(" + str(threshold) + ")"
        image.drawText(text)
		    
    elif(example == 2):
        image = image.dilate(threshold)
        text = "Dilate Morphology Example: img.dilate(" + str(threshold) + ")"
        image.drawText(text)
		    
    elif(example == 3):
        image = image.morphOpen()
        text = "Open Morphology Example: img.morphOpen()"
        image.drawText(text)
    
    elif(example == 4):
        image = image.morphClose()
        text = "Close Morphology Example: img.morphClose()"
        image.drawText(text)
    
    elif(example == 5):
        image = image.morphGradient()
        text = "Gradient Morphology Example: img.morphGradient()"
        image.drawText(text)
		
    image.save(display)
    time.sleep(0.1) # Let the program sleep for 1 millisecond so the computer can do other things
    if display.mouseLeft:
		    display.done = True #if the left arrow is pressed, close the program


