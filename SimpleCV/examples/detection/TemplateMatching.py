'''
This example uses the built in template matching.  The easiest way
to think of this is if you played the card matching game, the cards would
pretty much have to be identical.  The template method doesn't allow much
for the scale to change, nor for rotation.  This is the most basic pattern
matching SimpleCV offers.  If you are looking for something more complex
you will probably want to look into img.findKeypoints()
'''
print __doc__


from SimpleCV import *
import sys, time, socket

source = Image("templatetest.png", sample=True) # the image to search
template = Image("template.png", sample=True) # the template to search the image for
t = 5

methods = ["SQR_DIFF","SQR_DIFF_NORM","CCOEFF","CCOEFF_NORM","CCORR","CCORR_NORM"] # the various types of template matching available
for m in methods:
    print "current method:", m # print the method being used
    result = Image("templatetest.png", sample=True)
    dl = DrawingLayer((source.width,source.height))
    fs = source.findTemplate(template,threshold=t,method=m)
    for match in fs:
        dl.rectangle((match.x,match.y),(match.width(),match.height()),color=Color.RED)
    result.addDrawingLayer(dl)
    result.applyLayers()
    result.show()
    time.sleep(3)

