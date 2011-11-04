from SimpleCV.base import *
from SimpleCV.ImageClass import Image
from SimpleCV.Features.FeatureExtractorBase import *


class EdgeHistogramFeatureExtractor(FeatureExtractorBase):
    """
    Create a 1D edge length histogram and 1D edge angle histogram.
    
    This method takes in an image, applies an edge detector, and calculates
    the length and direction of lines in the image.
    
    bins = the number of bins
    """
    mNBins = 10
    def __init__(self, bins=10):

        self.mNBins = bins

    def extract(self, img):
        """
        Extract the line orientation and and length histogram.
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
        """
        Return the names of all of the length and angle fields. 
        """
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

    def getNumFields(self):
        """
        This method returns the total number of fields in the feature vector.
        """
        return self.mNBins*2
