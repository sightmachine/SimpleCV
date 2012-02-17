from SimpleCV import *
from numpy import *
from SimpleCV.Display import Display, pg
from SimpleCV import MorphologyFeatureExtractor 

#we pass this methods as our threshold operation
def thresholdOp(in_image):
    return in_image.binarize(thresh=70).invert().dilate(2)
# extract only morphology
morph_extractor = MorphologyFeatureExtractor()
morph_extractor.setThresholdOperation(thresholdOp)
extractors = [morph_extractor]
#setup the paths to our data
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
# flag if we need to train the SVM
TrainData = False
classifierSVM = None
if( TrainData ):
    classifierSVMS = SVMClassifier(extractors,props)
    classifierSVMS.train(path,classes,verbose=True) #train
    classifierSVMS.save("nutbolt.pkl")

# (re) load the SVM and feature extractors
classifierSVM = SVMClassifier.load("nutbolt.pkl")
def thresholdOpGreen(in_image):
     return in_image.hueDistance(60).binarize(thresh=70).invert().dilate(2)
morph_extractor = MorphologyFeatureExtractor()
morph_extractor.setThresholdOperation(thresholdOp)
classifierSVM.setFeatureExtractors([morph_extractor])


count = 0
cam = Camera(1)
blobber = BlobMaker()
disp = Display(resolution=(800,600))
minsize = 100
maxsize = (800*600)/10
while not disp.isDone():
    img = cam.getImage().resize(800,600)
    blobs = []
    w = img.width
    h = img.height
    dl = DrawingLayer((w,h))
    #segment our items from the background
    bw = thresholdOpGreen(img)
    #extract the blobs
    blobs = blobber.extractFromBinary(bw,img,minsize,maxsize)
    # if we get a blob
    if(len(blobs) > 0 ):
        # sort the blobs by size
        blobs = blobs.sortArea()
        biggest = blobs[-1].mArea
        # if we get a big blob ... ignore the frame
        if( biggest < maxsize):
            for i in range(len(blobs)):
                blob = blobs[i]
                # make the blob line up to veritcal
                blob.rectifyMajorAxis()
                mask = blob.mHullMask 
                # make sure bolts are right side up
                h = mask.height
                top =  mask[:,0:h/2].meanColor()
                bottom = mask[:,h/2:h].meanColor()
                if(bottom[0] > top[0] ):
                    blob.rotate(180)
                # do our classification
                name = classifierSVM.classify(blob.mImg)
                # render the result. 
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
    #count = count + 1
    #fname = "output"+str(count)+".png"
    #img.save(fname)
