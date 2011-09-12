from SimpleCV import *
from numpy import *
from SimpleCV.Display import Display, pg
from SimpleCV.EdgeHistogramFeatureExtractor import *
from SimpleCV.HueHistogramFeatureExtractor import *
from SimpleCV.BOFFeatureExtractor import *
from SimpleCV.MorphologyFeatureExtractor import *
import Orange
from SimpleBinaryClassifier import *
from BinarySVMClassifier import *


def thresholdOp(in_image):
    return in_image.binarize(thresh=100).dilate(2)

cam = Camera(0)
edge_extractor = EdgeHistogramFeatureExtractor()
morph_extractor = MorphologyFeatureExtractor()
morph_extractor.setThresholdOperation(thresholdOp)

saveFile = 'test.tab'
classifier = BinarySVMClassifier('nut','bolt',[edge_extractor,morph_extractor])
classifier.load(saveFile)
blobber = BlobMaker()
disp = Display(resolution=(800,600))
count = 0
path = ''
file = 'sorting'
ext = '.png'
img = cam.getImage()

minsize = 50#   img.width*img.height/200
maxsize = img.width*img.height/8
while not disp.isDone():
    img = cam.getImage() 
    blobs = []
    x = img.width/2
    y = img.height/2
    w = x
    h = y
    dl = DrawingLayer((w,h))
    img = img.crop(x,y,w,h,centered=True)
    bw = thresholdOp(img)
    blobs = blobber.extractFromBinary(bw,img,minsize,maxsize)
    blobs = blobs.sortArea()
    if(len(blobs) > 0):
        #img.blit(blobs[-1].mImg)
        for i in range(len(blobs)):
            blob = blobs[i]
            hull = blob.mConvexHull
            #print(blob.angle())
            blob.rectifyMajorAxis()
            mask = Image(blob.mHullMask)        
            h = mask.height
            ##Get the mass of the top and bottom using the avg value as an approximation
            ##for nails and screws the more massive end should be on top
            top =  mask[:,0:h/2].meanColor()
            bottom = mask[:,h/2:h].meanColor()
            if(bottom[0] > top[0] ):
                blob.rotate(180)
            #    print('MASS FLIP')
            #
            name = classifier.classify(blob.mImg)
            itemName = str(name)
            #
            #itemName = 'derp'
            if(itemName=='bolt'):
                img.dl().polygon(hull,color=Color.GREEN,width=3)
            else:
                img.dl().polygon(hull,color=Color.ORANGE,width=3)
            img.dl().setFontSize(50)
            img.dl().text(itemName,(blob.x,blob.y),color=Color.BLACK)
            #print(name)
    if(disp.mouseLeft):
        disp.mouseLeft = 0
        fname = path+file+str(count)+ext
        print('Saved '+fname)
        img.save(fname)
        count = count + 1    
    img.save(disp)    
    
   
   #a = (a.morphGradient()+a.dilate(3)-a.edges().smooth(aperature=(3,3)))
   #a.save(disp)