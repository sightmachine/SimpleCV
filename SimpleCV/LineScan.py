from SimpleCV.base import *
from SimpleCV.Color import *
import copy


class LineScan(list):

    pointLoc = None
    image = None
    
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


    def smooth(self,degree=3):
        """
        Do a simple smoothing operation
        cribbed from http://www.swharden.com/blog/2008-11-17-linear-data-smoothing-in-python/

        """
        window=degree*2-1  
        weight=np.array([1.0]*window)  
        weightGauss=[]  
        for i in range(window):  
            i=i-degree+1  
            frac=i/float(window)    
            gauss=1/(np.exp((4*(frac))**2))    
            weightGauss.append(gauss) 
        weight=np.array(weightGauss)*weight   
        smoothed=[0.0]*(len(self)-window)  
        for i in range(len(smoothed)):  
            smoothed[i]=sum(np.array(self[i:i+window])*weight)/sum(weight)
        # recenter the signal so it sits nicely on top of the old
        front = self[0:(degree-1)]
        front += smoothed
        front += self[-1*degree:]
        retVal = LineScan(front)
        retVal.image = self.image
        retVal.pointLoc = self.pointLoc
        return retVal

    def normalize(self):
        temp = np.array(self, dtype='float32')
        temp = temp / np.max(temp)
        retVal = LineScan(list(temp[:]))
        retVal.image = self.image
        retVal.pointLoc = self.pointLoc
        return retVal

    def scale(self,value_range=(0,1)):
        temp = np.array(self, dtype='float32')
        vmax = np.max(temp)
        vmin = np.min(temp)
        a = np.min(value_range)
        b = np.max(value_range)
        temp = (((b-a)/(vmax-vmin))*(temp-vmin))+a
        retVal = LineScan(list(temp[:]))
        retVal.image = self.image
        retVal.pointLoc = self.pointLoc
        return retVal

    def minima(self):
        # all of these functions should return
        # value, index, pixel coordinate
        # [(value,index,(pix_x,pix_y))...]        
        minvalue = np.min(self)
        idxs = np.where(np.array(self)==minvalue)[0]
        minvalue = np.ones((1,len(idxs)))*minvalue # make zipable
        minvalue = minvalue[0]
        pts = np.array(self.pointLoc)
        pts = pts[idxs]
        pts = [(p[0],p[1]) for p in pts] # un numpy this shit
        return zip(minvalue,idxs,pts)
        
    def maxima(self):
        pass

    def derivative(self):
        pass
    
    def localMaxima(self):
        pass
        
    def localMinima(self):
        pass

        
    def resample(self):
        pass
        

    def fitToModel(self):
        pass

    def getModelParameters(self):
        pass

    def fft(self):
        pass

        
    def drawable(self):
        pass
        

        
  