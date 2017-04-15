#!/usr/bin/env python
# 
# Released under the BSD license. See LICENSE file for details.
"""
This script detects a face in images and draw a frame around them. Press the
right mouse button to save the current face image.
"""
print __doc__

import datetime
import os
from SimpleCV import Camera, Display, HaarCascade

# Initialize the camera
cam = Camera(1)

# Initialize the display
display = Display()

# Use haar cascader to detect a face
haarcascade = HaarCascade("face")

# Create a directory for storing the images
folder = datetime.datetime.now().strftime("%Y%m%d")
if not os.path.exists(folder):
    os.mkdir(folder)

# Loop forever
while not display.isDone():
    # Get image, flip it so it looks mirrored, and scale it down to 0.5
    img = cam.getImage().flipHorizontal().scale(0.5)
    # Load in trained face file
    faces = img.findHaarFeatures(haarcascade)
    # Check for faces and add a frame for each one
    if faces:
        faces.draw(color=(0, 0, 255), width=2)
        face = faces[-1]
        # Crop out the face
        cropped_img = face.crop()
        # Show the face as small overlay
        face_image = cropped_img.resize(h=80)
        # Draw this image with the face onto the current image
        img.getDrawingLayer().blit(face_image, (5, 5))
    # Display the image
    img.save(display)

    # Save last face on mouse click with a timestamp
    if display.mouseRight:
        print "Image of face saved: face-%s.png" \
                % datetime.datetime.now().strftime("%H-%M-%S")
        cropped_img.save(folder + "/face-%s.png" \
                % datetime.datetime.now().strftime("%H-%M-%S"))
