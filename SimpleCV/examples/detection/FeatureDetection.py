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
display = Display((640,480)) # create our display

quality = 400.00
minDist = 0.35
minMatch = 0.2
template_img = None
mode = "untrained"
startX = None
startY = None
endY = None
endX = None

while( display.isNotDone() ):
		img = cam.getImage().resize(640,480)

		#Display this if a template has not been trained yet
		if mode == "untrained":
			if startX == None or startY == None:
				img.dl().text("Click the upper left corner to train", (10,10))
				if display.mouseLeft:
					startX = display.mouseRawX
					startY = display.mouseRawY
					time.sleep(0.2)
			elif endX == None or endY == None:
				img.dl().text("now click the lower right corner to train", (10,10))
				if display.mouseLeft:
					endX = display.mouseX
					endY = display.mouseY
					template_img = img.crop(startX,startY,endX - startX, endY - startY)
					mode = "trained"
					time.sleep(0.2)
			else:
				pass
			
		if mode == "trained":
			keypoints = img.findKeypointMatch(template_img,quality,minDist,minMatch)
			if keypoints:
				#keypoints.draw()
				img = img.applyLayers()
			img = img.drawKeypointMatches(template_img)   # draw the keypoint layers

			#Reset
			if display.mouseRight:
				template_img = None
				mode = "untrained"
				startX = None
				startY = None
				endY = None
				endX = None
				
		img = img.applyLayers() # apply the layers before resize
		img = img.resize(640,480)
		img.save(display)
		time.sleep(0.05)
