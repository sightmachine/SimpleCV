#!/usr/bin/python
'''
This program is used to find keypoint features in an image.

You need to click the upper left hand corner of what you want to train,
then click the right lower corner of what you want to train.

This will give you a template.  For instance if you wanted to train
a face to recognize in the image you would click on the upper left corner
of the face, then click in the lower right corner of the face.  If you
want to retrain then just right click to reset.

'''

print __doc__
 
import time
from SimpleCV import Color, Image, np, Camera
from SimpleCV.Display import Display
cam = Camera()
display = Display((800,600)) # create our display

def reinit():
	quality = 400.00
	minDist = 0.25
	minMatch = 0.2
	trained_img = None
	mode = "untrained"
	startX = None
	startY = None
	endY = None
	endX = None


while( display.isNotDone() ):
		img = cam.getImage().scale(0.5) # get the image

		if display.mouseX > 0:
			print "cood:",display.mouseX,",",display.mouseY

		if mode == "untrained":
			if startX == None or startY == None:
				img.dl().text("Click the upper left corner to train", (10,10))
				if display.mouseLeft:
					startX = display.mouseX
					startY = display.mouseY
					time.sleep(0.05)
					print "st:",startX,",",startY
			elif endX == None or endY == None:
				img.dl().text("now click the lower right corner to train", (10,10))
				if display.mouseLeft:
					endX = display.mouseX
					endY = display.mouseY
					mode = "trained"
					time.sleep(0.05)
					print "ed:",endX,",",endY

			else:
				pass
			
		if mode == "trained":
			img.dl().rectangle2pts((startX,startY),(endX,endY))
		

					
		img = img.applyLayers() # apply the layers before resize
		img.save(display)
