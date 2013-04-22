'''
This is how to track a white ball example using SimpleCV

The parameters may need to be adjusted to match the RGB color
of your object.

The demo video can be found at:

'''
print __doc__

import SimpleCV

display = SimpleCV.Display() #create the display to show the image
cam = SimpleCV.Camera() # initalize the camera
normaldisplay = True # mode toggle for segment detection and display

while display.isNotDone(): # loop until we tell the program to stop

    if display.mouseRight: # if right mouse clicked, change mode
        normaldisplay = not(normaldisplay)
        print "Display Mode:", "Normal" if normaldisplay else "Segmented"

    img = cam.getImage().flipHorizontal() # grab image from camera
    dist = img.colorDistance(SimpleCV.Color.BLACK).dilate(2) # try to separate colors in image
    segmented = dist.stretch(200,255) # really try to push out white colors
    blobs = segmented.findBlobs() # search the image for blob objects
    if blobs: # if blobs are found
        circles = blobs.filter([b.isCircle(0.2) for b in blobs]) # filter out only circle shaped blobs
        if circles:
            img.drawCircle((circles[-1].x, circles[-1].y), circles[-1].radius(),SimpleCV.Color.BLUE,3) # draw the circle on the main image

    if normaldisplay: # if normal display mode
        img.show()
    else: # segmented mode
        segmented.show()
