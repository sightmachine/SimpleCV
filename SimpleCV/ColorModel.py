# SimpleCV Color Model Library
#load required libraries
from SimpleCV.base import *
from SimpleCV.ImageClass import * 
from pickle import *

class ColorModel:
    """
    The color model is used to model the color of foreground and background objects
    by using an example. The color model is trained by passing either color tuples
    or images to learn from. The color model uses whatever color space the input imagery
    is in. 
    """
    #TODO: Discretize the colorspace into smaller intervals,eg r=[0-7][8-15] etc
    #TODO: Work in HSV space
    mIsBackground = True
    mData = {}
    
    def __init__(self, isBackground=True):
        self.mIsBackground = isBackground
        self.mData = {}
  
  
    def _makeCanonical(self, data):
        """
        Turn input types in a common form used by the rest of the class -- a
        4-bit shifted list of unique colors
        """ 
        ret = ''
        
        #first cast everything to a numpy array
        if(data.__class__.__name__ == 'Image'):
            ret =  np.array(data.toBGR().getMatrix()).reshape(-1, 3)
        elif(data.__class__.__name__ == 'cvmat'):
            ret = np.array(data).reshape(-1, 3)
        elif(data.__class__.__name__ == 'list'  ):
            ret = np.array(data)
        elif (data.__class__.__name__=='tuple'):
            ret = np.array(data)
        else:
            warnings.warn("ColorModel: color is not in an accepted format!")
            return None
    
        return ret.right_shift(4).unique()
  
    def addToModel(self, data):
        """
        Add an image, array, or tuple to the color model.
        Note that this operation can be slow on large images, and is insensitive
        to colorspace (RGB vs HSV)
        """
        data = self._makeCanonical(data)
        if( type(data) != None ):
            for i in data:
                self.mData[tuple(i)] = 1
  
    def removeFromModel(self, data):
        """
        Remove an image, array, or tuple from the model.
        """    
        data = self._makeCanonical(data)
        for i in data:
            if tuple(i) in self.mData:
                del self.mData[tuple(i)]
  
    def thresholdImage(self, img):
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
        mask = img.getEmpty(1)
        for x in range(img.width):
            for y in range(img.height):
                #do the bit shift on the pixels
                test = tuple(img[x, y])
                pix = (int(test[0]) >> 4, int(test[1]) >> 4, int(test[2]) >> 4)
                if pix  in self.mData:
                    mask[y, x] = a
                else:
                    mask[y, x] = b    
        return Image(mask)
    
    def containsColor(self, c):
        """
        Return true if a particular color is in our color model. 
        """
        retVal = False
        test = (int(c[0]) >> 4, int(c[1]) >> 4, int(c[2]) >> 4)
        if test in self.mData:
            retVal = True
        return retVal
    
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
      
    def loadFromFile(self, filename):
        """
        Dump the color model to the specified file.
        """
        self.mData =  load(open(filename))
    
    def saveToFile(self, filename):
        """
        Read a dumped color model file. 
        """
        dump(self.mData, open(filename, "wb"))
      
