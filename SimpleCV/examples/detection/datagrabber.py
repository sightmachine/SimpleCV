from SimpleCV import *
from numpy import *
from SimpleCV.Display import Display, pg
from SimpleCV import EdgeHistogramFeatureExtractor
from SimpleCV import MorphologyFeatureExtractor 

def thresholdOp(in_image):
    return in_image.hueDistance(60).binarize(thresh=70).invert().dilate(2)

cam = Camera(1)

#classifier.load(saveFile)
blobber = BlobMaker()
disp = Display(resolution=(1440,900))
#these params are to save the image
count = 0
path = ''
file = './data/bolts/bolts'
ext = '.png'
img = cam.getImage()

minsize = 350#   img.width*img.height/200
maxsize = img.width*img.height/8
avgColorThresh = 85
count = 0
while not disp.isDone():
    img = cam.getImage() 
    blobs = []
    w = img.width
    h = img.height
    hthresh = w*h*0.05
    dl = DrawingLayer((w,h))
    bw = thresholdOp(img)
    blobs = blobber.extractFromBinary(bw,img,minsize,maxsize)
    blobs = blobs.sortArea()
    blobs.draw(color=Color.RED)
    #get the average image color - we use this to filter out illumination effects
    avgColor = img.meanColor()
    if(len(blobs) > 0 and len(blobs) < 25 ):
        for i in range(len(blobs)):
            print blobs[i].mArea
            blob = blobs[i]
            blob.rectifyMajorAxis()
            hull = blob.mConvexHull
            mask = blob.mHullMask        
            h = mask.height
            top =  mask[:,0:h/2].meanColor()
            bottom = mask[:,h/2:h].meanColor()
            if(bottom[0] > top[0] ):
                blob.rotate(180)
            fname = file+str(count)+ext
            blob.mImg.save(fname)
            count = count+1
    time.sleep(.1)
    img.save(disp)    
