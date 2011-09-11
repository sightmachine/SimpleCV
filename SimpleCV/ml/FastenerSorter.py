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

cam = Camera()
edge_extractor = EdgeHistogramFeatureExtractor()
morph_extractor = MorphologyFeatureExtractor()
saveFile = 'test.tab'
classifier = BinarySVMClassifier('nut','bolt',[edge_extractor,morph_extractor])
classifier.load(saveFile)
blobber = BlobMaker()
disp = cam.getImage().show()

while not disp.isDone():
    img = cam.getImage()
    blobs = blobber.extract(img,threshval=200)
    
    if(len(blobs) > 0):
        blobs = blobs.sortArea()
        #blobs[-1].draw()
        #img.save(disp)
        blob = blobs[-1]
        blobs.draw()
        print(blob.angle())
        blob.rectifyMajorAxis()
        mask = Image(blob.mHullMask)
        h = mask.height
        #Get the mass of the top and bottom using the avg value as an approximation
        #for nails and screws the more massive end should be on top
        top =  mask[:,0:h/2].meanColor()
        bottom = mask[:,h/2:h].meanColor()
        if(bottom[0] > top[0] ):
            blobs[0].rotate(180)
            print('MASS FLIP')
        img.blit(mask)
        #blob.mImg.save(disp)     
    img.save(disp)    
    
   
   #a = (a.morphGradient()+a.dilate(3)-a.edges().smooth(aperature=(3,3)))
   #a.save(disp)