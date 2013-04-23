'''
A Simple program in python for motion detection and drawing lines over the moving Object.
Here we accepts two images of different time and substract them . The Sucbstracted Image
Holds The Key . The image show the object in motion everything else is substracted off.
Lines are found on substracted Image and drawn to the normal image.
'''

from SimpleCV import *
from SimpleCV import Camera

cam = Camera()
while True:
        first = cam.getImage()   #getting First Image 
        second = cam.getImage()  #getting Second Image 
        diff = second-first           #substracting Second Image from First and stored in diff
        lines = diff.findLines(threshold=10, minlinelength=15)   #finding Lines in the Differenced image .
        lines.draw(width=3)                                                 #drawing Lines on the Diff image
        second.addDrawingLayer(diff.dl())                           #Drawing the lines to normal image .
        second.show()

