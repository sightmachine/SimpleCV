#!/usr/bin/python
'''
This program is basically the hello world in SimpleCV
all it does is grab an image from the camera and display it
'''
from __future__ import print_function
print(__doc__)

from SimpleCV import *
cam = Camera()

while True:
    img = cam.getImage()
    img.show()
