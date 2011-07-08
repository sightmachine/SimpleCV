#!/usr/bin/python 
from SimpleCV import *
from SimpleCV import RenderEngine

img = Image("../sampleimages/aerospace.jpg")
engine = RenderEngine(img)
a = (20,20)
b = (20,100)
c = (100,100)
d = (100,20)
engine.drawLine(a,b)
engine.drawLine(b,c)
engine.drawLine(c,d)
engine.drawLine(d,a)
img2 = engine.renderImage()
img2.save("ItWorks.jpg")