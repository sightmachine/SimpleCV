from SimpleCV.base import *
from SimpleCV.ImageClass import Image
from SimpleCV.FeatureExtractorBase import *
import abc


class MorphologyFeatureExtractor(object):
    """
    This feature extractor collects some basic morphology infromation about a given
    image. It is assumed that the object to be recognized is the largest object
    in the image. The user must provide a segmented white on black blob image.
    This operation then straightens the image and collects the data. 
    """
    mNBins = 12
    mBlobMaker = None
    def __init__(self):
        self.mNBins = 12
        self.mBlobMaker = BlobMaker() 

    def extract(self, bwImg, colorImg):
        """
        This feature extractor takes in a color image and returns a normalized color
        histogram of the pixel counts of each hue. 
        """
        fs = self.mBlobMaker.extractFromBinary(bwImg,colorImg)
        fs = fs.sortArea()
        retVal = []
        retVal.append(fs[0].mArea/fs[0].mPerimeter)
        retVal.append(fs[0].mAspectRatio)
        retVal.append(fs[0].mHuMoments[0])
        retVal.append(fs[0].mHuMoments[1])
        retVal.append(fs[0].mHuMoments[2])
        retVal.append(fs[0].mHuMoments[3])
        retVal.append(fs[0].mHuMoments[4])
        retVal.append(fs[0].mHuMoments[5])
        retVal.append(fs[0].mHuMoments[6])
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

    
    def getFieldTypes(self):
        """
        This method returns the field types
        - Do we need this - spec out 
        """

    def getNumFields(self):
        """
        This method returns the total number of fields in the feature vector.
        """
        return self.mNBins