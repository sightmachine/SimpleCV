from SimpleCV.Features import Feature, FeatureSet, BlobMaker
from SimpleCV.ImageClass import Image
from SimpleCV.Segmentation.SegmentationBase import SegmentationBase

class MOGSegmentation(SegmentationBase):
    """
    Background subtraction using mixture of gausians.
    For each pixel store a set of gaussian distributions and try to fit new pixels
    into those distributions. One of the distributions will represent the background.
    
    history - length of the pixel history to be stored
    nMixtures - number of gaussian distributions to be stored per pixel
    backgroundRatio - chance of a pixel being included into the background model
    noiseSigma - noise amount
    learning rate - higher learning rate means the system will adapt faster to new backgrounds
    """

    mError = False
    mDiffImg = None
    mColorImg = None
    mReady = False
    
    # OpenCV default parameters
    history = 200
    nMixtures = 5
    backgroundRatio = 0.7
    noiseSigma = 15
    learningRate = 0.7
    bsMOG = None

    def __init__(self, history = 200, nMixtures = 5, backgroundRatio = 0.7, noiseSigma = 15, learningRate = 0.7):
        
        try:
            import cv2            
        except ImportError:
            raise ImportError("Cannot load OpenCV library which is required by SimpleCV")
            return    
        if not hasattr(cv2, 'BackgroundSubtractorMOG'):
            raise ImportError("A newer version of OpenCV is needed")
            return            
        
        self.mError = False
        self.mReady = False        
        self.mDiffImg = None
        self.mColorImg = None
        self.mBlobMaker = BlobMaker()
        
        self.history = history
        self.nMixtures = nMixtures
        self.backgroundRatio = backgroundRatio
        self.noiseSigma = noiseSigma
        self.learningRate = learningRate
        
        self.mBSMOG = cv2.BackgroundSubtractorMOG(history, nMixtures, backgroundRatio, noiseSigma)
        
        
        

    def addImage(self, img):
        """
        Add a single image to the segmentation algorithm
        """
        if( img is None ):
            return

        self.mColorImg = img
        self.mDiffImg = Image(self.mBSMOG.apply(img.getNumpyCv2(), None, self.learningRate), cv2image=True) 
        self.mReady = True
        return


    def isReady(self):
        """
        Returns true if the camera has a segmented image ready.
        """
        return self.mReady


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
        self.mError = false
        return

    def reset(self):
        """
        Perform a reset of the segmentation systems underlying data.
        """
        self.mModelImg = None
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
        return self.mDiffImg

    def getSegmentedBlobs(self):
        """
        return the segmented blobs from the fg/bg image
        """
        retVal = []
        if( self.mColorImg is not None and self.mDiffImg is not None ):
            retVal = self.mBlobMaker.extractFromBinary(self.mDiffImg ,self.mColorImg)
        return retVal


    def __getstate__(self):
        mydict = self.__dict__.copy()
        self.mBlobMaker = None
        self.mDiffImg = None
        del mydict['mBlobMaker']
        del mydict['mDiffImg']
        return mydict

    def __setstate__(self, mydict):
        self.__dict__ = mydict
        self.mBlobMaker = BlobMaker()
        
