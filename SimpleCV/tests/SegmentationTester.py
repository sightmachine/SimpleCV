import time
from SimpleCV import *
import SimpleCV.Segmentation.DiffSegmentation
from SimpleCV.Display import Display
w = 400
h = 300
display = Display(resolution = (w,h)) #create a new display to draw images on
cam = Camera()
segmentor = DiffSegmentation()
while(1):
    segmentor.addImage(cam.getImage())
    if(segmentor.isReady()):
        img = segmentor.getSegmentedImage()
        img.save(display)