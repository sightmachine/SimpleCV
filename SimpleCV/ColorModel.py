# SimpleCV Color Model Library
#load required libraries
from SimpleCV.base import *
from SimpleCV.ImageClass import * 
from pickle import *

class ColorModel:
    """
    The color model is used to model the color of foreground and background objects
    by using a a training set of images.
    
    You can create the color model with any number of "training" images, or
    add images to the model with add() and remove().  Then for your data images,
    you can useThresholdImage() to return a segmented picture.
    
    """
    #TODO: Discretize the colorspace into smaller intervals,eg r=[0-7][8-15] etc
    #TODO: Work in HSV space
    mIsBackground = True
    mData = {}
    
    def __init__(self, data = None, isBackground=True):
        self.mIsBackground = isBackground
        self.mData = {}
        
        if data:
            try:
                [ self.add(d) for d in data ]
            except TypeError:
                self.add(data)
  
  
    def _makeCanonical(self, data):
        """
        Turn input types in a common form used by the rest of the class -- a
        4-bit shifted list of unique colors
        """ 
        ret = ''
        
        #first cast everything to a numpy array
        if(data.__class__.__name__ == 'Image'):
            ret =  data.getNumpy().reshape(-1, 3)
        elif(data.__class__.__name__ == 'cvmat'):
            ret = np.array(data).reshape(-1, 3)
        elif(data.__class__.__name__ == 'list'  ):
            ret = np.array(data)
        elif (data.__class__.__name__=='tuple'):
            ret = np.array([data])
        else:
            warnings.warn("ColorModel: color is not in an accepted format!")
            return None
    
        rs = np.right_shift(ret, 4)  #right shift 4 bits
        
        uniques = np.unique(rs.view([('',rs.dtype)]*rs.shape[1])).view(rs.dtype).reshape(-1, 3)
        #create a unique set of colors.  I had to look this one up
        
        #create a dict of encoded strings
        return dict.fromkeys(map(np.ndarray.tostring, uniques), 1)
  
    def add(self, data):
        """
        Add an image, array, or tuple to the color model.
        """
        self.mData.update(self._makeCanonical(data))
  
    def remove(self, data):
        """
        Remove an image, array, or tuple from the model.
        """
        self.mData = dict.fromkeys(set(self.mData) ^ set(self._makeCanonical(data)), 1)
  
    def threshold(self, img):
        """
        Perform a threshold operation on the given image. This involves iterating
        over the image and comparing each pixel to the model. If the pixel is in the
        model it is set to be either the foreground (white) or background (black) based
        on the setting of mIsBackground.
        """
        a = 0
        b = 255
        if( self.mIsBackground == False ):
            a = 255
            b = 0
        
        rs = np.right_shift(img.getNumpy(), 4).reshape(-1, 3) #bitshift down and reshape to Nx3
        mapped = np.array(map(self.mData.has_key, map(np.ndarray.tostring, rs))) #map to True/False based on the model
        thresh = np.where(mapped, a, b) #replace True and False with fg and bg
        return Image(thresh.reshape(img.width, img.height))
    
    def contains(self, c):
        """
        Return true if a particular color is in our color model. 
        """
        #reverse the color, cast to uint8, right shift, convert to string, check dict
        return self.mData.has_key(np.right_shift(np.cast['uint8'](c[::-1]), 4).tostring())
    
    def setIsForeground(self):
        """
        Set our model as being foreground imagery.
        """    
        mIsBackground = False
      
    def setIsBackground(self):
        """
        Set our model as being background imager. 
        """
        mIsBackground = True
      
    def load(self, filename):
        """
        Dump the color model to the specified file.
        """
        self.mData =  load(open(filename))
    
    def save(self, filename):
        """
        Read a dumped color model file. 
        """
        dump(self.mData, open(filename, "wb"))
      
