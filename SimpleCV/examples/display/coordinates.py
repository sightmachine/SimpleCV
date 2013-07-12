#!/usr/bin/env python
# 
# Released under the BSD license. See LICENSE file for details.
"""
This script let you move two forms around an image with your mouse and gives
you back the coordinates of the center.
"""
print __doc__

from SimpleCV import Camera, Display, Color

# Initialize the camera
cam = Camera()

# Initialize the display
display = Display()

# Define center points from the camera properties (must be int)
cpCircle = (int(cam.getProperty("width")) / 2,
            int(cam.getProperty("height")) / 2
           )
cpRectangle = cpCircle

# Loop forever
while display.isNotDone():
    # Grab image from camera
    img = cam.getImage()

    # Add text
    img.drawText('Move the circle with left mouse button', 15, 15,
                 Color.RED)
    img.drawText('Move the rectangle with right mouse button', 15, 30,
                 Color.GREEN)

    # Action for left Mouse button
    if display.leftButtonDown:
        # Get the coordinates of the mouse pointer as center point
        cpCircle = display.leftButtonDownPosition()
    # Move the circle to the clicked position and draw it 
    img.dl().circle(cpCircle, 20, Color.RED, 3)
    # Displays the coordinates on top of the circle
    img.drawText('%s, %s' % (cpCircle[0], cpCircle[1]), cpCircle[0],
                             cpCircle[1] - 35, Color.RED)

    # Action for right mouse button
    if display.rightButtonDown:
        cpRectangle = display.rightButtonDownPosition()
    img.dl().centeredRectangle(cpRectangle, (80, 40), Color.GREEN, 3)
    img.drawText('%s, %s' % (cpRectangle[0], cpRectangle[1]), cpRectangle[0],
                             cpRectangle[1] - 35, Color.GREEN)

    # Show the output
    img.save(display)
