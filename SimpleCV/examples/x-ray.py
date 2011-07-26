#!/usr/bin/python 

import time
from SimpleCV import *
from SimpleCV.Display import Display, pg

display_width = 640
display_height = 480
display = Display(resolution = (display_width, display_height)) #create a new display to draw images on
cam = Camera() #initialize the camera
done = False # setup boolean to stop the program

# Loop until not needed
while not display.isDone():
    image = cam.getImage().flipHorizontal()
    crop_width = 200 #set the width of the crop window
    crop_height = 200 #set the height of the crop window
    crop_x = display.mouseX * image.width / display_width #set the x location to scale
    crop_y = display.mouseY * image.height / display_height #set the y location to scale

    if(display.mouseX <= 1): #mouse outside the left of the screen
        crop_x = 1
    if(display.mouseY <= 1): #mouse outside the top of the screen
        crop_y = 1
    if(display.mouseX + crop_width >= display_width): #region outside the right side of the screen
        crop_x = (display_width - crop_width)
    if(display.mouseY + crop_height >= display_height): #region below the bottom of the screen
        crop_y = (display_height - crop_height)

    cropped_image = image.crop(crop_x, crop_y, crop_width, crop_height) #crop out the section of image we want
    xray_image = cropped_image.edges().smooth() #get the edges of cropped region
    image.getDrawingLayer().blit(xray_image, (crop_x, crop_y)) #draw the cropped image onto the current image

    image.save(display)
    time.sleep(0.01) # Let the program sleep for 1 millisecond so the computer can do other things

