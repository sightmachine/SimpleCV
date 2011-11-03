import time
from SimpleCV import *
from SimpleCV.Display import Display, pg
from SimpleCV.Segmentation import ColorSegmentation
segmentation = ColorSegmentation()
cam = Camera(1)
SegmentMode = False
x0 = 0
y0 = 0
x1 = 0
y1 = 0
img = cam.getImage()
w = 800
h = 600
display = Display((w,h))
mouse_down = False
while not display.isDone():
    temp = cam.getImage()
    img = temp.scale(w,h)
    dl = DrawingLayer((w,h))
    if SegmentMode:
        segmentation.addImage(img)
        if(segmentation.isReady()):
            img = segmentation.getSegmentedImage()
            img = img.erode(iterations = 2).dilate().invert()
            img.save(display)
        if(display.mouseLeft):
            SegmentMode = False
            segmentation.reset()
            display.mouseLeft = False
    else:
        if(display.mouseLeft and not mouse_down):
            x0 = display.mouseX
            y0 = display.mouseY
            mouse_down = True
        elif( display.mouseLeft and mouse_down ):
            dl.circle((x0,y0),radius=10,color=Color.RED)
            dl.rectangle2pts( (display.mouseX,display.mouseY),(x0,y0),color=Color.RED)
            dl.circle((display.mouseX,display.mouseY),radius=10,color=Color.RED)
        elif(mouse_down):
            x = min(x0,display.mouseX)
            y = min(y0,display.mouseY)
            ww = max(x0,display.mouseX)-x
            hh = max(y0,display.mouseY)-y
            if( ww > 0 and hh > 0):
                crop = img.crop(x,y,ww,hh)
                segmentation.addToModel(crop)
                SegmentMode = True
                mouse_down = False
        img.addDrawingLayer(dl)
        img.save(display)
 
    time.sleep(0.001)
    