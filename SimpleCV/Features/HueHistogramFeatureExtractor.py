from SimpleCV.base import *
from SimpleCV.ImageClass import Image
from SimpleCV.Features.FeatureExtractorBase import *

class HueHistogramFeatureExtractor(FeatureExtractorBase):
    """
    Create a Hue Histogram feature extractor. This feature extractor
    takes in an image, gets the hue channel, bins the number of pixels
    with a particular Hue, and returns the results.

    mNBins - the number of Hue bins.
    """
    mNBins = 16
    def __init__(self, mNBins=16):
        #we define the black (positive) and white (negative) regions of an image
        #to get our haar wavelet
        self.mNBins = mNBins

    def extract(self, img):
        """
        This feature extractor takes in a color image and returns a normalized color
        histogram of the pixel counts of each hue.
        """
        img = img.toHLS()
        h = img.getEmpty(1)
        cv.Split(img.getBitmap(),h,None,None,None)
        npa = np.array(h[:,:])
        npa = npa.reshape(1,npa.shape[0]*npa.shape[1])
        hist = np.histogram(npa,self.mNBins,normed=True,range=(0,255))
        return hist[0].tolist()


    def getFieldNames(self):
        """
        This method gives the names of each field in the feature vector in the
        order in which they are returned. For example, 'xpos' or 'width'
        """
        retVal = []
        for i in range(self.mNBins):
            name = "Hue"+str(i)
            retVal.append(name)
        return retVal

    def getNumFields(self):
        """
        This method returns the total number of fields in the feature vector.
        """
        return self.mNBins
