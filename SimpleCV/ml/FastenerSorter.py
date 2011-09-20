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

#we pass this methods as our threshold operation
def thresholdOp(in_image):
    return in_image.binarize(thresh=90).dilate(2)

cam = Camera(0)
#setup the feature extractors
edge_extractor = EdgeHistogramFeatureExtractor()
morph_extractor = MorphologyFeatureExtractor()
morph_extractor.setThresholdOperation(thresholdOp)

#load the classifier
saveFile = 'test.tab'
classifier = BinarySVMClassifier('nut','bolt',[edge_extractor,morph_extractor])
classifier.load(saveFile)
blobber = BlobMaker()
disp = Display(resolution=(1440,900))
#these params are to save the image
count = 0
path = ''
file = 'sorting'
ext = '.png'
img = cam.getImage()

minsize = 50#   img.width*img.height/200
maxsize = img.width*img.height/8
avgColorThresh = 85
while not disp.isDone():
    img = cam.getImage() 
    blobs = []
    x = img.width/2
    y = img.height/2
    w = x
    h = y
    hthresh = w*h*0.05
    dl = DrawingLayer((w,h))
    #crop the image, to get rid of illumination effects
    img = img.crop(x,y,w,h,centered=True)
    # do the threshold
    bw = thresholdOp(img)
    #extract the blobs
    blobs = blobber.extractFromBinary(bw,img,minsize,maxsize)
    blobs = blobs.sortArea()
    #get the average image color - we use this to filter out illumination effects
    avgColor = img.meanColor()
    if(len(blobs) > 0):
        for i in range(len(blobs)):
            blob = blobs[i]
            blobColor = blob.mAvgColor
            dist = spsd.cdist([avgColor],[blobColor])
            #if the color is above our thresh
            if( dist > avgColorThresh ):
                hull = blob.mConvexHull
                #make the major axis align to vertical
                blob.rectifyMajorAxis()
                #get the mask, see which side more of the mask sits on
                mask = Image(blob.mHullMask)        
                h = mask.height
                ##Get the mass of the top and bottom using the avg value as an  approximation
                ##for nails and screws the more massive end should be on top
                top =  mask[:,0:h/2].meanColor()
                bottom = mask[:,h/2:h].meanColor()
                if(bottom[0] > top[0] ):
                    blob.rotate(180)
                #apply the classifier
                name = classifier.classify(blob.mImg)
                if( name is not None ):
                    #get the name and apply it
                    itemName = str(name)
                    if(blob.mArea > hthresh ):
                        img.dl().polygon(hull, color=Color.RED,width=7)
                        img.dl().setFontSize(70)
                        img.dl().text('HUMAN - DESTROY',(blob.x,blob.y),color=Color.RED)
                    elif(itemName=='bolt'):
                        img.dl().polygon(hull,color=Color.GREEN,width=3)
                        img.dl().setFontSize(50)
                        img.dl().text(itemName,(blob.x,blob.y),color=Color.BLACK)
                    else:
                        img.dl().polygon(hull,color=Color.ORANGE,width=3)
                        img.dl().setFontSize(50)
                        img.dl().text(itemName,(blob.x,blob.y),color=Color.BLACK)
                    
                    i
                #print(name)
        if(disp.mouseLeft):
            #save any frame we click on 
            disp.mouseLeft = 0
            fname = path+file+str(count)+ext
            print('Saved '+fname)
            img.save(fname)
            count = count + 1    
    img.save(disp)    