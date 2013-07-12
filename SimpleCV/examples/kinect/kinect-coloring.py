#!/usr/bin/python

import time, webbrowser
from operator import add
from SimpleCV import Color, ColorCurve, Kinect, Image, pg, np
from SimpleCV.Display import Display

d = Display(flags = pg.FULLSCREEN)
#create video streams

cam = Kinect()
#initialize the camera

compositeframe = Image((640, 480))
#populate the compositeframe

offtime = 5.0
laststroke = time.time()

while not d.isDone():
    img = cam.getImage()
    imgscene = img.copy()

    depth = cam.getDepth()
    mindepth = np.min(depth.getNumpy())

    if mindepth < 180:
        depthbin = depth.binarize(np.min(depth.getNumpy()) + np.std(depth.getNumpy()) / 4).erode(3)
        #take the front 1/4 stdev of the depth map

        img = img.crop(0,25, 605, 455).scale(640,480)
        #img.dl().blit(img.crop(100, 25, 515, 455), (125,0))
        #this is a bit of a hack to compensate for the offset between cam and depth sensor
        #img = img.applyLayers()
        img = img - depthbin.invert()
        #img.save(d)
        meanred, meangrn, meanblue = img.meanColor()

        if meanred > meanblue and meanred > meangrn:
            depthbin, junk, junk = depthbin.splitChannels(grayscale = False)
        if meanblue > meanred and meanblue > meangrn:
            junk, junk, depthbin = depthbin.splitChannels(grayscale = False)
        if meangrn > meanred and meangrn > meanblue:
            junk, depthbin, junk = depthbin.splitChannels(grayscale = False)

        laststroke = time.time()
        compositeframe = compositeframe + depthbin
        #we're painting -- keep adding to the composite frame

    else:
        if (time.time() - laststroke > offtime):
        #if we're not painting for a certain amount of time, reset
            compositeframe = Image(cam.getImage().getEmpty())

    frame = ((imgscene - compositeframe.binarize(10).invert()) + compositeframe).flipHorizontal()
    #subtract our composite frame from our camera image, then add it back in in red. False = Show red channel as red, [0] = first (red) channel
    frame.save(d) #show in browser
    if d.mouseLeft:
        d.done = True
        pg.quit()

    time.sleep(0.01) #yield to the webserver
