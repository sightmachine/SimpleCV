#!/usr/bin/env python
# 
# Released under the BSD license. See LICENSE file for details.
"""
This program basically overlays an edge detector window that gives the
illusion of X-ray vision.  It is mearly meant to show how to perform a
basic image operation and overlay back onto the original image.
"""
print __doc__

from SimpleCV import Camera, Display

# Initialize the camera
cam = Camera() 

# Set the default size of the output window
display_width = 640
display_height = 480
# Create a new display to draw images on
display = Display(resolution = (display_width, display_height)) 

# Set the width and the height of the crop window
crop_width = 200
crop_height = 200

# Loop forever
while display.isNotDone():
    # Grab image from camera and flip it
    img = cam.getImage().flipHorizontal()
    # Set the x and the y location to scale
    crop_x = display.mouseX * img.width / display_width 
    crop_y = display.mouseY * img.height / display_height
    # Mouse outside the left or the top of the screen
    if(display.mouseX <= 1): 
        crop_x = 1
    if(display.mouseY <= 1):
        crop_y = 1
    # Region outside the right side or below the bottom of the screen
    if(display.mouseX + crop_width >= display_width):
        crop_x = (display_width - crop_width)
    if(display.mouseY + crop_height >= display_height):
        crop_y = (display_height - crop_height)
    # Crop out the section of image we want
    cropped_img = img.crop(crop_x, crop_y, crop_width, crop_height)
    # Get the edges of cropped region 
    xray_img = cropped_img.edges().smooth()
    # Draw the cropped image onto the current image
    img.getDrawingLayer().blit(xray_img, (crop_x, crop_y))
    # Display the image
    img.save(display)
