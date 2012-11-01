from SimpleCV.base import *
from SimpleCV.Color import *
import scipy.signal as sps
import scipy.optimize as spo

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
        # [(index,value,(pix_x,pix_y))...]        
        minvalue = np.min(self)
        idxs = np.where(np.array(self)==minvalue)[0]
        minvalue = np.ones((1,len(idxs)))*minvalue # make zipable
        minvalue = minvalue[0]
        pts = np.array(self.pointLoc)
        pts = pts[idxs]
        pts = [(p[0],p[1]) for p in pts] # un numpy this shit
        return zip(idxs,minvalue,pts)
        
    def maxima(self):
        # all of these functions should return
        # value, index, pixel coordinate
        # [(index,value,(pix_x,pix_y))...]        
        maxvalue = np.max(self)
        idxs = np.where(np.array(self)==maxvalue)[0]
        maxvalue = np.ones((1,len(idxs)))*maxvalue # make zipable
        maxvalue = maxvalue[0]
        pts = np.array(self.pointLoc)
        pts = pts[idxs]
        pts = [(p[0],p[1]) for p in pts] # un numpy this shit
        return zip(idxs,maxvalue,pts)
 
    def derivative(self):
        temp = np.array(self,dtype='float32')
        d = [0]
        d += list(temp[1:]-temp[0:-1])
        retVal = LineScan(d)
        retVal.image = self.image
        retVal.pointLoc = self.pointLoc
        return retVal
    
    def localMaxima(self):
        temp = np.array(self)
        idx = np.r_[True, temp[1:] > temp[:-1]] & np.r_[temp[:-1] > temp[1:], True]
        idx = np.where(idx==True)[0]
        values = temp[idx]
        pts = np.array(self.pointLoc)
        pts = pts[idx]
        pts = [(p[0],p[1]) for p in pts] # un numpy this shit
        return zip(idx,values,pts)

        
    def localMinima(self):
        temp = np.array(self)
        idx = np.r_[True, temp[1:] < temp[:-1]] & np.r_[temp[:-1] < temp[1:], True]
        idx = np.where(idx==True)[0]
        values = temp[idx]
        pts = np.array(self.pointLoc)
        pts = pts[idx]
        pts = [(p[0],p[1]) for p in pts] # un numpy this shit
        return zip(idx,values,pts)

    def resample(self,n=100):
        signal = sps.resample(self,n)
        pts = np.array(self.pointLoc)
        # we assume the pixel points are linear
        # so we can totally do this better manually 
        x = linspace(pts[0,0],pts[-1,0],n)
        y = linspace(pts[0,1],pts[-1,1],n)
        pts = zip(x,y)
        retVal = LineScan(list(signal))
        retVal.image = self.image
        retVal.pointLoc = pts
        return retVal


    # this needs to be moved out to a cookbook or something
    def linear(xdata,m,b):
        return m*xdata+b

    # need to add polyfit too
    http://docs.scipy.org/doc/numpy/reference/generated/numpy.polyfit.html
    def fitToModel(self,f,p0=None):
        yvals = np.array(self,dtype='float32')
        xvals = range(0,len(yvals),1)
        popt,pcov = spo.curve_fit(f,xvals,yvals,p0=p0)
        yvals = f(xvals,*popt)
        retVal = LineScan(list(yvals))
        retVal.image = self.image
        retVal.pointLoc = self.pointLoc
        return retVal


    def getModelParameters(self,f,p0=None):
        yvals = np.array(self,dtype='float32')
        xvals = range(0,len(yvals),1)
        popt,pcov = spo.curve_fit(f,xvals,yvals,p0=p0)
        return popt

