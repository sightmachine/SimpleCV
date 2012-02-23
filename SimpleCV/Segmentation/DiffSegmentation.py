from SimpleCV.base import *
from SimpleCV.Features import Feature, FeatureSet, BlobMaker
from SimpleCV.ImageClass import Image
from SimpleCV.Segmentation.SegmentationBase import SegmentationBase


class DiffSegmentation(SegmentationBase):
    """
    This method will do image segmentation by looking at the difference between
    two frames.
    
    grayOnly - use only gray images.
    threshold - The value at which we consider the color difference to
    be significant enough to be foreground imagery.
    
    The general usage is
    
    >>> segmentor = DiffSegmentation()
    >>> cam = Camera()
    >>> while(1):
    >>>    segmentor.addImage(cam.getImage())
    >>>    if(segmentor.isReady()):
    >>>        img = segmentor.getSegmentedImage()

    """
    mError = False
    mLastImg = None
    mCurrImg = None
    mDiffImg = None
    mColorImg = None
    mGrayOnlyMode = True
    mThreshold = 10
    mBlobMaker = None
    
    def __init__(self, grayOnly=False, threshold = (10,10,10) ):
        self.mGrayOnlyMode = grayOnly
        self.mThreshold = threshold 
        self.mError = False
        self.mCurrImg = None
        self.mLastImg = None
        self.mDiffImg = None
        self.mColorImg = None
        self.mBlobMaker = BlobMaker()
    
    def addImage(self, img):
        """
        Add a single image to the segmentation algorithm
        """
        if( img is None ):
            return
        if( self.mLastImg == None ):
            if( self.mGrayOnlyMode ):
                self.mLastImg = img.toGray()
                self.mDiffImg = Image(self.mLastImg.getEmpty(1))
                self.mCurrImg = None
            else:
                self.mLastImg = img
                self.mDiffImg = Image(self.mLastImg.getEmpty(3))
                self.mCurrImg = None                
        else:   
            if( self.mCurrImg is not None ): #catch the first step
                self.mLastImg = self.mCurrImg

            if( self.mGrayOnlyMode ):
                self.mColorImg = img
                self.mCurrImg = img.toGray()
            else:
                self.mColorImg = img
                self.mCurrImg = img
                
                
            cv.AbsDiff(self.mCurrImg.getBitmap(),self.mLastImg.getBitmap(),self.mDiffImg.getBitmap())

        return
    

    def isReady(self):
        """
        Returns true if the camera has a segmented image ready. 
        """
        if( self.mDiffImg is None ):
            return False
        else:
            return True

    
    def isError(self):
        """
        Returns true if the segmentation system has detected an error.
        Eventually we'll consruct a syntax of errors so this becomes
        more expressive 
        """
        return self.mError #need to make a generic error checker
    
    def resetError(self):
        """
        Clear the previous error. 
        """
        self.mError = False
        return 

    def reset(self):
        """
        Perform a reset of the segmentation systems underlying data.
        """
        self.mCurrImg = None
        self.mLastImg = None
        self.mDiffImg = None
    
    def getRawImage(self):
        """
        Return the segmented image with white representing the foreground
        and black the background. 
        """
        return self.mDiffImg
    
    def getSegmentedImage(self, whiteFG=True):
        """
        Return the segmented image with white representing the foreground
        and black the background. 
        """
        retVal = None
        if( whiteFG ):
            retVal = self.mDiffImg.binarize(thresh=self.mThreshold)
        else:
            retVal = self.mDiffImg.binarize(thresh=self.mThreshold).invert()
        return retVal
    
    def getSegmentedBlobs(self):
        """
        return the segmented blobs from the fg/bg image
        """
        retVal = []
        if( self.mColorImg is not None and self.mDiffImg is not None ):
            retVal = self.mBlobMaker.extractFromBinary(self.mDiffImg.binarize(thresh=self.mThreshold),self.mColorImg)
        return retVal
    
    def __getstate__(self):
        mydict = self.__dict__.copy()
        self.mBlobMaker = None
        del mydict['mBlobMaker']     
        return mydict
    
    def __setstate__(self, mydict):
        self.__dict__ = mydict
        self.mBlobMaker = BlobMaker()
        
    
    
