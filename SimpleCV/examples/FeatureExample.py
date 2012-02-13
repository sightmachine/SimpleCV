#!/usr/bin/python 
import time
from SimpleCV import Color, ColorCurve, Camera, Image, pg, np, cv
from SimpleCV.Display import Display
cam = Camera(1)
time.sleep(.1) # uhg
display = Display((800,600))
got_img = False
tl= None
br= None 
template = None
quality = 400.00
minDist = 0.25
minMatch = 0.2
while( display.isNotDone() ):
    img = cam.getImage().scale(0.5)
    #display.checkEvents()
    if( not got_img ):
        if( tl is None ):
            tl = display.leftButtonDownPosition()
        br = display.leftButtonUpPosition()
        if( br is not None and tl is not None):
            x,y,w,h = display.pointsToBoundingBox(tl,br)
            template = img.crop(x,y,w,h)
            got_img = True
        elif(br is None and tl is not None):
                temp = (display.mouseX,display.mouseY)
                if( temp != tl ):
                    x,y,w,h = display.pointsToBoundingBox(temp,tl)
                    img.drawRectangle(x,y,w,h)

    else:
        dummy = display.rightButtonDownPosition()
        if(dummy is not None):
            tl = None
            br = None
            got_img = False
        kp = img.findKeypointMatch(template,quality,minDist,minMatch)
        if( kp is not None):
            kp[0].draw(width=4)
            img = img.applyLayers()
        
        
        img = img.drawKeypointMatches(template)    

    img = img.applyLayers()
    img = img.resize(800,600)
    display.writeFrame(img,fit=False)
    img.save(display)
    time.sleep(0.001)
