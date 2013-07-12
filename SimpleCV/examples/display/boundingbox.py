#!/usr/bin/env python
# 
# Released under the BSD license. See LICENSE file for details.
"""
This script let you draw a bounding box on an image with your mouse. This is
only a show case meaning that there is no checking if your bounding box is
outside the available area.
"""
print __doc__

from SimpleCV import Camera, Display, Color

# Initialize the camera
cam = Camera()

# Initialize the display
display = Display()

# Biggest possible bounding box
down = (0, 0)
up = (int(cam.getProperty("height")), int(cam.getProperty("width")))

# Loop forever
while display.isNotDone():
    # Grab image from camera
    img = cam.getImage()

    # Action for mouse down and up
    if display.leftButtonDown:
        # Get the coordinates of the mouse pointer as position
        down = display.leftButtonDownPosition()
        # Set the up position to the same value as the down position while
        # drawing.
        up = down
    if display.leftButtonUp:
        # Get the coordinates of the mouse pointer
        up = display.leftButtonUpPosition()

    # Reset with right mouse button
    if display.rightButtonDown:
        # Delete the coordinates and go on with full image
        down = (0, 0)
        up = (int(cam.getProperty("height")), int(cam.getProperty("width")))

    # If the up and the down position are equal, go on with a default
    # rectangle of 160 x 120
    if (down == up):
        img.getDrawingLayer().centeredRectangle(down, (160, 120), Color.GREEN, 3)
        x = down[0] - 60
        y = down[1] - 80
        h = 120
        w = 160
    else:
    # Draw the box according the mouse clicks
        bbox = display.pointsToBoundingBox(up, down)
        x = bbox[0]
        y = bbox[1]
        h = bbox[2]
        w = bbox[3]
        img.drawRectangle(x, y, w, h, Color.RED, 3)

    #print "x: %i, y: %i, w: %s, h: %i" % (x, y, w, h)
    # Crop the bounding box
    cropImg = img.crop(x, y, w, h)
    # Show the cropped image as small overlay
    area_image = cropImg.resize(160, 120)
    # Draw this image onto the current image
    img.getDrawingLayer().blit(area_image, (5, 5))

    # Show the output
    img.save(display)
