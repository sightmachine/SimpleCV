# SimpleCV Color Library
#
# This library is used to modify different color properties of images

#load required libraries
import random
from SimpleCV.base import *
from SimpleCV.ImageClass import * 

  
class Color:
    """
    **SUMMARY**

    Color is a class that stores commonly used colors in a simple
    and easy to remember format, instead of requiring you to remember
    a colors specific RGB value.
    

    **EXAMPLES**

    To use the color in your code you type:
    Color.RED
    
    To use Red, for instance if you want to do a line.draw(Color.RED)
    """
    colorlist = []
    
    #Primary Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)

    LEGO_BLUE = (0,50,150)
    LEGO_ORANGE = (255,150,40)

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
    DEFAULT = (0, 0, 0)
    # These are for the grab cut / findBlobsSmart
    BACKGROUND = (0,0,0)
    MAYBE_BACKGROUND = (64,64,64)
    MAYBE_FOREGROUND =  (192,192,192)
    FOREGROUND = (255,255,255)

    colorlist = [
                BLACK,
                WHITE,                
                BLUE,
                YELLOW,
                RED,                
                VIOLET,
                ORANGE,
                GREEN,
                GRAY,
                IVORY,
                BEIGE,
                WHEAT,
                TAN,
                KHAKI,
                SILVER,
                CHARCOAL,
                NAVYBLUE,
                ROYALBLUE,
                MEDIUMBLUE,
                AZURE,
                CYAN,
                AQUAMARINE,
                TEAL,
                FORESTGREEN,
                OLIVE,
                LIME,
                GOLD,
                SALMON,
                HOTPINK,
                FUCHSIA,
                PUCE,
                PLUM,
                INDIGO,
                MAROON,
                CRIMSON,
                DEFAULT
                ]

    def getRandom(self):
        """
        **SUMMARY**

        Returns a random color in tuple format.

        **RETURNS**
        
        A random color tuple.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> kp = img.findKeypoints()
        >>> for k in kp:
        >>>    k.draw(color=Color.getRandom())
        >>> img.show()

        """
        r = random.randint(1, (len(self.colorlist) - 1))
        return self.colorlist[r]
        
    @classmethod    
    def hsv(cls, tuple):
        """
        **SUMMARY**

        Convert any color to HSV, OpenCV style (0-180 for hue)
        
        **PARAMETERS**
        
        * *tuple* - an rgb tuple to convert to HSV.

        **RETURNS**

        A color tuple in HSV format.

        **EXAMPLE**
        
        >>> c = Color.RED
        >>> hsvc = Color.hsv(c)
        
        
        """
        hsv_float = colorsys.rgb_to_hsv(*tuple)
        return (hsv_float[0] * 180, hsv_float[1] * 255, hsv_float[2])
    
    @classmethod
    def getHueFromRGB(cls, tuple):
        """
        **SUMMARY**

        Get corresponding Hue value of the given RGB values
        
        **PARAMETERS**
        
        * *tuple* - an rgb tuple to convert to HSV.

        **RETURNS**

        floating value of Hue ranging from 0 to 180

        **EXAMPLE**
        
        >>> i = Image("lenna")
        >>> hue = Color.getHueFromRGB(i[100,300])
        
        """
        h_float = colorsys.rgb_to_hsv(*tuple)[0]
        return h_float*180
        
    @classmethod    
    def getHueFromBGR(self,color_tuple):
        """
        **SUMMARY**

        Get corresponding Hue value of the given BGR values
        
        **PARAMETERS**
        
        * *tuple* - a BGR tuple to convert to HSV.

        **RETURNS**

        floating value of Hue ranging from 0 to 180

        **EXAMPLE**
        
        >>> i = Image("lenna")
        >>> color_tuple = tuple(reversed(i[100,300]))
        >>> hue = Color.getHueFromRGB(color_tuple)
        
        """
        a = color_tuple
        print a
        h_float = colorsys.rgb_to_hsv(*tuple(reversed(color_tuple)))[0]
        return h_float*180
        
    @classmethod
    def hueToRGB(self, h):
        """
        **SUMMARY**

        Get corresponding RGB values of the given Hue
        
        **PARAMETERS**
        
        * *int* - a hue int to convert to RGB

        **RETURNS**

        A color tuple in RGB format.

        **EXAMPLE**
        
        >>> c = Color.huetoRGB(0)
        
        """
        h = h/180.0
        r,g,b = colorsys.hsv_to_rgb(h,1,1)
        return (round(255.0*r),round(255.0*g),round(255.0*b))
        
    @classmethod
    def hueToBGR(self,h):
        """
        **SUMMARY**

        Get corresponding BGR values of the given Hue
        
        **PARAMETERS**
        
        * *int* - a hue int to convert to BGR

        **RETURNS**

        A color tuple in BGR format.

        **EXAMPLE**
        
        >>> c = Color.huetoBGR(0)
        
        """
        return(tuple(reversed(self.hueToRGB(h))))
         

class ColorCurve:
    """
    **SUMMARY**

    ColorCurve is a color spline class for performing color correction.  
    It can takeas parameters a SciPy Univariate spline, or an array with at 
    least 4 point pairs.  Either of these must map in a 255x255 space.  The curve 
    can then be used in the applyRGBCurve, applyHSVCurve, and 
    applyInstensityCurve functions.
  
    **EXAMPLE**

    >>> clr = ColorCurve([[0,0], [100, 120], [180, 230], [255, 255]])
    >>> image.applyIntensityCurve(clr)
  
    the only property, mCurve is a linear array with 256 elements from 0 to 255
    """
    mCurve = ""
  
    def __init__(self, curve_vals ):
        inBins = linspace(0, 255, 256)
        if( type(curve_vals) == UnivariateSpline ):
            self.mCurve = curvVals(inBins)
        else: 
            curve_vals = np.array(curve_vals)
            aSpline = UnivariateSpline(curve_vals[:, 0], curve_vals[:, 1], s=1)   
            self.mCurve = aSpline(inBins)
        
        
class ColorMap:
    """
    **SUMMARY**

    A color map takes a start and end point in 3D space and lets you map a range
    of values to it.  Using the colormap like an array gives you the mapped color.

    **EXAMPLE**

    This is useful for color coding elements by an attribute:
    
    >>> blobs = image.findBlobs()
    >>> cm = ColorMap(startcolor = Color.RED, endcolor = Color.Blue, 
    >>>  startmap = min(blobs.area()) , endmap = max(blobs.area())        
    >>>  for b in blobs:
    >>>    b.draw(cm[b.area()])

    """
    startcolor = ()
    endcolor = ()
    startmap = 0
    endmap = 0
    colordistance = 0
    valuerange = 0
    ratios = []
    
    
    def __init__(self, startcolor, endcolor, startmap, endmap):
        self.startcolor = np.array(startcolor)
        self.endcolor = np.array(endcolor)
        self.startmap = float(startmap)
        self.endmap = float(endmap)
        self.valuerange = float(endmap - startmap)
        self.ratios = (self.endcolor - self.startcolor) / self.valuerange
      
    def __getitem__(self, value):
        color = tuple(self.startcolor + (self.ratios * (value - self.startmap)))
        return (int(color[0]), int(color[1]), int(color[2]))
