# SimpleCV Color Library
#
# This library is used to modify different color properties of images

#load required libraries
from SimpleCV.base import *
from SimpleCV.ImageClass import Image 

class Color:
  """
  Color is a class that stores commonly used colors in a simple
  and easy to remember format, instead of requiring you to remember
  a colors specific RGB value.
  
  To use the color in your code you type:
  Color.RED
  
  To use Red, for instance if you want to do a line.draw(Color.RED)
  """
  #Primary Colors
  BLACK = (0, 0, 0)
  WHITE = (255, 255, 255)
  
  BLUE = (0, 0, 255)
  YELLOW = (255, 255, 0)
  RED = (255, 0, 0)
  
  VIOLET = (181, 126, 220)
  ORANGE = (255, 165, 0)
  GREEN = (0, 128, 0)
  GRAY = (128, 128, 128)

  
  #Extended Colors
  IVORY = (255, 255, 240)
  BEIGE = (245, 245, 220)
  WHEAT = (245, 222, 179)
  TAN = (210, 180, 140)
  KHAKI = (195, 176, 145)
  SILVER = (192, 192, 192)
  CHARCOAL = (70, 70, 70)
  NAVYBLUE = (0, 0, 128)
  ROYALBLUE = (8, 76, 158)
  MEDIUMBLUE = (0, 0, 205)
  AZURE = (0, 127, 255)
  CYAN = (0, 255, 255)
  AQUAMARINE = (127, 255, 212)
  TEAL = (0, 128, 128)
  FORESTGREEN = (34, 139, 34)
  OLIVE = (128, 128, 0)
  LIME = (191, 255, 0)
  GOLD = (255, 215, 0)
  SALMON = (250, 128, 114)
  HOTPINK = (252, 15, 192)
  FUCHSIA = (255, 119, 255)
  PUCE = (204, 136, 153)
  PLUM = (132, 49, 121)
  INDIGO = (75, 0, 130)
  MAROON = (128, 0, 0)
  CRIMSON = (220, 20, 60)
  
  


class ColorCurve:
  """
  ColorCurve is a color spline class for performing color correction.  
  It can takeas parameters a SciPy Univariate spline, or an array with at 
  least 4 point pairs.  Either of these must map in a 255x255 space.  The curve 
  can then be used in the applyRGBCurve, applyHSVCurve, and 
  applyInstensityCurve functions::

    clr = ColorCurve([[0,0], [100, 120], [180, 230], [255, 255]])
    image.applyIntensityCurve(clr)

  the only property, mCurve is a linear array with 256 elements from 0 to 255
  """
  mCurve =""

  def __init__(self, curve_vals ):
    inBins = linspace(0,255,256)
    if( type(curve_vals) == UnivariateSpline ):
      self.mCurve = curvVals(inBins)
    else: 
      curve_vals = np.array(curve_vals)
      aSpline = UnivariateSpline( curve_vals[:,0],curve_vals[:,1],s=1)   
      self.mCurve = aSpline(inBins)
      
class ColorModel:
  """
  """
  mIsColor = True
  mIsBackground = True
  mData = []
  
  def __init__(self,isColor=True,isBackground=True):
    mIsColor = isColor
    mIsBackground = isBackground

  def _makeCanonical(self,data):
    if(data.__class__.__name__=='Image'):
      rs = np.array(data.getMatrix()).reshape(-1, 3)
      retVal = np.unique(rs.view([('',rs.dtype)]*rs.shape[1])).view(rs.dtype).reshape(-1,rs.shape[1])
    elif(data.__class__.__name__=='cvmat'):
      rs = np.array(data).reshape(-1, 3)
      retVal = np.unique(rs.view([('',rs.dtype)]*rs.shape[1])).view(rs.dtype).reshape(-1,rs.shape[1])    
    elif(data.__class__.__name__=='Color'):
      retVal = np.array([data])
    elif(data.__class__.__name__=='ndarray'):
      #assume the shape is correct
      retVal = np.unique(data.view([('',data.dtype)]*data.shape[1])).view(data.dtype).reshape(-1,data.shape[1])
    elif(data.__class__.__name__=='list'  ):
      retVal = np.array(data)
    else:
      warnings.warn("ColorModel: color is not in an accepted format!")
      retVal = None
      
    return retVal
  
  def addToModel(self,data):
    data =self._makeCanonical(data)
    if( type(data) != None ):
      if( len(self.mData) == 0 ): #no data yet
        self.mData = np.unique(data.view([('',data.dtype)]*data.shape[1])).view(data.dtype).reshape(-1,data.shape[1])
      else:
        self.mData = np.concatenate((self.mData,data))
        self.mData = np.unique(self.mData.view([('',self.mData.dtype)]*self.mData.shape[1])).view(self.mData.dtype).reshape(-1,self.mData.shape[1])
    
    
  def removeFromModel(self,data):
    data =self._makeCanonical(data)
    self.mData = np.remove(self.mData.view([('',self.mData.dtype)]*self.mData.shape[1]),data.view([('',data.dtype)]*data.shape[1])).view(self.mData.dtype).reshape(-1,self.mData.shape[1])
  
  def thresholdImage(self,img):
    a = 255
    b = 0
    if( self.mIsBackground == False ):
      a = 0
      b = 255
    mask = img.getEmpty(1)
    l = self.mData.tolist()
    for x in range(img.width):
      for y in range(img.height):
        vals  = -1
        try:
          vals = l.index(img.getPixel(x,y))
        except ValueError:
          pass
        #vals = np.intersect1d(self.mData, img.getPixel(x,y) ) #(np.where(spsd.cdist(self.mData,[img[x,y]])<=threshold))
        if(vals >= 0):
          mask[y,x] = a
        else:
          mask[y,x] = b
    return Image(mask)
  
  def containsColor(self,c):
    retVal = False
    val = np.where(spsd.cdist(self.mData,[c])==0.00)
    if( val[0].shape[0] > 0 ):
      retVal = True;
    return retVal
  
  def setIsForeground(self):
    mIsBackground = False
    
  def setIsBackground(self):
    mIsBackground = True
    
  def loadFromFile(self,filename):
    self.mData = np.loadtxext(filename)
  
  def saveToFile(self,filename):
    np.savetxt(filename,self.mData)
  
  

  