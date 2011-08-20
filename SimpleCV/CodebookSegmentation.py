#
#from SimpleCV.base import *
#from SimpleCV.Features import Feature, FeatureSet
#from SimpleCV.ImageClass import Image
#from SimpleCV.BlobMaker import BlobMaker
#from SimpleCV.SegmentationBase import SegmentationBase
#from rcdtype import *
#
#import abc
## THIS IS SCRATCH CODE
## STAY AWAY
##img = Image("./SimpleCV/sampleimages/aerospace.jpg")
##numpyImg = img.getNumpy()
##shape = img.getNumpy().shape
##linear_img = img.getNumpy().reshape(shape[0]*shape[1],3)
##linear_list = linear_img.tolist()
#
#from collections import namedtuple
#CodebookCode = recordtype('CodebookCode',['yMax','yMin','yLearnHigh','yLearnLow','uMax','uMin','uLearnHigh','uLearnLow','vMax','vMin','vLearnHigh','vLearnLow','lastUpdate','stale'] )
#
##NEED TO GET ACTUAL THRESHOLD OPERATION
#
##make the list of codebooks that is image widthxheight
##convert the image to yuv, linearize
##need the count array 
##map the lambda function of update codebook to the input pixel array and the codebook
##map(lambda x,y: Codecheck(x,y), image, codebook)
#
#class CodebookSegmentation(SegmentationBase):
#
#    mError = False
#    mResultImg = None
#    mColorImg = None
#    mGrayOnlyMode = True
#    mCount = 0
#    mCodebook = []
#    mMinBound = [10,10,10]
#    mMaxBound =[10,10,10]
#    mBounds = [10,10,10]
#    mBlobMaker = None
#    mRefilter = 60 # how often to purge the codebook
#    mW = 0
#    mH = 0
#    mSz = 0
#
#    def __init__(self, grayOnly=False, minBound=(10,10,10), maxBound=(10,10,10) ):
#        self.mError = False
#        self.mResultImg = None
#        self.mColorImg = None
#        self.mGrayOnlyMode = True
#        self.mCount = 0
#        self.mCodebook = None
#        self.mRefilter = 60 
#        self.mMinBound = [10,10,10]
#        self.mMaxBound = [10,10,10]
#        self.mBounds = [10,10,10]
#        self.mBlobMaker = None
#        self.mW = 0
#        self.mH = 0
#        self.mSz = 0
#        
#    def loadSettings(self, file):       
#        """
#        Load all of the segmentation settings from file
#        """
#        myFile = open(file,'w')
#        myFile.writeline("Difference Segmentation Parameters")
#        myFile.write(str(self.mGrayOnlyMode))
#        myFile.write(str(self.mThreshold))
#        myFile.close()
#        return
#    
#    def saveSettings(self, file):
#        """
#        save all of the segmentation settings from file
#        """
#        myFile = open(file,'r')
#        myFile.readline()
#        self.mGrayOnlyMode = myFile.readline()
#        self.mThreshold = myFile.readline()
#        myFile.close()
#        return
#    
#    def addImage(self, img):
#        """
#        Add a single image to the segmentation algorithm
#        """
#        if( img is None ):
#            return
#        if( self.mCodebook == None ):
#            self.mW = img.width
#            self.mH = img.height
#            self.mSz = img.width * img.height
#            self.mCodebook = self.mSz * [None]
#        else:
#            self.mCount = self.mCount + 1 
#            numpyImg = img.toHSV().getNumpy()
#            shape = img.getNumpy().shape
#            linearImg = img.getNumpy().reshape(shape[0]*shape[1],3).tolist()
#            
#            # update codebook
#            linearResult = map(lambda code,img: self.CodebookThreshold(code,img,self.mMinBound,self.mMaxBound), self.mCodebook,linearImg )
#            #convert the NP result to an image
#            print(linearResult[0])
#            self.mResultImg = Image(np.array(linearResult).reshape(self.mW,self.mH))
#            
#            
#            #now do the codebook update ---- this should alter between static (setup once) and dynamic continuous update
#            self.mCodebook = map( lambda code,img: self.UpdateCodebook(code,img,self.mCount,self.mBounds),self.mCodebook,linearImg)
#            print(self.mCodebook[0])
#            print(self.mCount)
#            print('-------------------------------------')
#            if(self.mCount%self.mRefilter == 0 and self.mCount > 0):
#                self.mCodebook = filter(lambda codebook: self.PurgeCodebook(codebook,self.mCount/2), self.mCodebook)
#        return
#    
#
#    def isReady(self):
#        """
#        Returns true if the camera has a segmented image ready. 
#        """
#        if( self.mResultImg is None ):
#            return False
#        else:
#            return True
#
#    
#    def isError(self):
#        """
#        Returns true if the segmentation system has detected an error.
#        Eventually we'll consruct a syntax of errors so this becomes
#        more expressive 
#        """
#        return self.mError #need to make a generic error checker
#    
#    def resetError(self):
#        """
#        Clear the previous error. 
#        """
#        self.mError = false
#        return 
#
#    def reset(self):
#        """
#        Perform a reset of the segmentation systems underlying data.
#        """
#        self.mResultImg = None
#        self.mColorImg = None
#        self.mCount = 0
#        self.mCodebook = None
#        self.mRefilter = 60 
#        self.mW = 0
#        self.mH = 0
#        self.mSz = 0
#
#    
#    def getRawImage(self):
#        """
#        Return the segmented image with white representing the foreground
#        and black the background. 
#        """
#        return self.mResultImg
#    
#    def getSegmentedImage(self, whiteFG=True):
#        """
#        Return the segmented image with white representing the foreground
#        and black the background. 
#        """
#        retVal = None
#        if( whiteFG ):
#            retVal = self.mResultImg.binarize(thresh=self.mThreshold)
#        else:
#            retVal = self.mResultImg.binarize(thresh=self.mThreshold).invert()
#        return retVal
#    
#    def getSegmentedBlobs(self):
#        """
#        return the segmented blobs from the fg/bg image
#        """
#        retVal = []
#        if( self.mColorImg is not None and self.mResultImg is not None ):
#            retVal = self.mBlobMaker.extractFromBinary(self.mResultImg.binarize(thresh=self.mThreshold),self.mColorImg)
# 
#        return retVal
#        
#        
#    def Codecheck(self, code, pixel ):
#        return( pixel[0] <= code.yLearnHigh and
#                pixel[0] >= code.yLearnLow and
#                pixel[1] <= code.uLearnHigh and
#                pixel[1] >= code.uLearnLow and
#                pixel[2] <= code.vLearnHigh and
#                pixel[2] >= code.vLearnLow )
#        
#    def CodeMatch(self,code,pixel,minBound,maxBound):
#        # return true if pixel is close to the code
#        return ( pixel[0] <= code.yMax+maxBound[0] and
#                 pixel[0] >= code.yMin+minBound[0] and
#                 pixel[1] <= code.uMax+maxBound[1] and
#                 pixel[1] >= code.uMin+minBound[1] and
#                 pixel[2] <= code.vMax+maxBound[2] and
#                 pixel[2] >= code.vMin+minBound[2] )
#        
#    def CodebookThreshold(self,codebook,pixel,minBound=(10,10,10),maxBound=(10,10,10)):
#        #codebook should be short, we'll iterate here
#        if(codebook is None):   
#            return [255]
#        for c in codebook:
#            if( self.CodeMatch(c,pixel,minBound,maxBound) ):
#                return [0]
#        return [255]
#        
#    def UpdateCodebook(self,codebook, pixel, count, bounds ):
#        # count = c.t
#        low = [0,0,0]
#        high = [0,0,0]
#        for i in range(3):
#            low[i] = max(pixel[i]-bounds[i],0)
#            high[i] = min(pixel[i]+bounds[i],255)
#        
#        #filter() such that the resulting codebook code is updateCode
#        updateCode = None
#        if(codebook is not None):
#            updateCode = filter(lambda x: self.Codecheck(x,pixel), codebook)
#    
#        #update the results
#        if( updateCode is not None and len(updateCode) > 0):
#            print("UPDATE ")
#            print(updateCode[0])
#            updateCode = updateCode[0]
#            if(updateCode.yMax < pixel[0] ):
#                updateCode.yMax = pixel[0]
#            elif( updateCode.yMin > pixel[0] ):
#                updateCode.yMin = pixel[0] 
#        
#            if(updateCode.uMax < pixel[1] ):
#                updateCode.uMax = pixel[1]
#            elif( updateCode.uMin > pixel[1] ):
#                updateCode.uMin = pixel[1]
#            
#            if(updateCode.vMax< pixel[2] ):        
#                updateCode.vMax = pixel[2]
#            elif( updateCode.vMin > pixel[2] ):
#                updateCode.vMin = pixel[2] 
#            # update the negative entries
#            
#            #this is the last step... is this right?
#            if(updateCode.yLearnHigh < high[0] ):
#                updateCode.yLearnHigh+=1
#            if(updateCode.yLearnLow > low[0] ):
#                updateCode.yLearnLow-=1
#            if(updateCode.uLearnHigh < high[1] ):
#                updateCode.uLearnHigh+=1
#            if(updateCode.uLearnLow > low[1] ):
#                updateCode.uLearnLow-=1
#            if(updateCode.vLearnHigh < high[2] ):
#                updateCode.vLearnHigh+=1
#            if(updateCode.vLearnLow > low[2] ):
#                updateCode.vLearnLow-=1
#                
#            for cbc in codebook:
#                negrun = count - cbc.lastUpdate
#                if(cbc.stale < negrun ):
#                    cbc.stale = negrun
#            
#        else:#finally add a new value to the codebook
#            newCode = CodebookCode( pixel[0],pixel[0],high[0],low[0],
#                                    pixel[1],pixel[1],high[1],low[1],
#                                    pixel[2],pixel[2],high[2],low[2],
#                                    count,0)
#            if( codebook is None ):
#                codebook = [newCode]
#            else:
#                codebook.append(newCode)
#                
#        return codebook
#    
#    def PurgeCodebook(self,codebook, thresh):
#        #thresh is c.t>>1
#        retVal = [] 
#        for codes in codebook:
#            if codes.stale < thresh:
#                codes.lastUpdate = 0 
#                retVal.append(codes)
#
#
#        
#        
#    
#    