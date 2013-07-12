from SimpleCV.base import *
from SimpleCV.ImageClass import Image
from SimpleCV.Features.FeatureExtractorBase import *
from SimpleCV.Features.BlobMaker import *

class MorphologyFeatureExtractor(FeatureExtractorBase):
    """
    This feature extractor collects some basic morphology infromation about a given
    image. It is assumed that the object to be recognized is the largest object
    in the image. The user must provide a segmented white on black blob image.
    This operation then straightens the image and collects the data.
    """
    mNBins = 9
    mBlobMaker = None
    mThresholdOpeation = None
    def __init__(self, thresholdOperation=None):
        """
        The threshold operation is a function of the form
        binaryimg = threshold(img)

        the simplest example would be:
        def binarize_wrap(img):

        """
        self.mNBins = 9
        self.mBlobMaker = BlobMaker()
        self.mThresholdOpeation = thresholdOperation

    def setThresholdOperation(self, threshOp):
        """
        The threshold operation is a function of the form
        binaryimg = threshold(img)

        Example:

        >>> def binarize_wrap(img):
        >>>    return img.binarize()
        """
        self.mThresholdOperation = threshOp

    def extract(self, img):
        """
        This method takes in a image and returns some basic morphology
        characteristics about the largest blob in the image. The
        if a color image is provided the threshold operation is applied.
        """
        retVal = None
        if(self.mThresholdOpeation is not None):
            bwImg = self.mThresholdOpeation(img)
        else:
            bwImg = img.binarize()

        if( self.mBlobMaker is None ):
            self.mBlobMaker = BlobMaker()

        fs = self.mBlobMaker.extractFromBinary(bwImg,img)
        if( fs is not None and len(fs) > 0 ):
            fs = fs.sortArea()
            retVal = []
            retVal.append(fs[0].mArea/fs[0].mPerimeter)
            retVal.append(fs[0].mAspectRatio)
            retVal.append(fs[0].mHu[0])
            retVal.append(fs[0].mHu[1])
            retVal.append(fs[0].mHu[2])
            retVal.append(fs[0].mHu[3])
            retVal.append(fs[0].mHu[4])
            retVal.append(fs[0].mHu[5])
            retVal.append(fs[0].mHu[6])
        return retVal


    def getFieldNames(self):
        """
        This method gives the names of each field in the feature vector in the
        order in which they are returned. For example, 'xpos' or 'width'
        """
        retVal = []
        retVal.append('area over perim')
        retVal.append('AR')
        retVal.append('Hu0')
        retVal.append('Hu1')
        retVal.append('Hu2')
        retVal.append('Hu3')
        retVal.append('Hu4')
        retVal.append('Hu5')
        retVal.append('Hu6')
        return retVal


    def getNumFields(self):
        """
        This method returns the total number of fields in the feature vector.
        """
        return self.mNBins

    def __getstate__(self):
        mydict = self.__dict__.copy()
        self.mBlobMaker = None
        del mydict['mBlobMaker']
        return mydict

    def __setstate__(self, mydict):
        self.__dict__ = mydict
        self.mBlobMaker = BlobMaker()
