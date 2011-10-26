#!/usr/bin/python
#
# This example just takes an image, finds the edges, and draws them
# the threshold is used for the edge detection, if you adjust the
# max_threshold and threshhold_step values and run the program you will
# see it change over time
#

import time
from SimpleCV import *
from SimpleCV.Display import Display, pg

cam = Camera() #initialize the camera
done = False # setup boolean to stop the program
max_threshold = 500 # this is used for the edge detection
threshold_step = 0.5 # this is the amount to adjust the threshold by each time the display is updated
threshold = max_threshold
running = True

# Loop until not needed
while running:
    image = cam.getImage() # get image (or frame) from camera
    flipped_image = image.flipHorizontal() # flip it so it looks mirrored
    edged_image = flipped_image.edges(threshold) # get the image edges

    # This just automatically cycles through threshold levels
    if(threshold <= 0):
        threshold = max_threshold

    else:
        threshold = threshold - 0.5

    edged_image.drawText("Current Edge Threshold:" + str(threshold), 10,10, fontsize=20, color=Color.GREEN)

    edged_image.show()
