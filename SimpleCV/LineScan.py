from SimpleCV.base import *
from SimpleCV.Color import *
import copy


class LineScan(list):

#    def __init__(self, data):#, points, indicies, image):
        #self.indicies = indices # the (x,y) points from the signal
        #self.image = image
#        pass
        
#    def __init__(self,points):
#        pass
        
    def __getitem__(self,key):
        """
        **SUMMARY**

        Returns a LineScan when sliced. Previously used to
        return list. Now it is possible to use LineScanm member
        functions on sub-lists

        """
        if type(key) is types.SliceType: #Or can use 'try:' for speed
            return LineScan(list.__getitem__(self, key))
        else:
            return list.__getitem__(self,key)
        
    def __getslice__(self, i, j):
        """
        Deprecated since python 2.0, now using __getitem__
        """
        return self.__getitem__(slice(i,j))

    def pointLocations(self):
        pass
        
    def resample(self):
        pass
        
    def smooth(self):
        pass

    def fitToModel(self):
        pass

    def getModelParameters(self):
        pass

    def fft(self):
        pass

    def minima(self):
        pass

    def maxima(self):
        pass

    def derivative(self):
        pass
    
    def localMaxima(self):
        pass
        
    def localMinima(self):
        pass
        
    def drawable(self):
        pass
        

        
  