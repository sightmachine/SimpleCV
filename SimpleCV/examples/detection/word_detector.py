'''
This example reads in the file name of an image. 

It will display any words that are found in the image.

Note: an OCR library needs to be installed.

'''

print __doc__

import os, sys, pickle
from SimpleCV import *
from nose.tools import with_setup, nottest

img = Image("hello.jpg")

foundtext = img.readText() 

img.show()
print "The picture says:"
print foundtext