from SimpleCV import *
from numpy import *
from SimpleCV.Display import Display, pg
from SimpleCV import EdgeHistogramFeatureExtractor
from SimpleCV import MorphologyFeatureExtractor 

#we pass this methods as our threshold operation
def thresholdOp(in_image):
    return in_image.binarize(thresh=70).invert().dilate(2)

morph_extractor = MorphologyFeatureExtractor()
morph_extractor.setThresholdOperation(thresholdOp)


extractors = [morph_extractor]
nuts_path = "./data/nuts/"
bolts_path = "./data/bolts/"
path = [nuts_path,bolts_path]
classes = ['washer','bolt']
props ={
        'KernelType':'Linear', #default is a RBF Kernel
        'SVMType':'C',     #default is C 
        'nu':None,          # NU for SVM NU
        'c':None,           #C for SVM C - the slack variable
        'degree':None,      #degree for poly kernels - defaults to 3
        'coef':None,        #coef for Poly/Sigmoid defaults to 0
        'gamma':None,       #kernel param for poly/rbf/sigma - default is 1/#samples       
    }


TrainData = False
classifierSVM = None
if( TrainData ):
    classifierSVMS = SVMClassifier(extractors,props)
    classifierSVMS.train(path,classes,verbose=True) #train
    classifierSVMS.save("nutbolt.pkl")


classifierSVM = SVMClassifier.load("nutbolt.pkl")

def thresholdOpGreen(in_image):
     return in_image.hueDistance(60).binarize(thresh=70).invert().dilate(2)

morph_extractor = MorphologyFeatureExtractor()
morph_extractor.setThresholdOperation(thresholdOp)
classifierSVM.setFeatureExtractors([morph_extractor])

cam = Camera(1)
blobber = BlobMaker()
img = cam.getImage()
disp = Display(resolution=(800,600))
minsize = 400#   img.width*img.height/200
maxsize = (800*600)/20
while not disp.isDone():
    img = cam.getImage().resize(800,600)
    blobs = []
    w = img.width
    h = img.height
    dl = DrawingLayer((w,h))
    bw = thresholdOpGreen(img)
    #extract the blobs
    blobs = blobber.extractFromBinary(bw,img,minsize,maxsize)
    #blobs.draw(color=Color.RED)
    #get the average image color - we use this to filter out illumination effects
    if(len(blobs) > 0 ):
        blobs = blobs.sortArea()
        biggest = blobs[-1].mArea
        if( biggest < maxsize):
            for i in range(len(blobs)):
                blob = blobs[i]
                hull = blob.mConvexHull
            #make the major axis align to vertical
                blob.rectifyMajorAxis()
                mask = blob.mHullMask 
                h = mask.height
                top =  mask[:,0:h/2].meanColor()
                bottom = mask[:,h/2:h].meanColor()
                if(bottom[0] > top[0] ):
                    blob.rotate(180)
                    name = classifierSVM.classify(blob.mImg)
                    if( name is not None ):
                        itemName = str(name)
                        if(itemName=='bolt'):
                            img.dl().polygon(hull,color=Color.BLUE,width=3)
                            img.dl().setFontSize(50)
                            img.dl().text(itemName,(blob.x,blob.y),color=Color.BLUE)
                        else:
                            img.dl().polygon(hull,color=Color.ORANGE,width=3)
                            img.dl().setFontSize(50)
                            img.dl().text(itemName,(blob.x,blob.y),color=Color.ORANGE)

    img.save(disp)    
