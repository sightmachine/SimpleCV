from SimpleCV.base import *
from SimpleCV.ImageClass import Image
from SimpleCV.FeatureExtractorBase import *
import abc


class EdgeHistogramFeatureExtractor(object):

    mNBins = 10
    def __init__(self, mNBins=10):
        self.mNBins = mNBins

    def extract(self, img):
        """
        This feature extractor takes in a color image and returns a normalized color
        histogram of the pixel counts of each hue. 
        """
        #I am not sure this is the best normalization constant. 
        retVal = []
        p = max(img.width,img.height)/2
        minLine = 0.01*p
        gap = 0.1*p
        fs = img.findLines(threshold=10,minlinelength=minLine,maxlinegap=gap)
        ls = fs.length()/p #normalize to image length
        angs = fs.angle()
        lhist = np.histogram(ls,self.mNBins,normed=True,range=(0,1))
        ahist = np.histogram(angs,self.mNBins,normed=True,range=(-180,180))
        retVal.extend(lhist[0].tolist())
        retVal.extend(ahist[0].tolist())
        return retVal


    
    def getFieldNames(self):
        retVal = []
        for i in range(self.mNBins):
            name = "Length"+str(i)
            retVal.append(name)
        for i in range(self.mNBins):
            name = "Angle"+str(i)
            retVal.append(name)
                        
        return retVal
        """
        This method gives the names of each field in the feature vector in the
        order in which they are returned. For example, 'xpos' or 'width'
        """
    
    def getFieldTypes(self):
        """
        This method returns the field types
        - Do we need this - spec out 
        """

    def getNumFields(self):
        """
        This method returns the total number of fields in the feature vector.
        """
        return self.mNBins*2