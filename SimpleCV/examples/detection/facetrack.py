#!/usr/bin/env python
# 
# Released under the BSD license. See LICENSE file for details.
"""
This program basically does face detection an blurs the face out.
"""
print __doc__

from SimpleCV import Camera, Display, HaarCascade

# Initialize the camera
cam = Camera()

# Create the display to show the image
display = Display()

# Haar Cascade face detection, only faces
haarcascade = HaarCascade("face")

# Loop forever
while display.isNotDone():
    # Get image, flip it so it looks mirrored, scale to speed things up
    img = cam.getImage().flipHorizontal().scale(0.5)
    # Load in trained face file
    faces = img.findHaarFeatures(haarcascade)
    # Pixelize the detected face
    if faces:
        bb = faces[-1].boundingBox()
        img = img.pixelize(10, region=(bb[0], bb[1], bb[2], bb[3]))
    # Display the image
    img.save(display)
