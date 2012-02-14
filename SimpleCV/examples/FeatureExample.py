#!/usr/bin/python 
import time
from SimpleCV import Color, Image, np, Camera
from SimpleCV.Display import Display
cam = Camera(1)
time.sleep(.1) # grab our camera
display = Display((800,600)) # create our display
got_img = False
tl= None # our conrners for the template
br= None 
template = None
quality = 400.00
minDist = 0.25
minMatch = 0.2
while( display.isNotDone() ):
    img = cam.getImage().scale(0.5) # get the image
    if( not got_img ): # wait for the user to select a template
        if( tl is None ):  #get the left corner
            tl = display.leftButtonDownPosition()
        br = display.leftButtonUpPosition() # check for the user to finish drawing
        if( br is not None and tl is not None): # grab the template
            x,y,w,h = display.pointsToBoundingBox(tl,br)
            template = img.crop(x,y,w,h)
            got_img = True
        elif(br is None and tl is not None): #otherwise draw the box outline
                temp = (display.mouseX,display.mouseY)
                if( temp != tl ):
                    x,y,w,h = display.pointsToBoundingBox(temp,tl)
                    img.drawRectangle(x,y,w,h)

    else: # if the user right clicks reset
        dummy = display.rightButtonDownPosition()
        if(dummy is not None):
            tl = None
            br = None
            got_img = False
        # otherwise find the keypoint matches
        kp = img.findKeypointMatch(template,quality,minDist,minMatch)
        if( kp is not None): # if we get a match - draw the bounding box
            kp[0].draw(width=4)
            img = img.applyLayers()
        img = img.drawKeypointMatches(template)   # draw the keypoint layers
    img = img.applyLayers() # apply the layers before resize
    img = img.resize(800,600) # resize the image to fit the display
    display.writeFrame(img,fit=False)# draw the display
    time.sleep(0.001)
