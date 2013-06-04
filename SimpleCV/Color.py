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
    WATERSHED_FG = (255,255,255) # Watershed foreground
    WATERSHED_BG = (128,128,128) # Watershed background
    WATERSHED_UNSURE = (0,0,0) # Watershed either fg or bg color
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

    @classmethod
    def getRandom(cls):
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
        r = random.randint(1, (len(cls.colorlist) - 1))
        return cls.colorlist[r]

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

    @classmethod
    def getAverageRGB(self,rgb):
        """
        **SUMMARY**

        Get the average of the R,G,B values

        **PARAMETERS**

        * *rgb* - a tuple of RGB values

        **RETURNS**

        Average value of RGB

        **EXAMPLE**

        >>> c = Color.getAverageRGB((22,35,230))

        """
        return int(((rgb[0]+rgb[1]+rgb[2])/3))

    @classmethod
    def getLightness(self,rgb):
        """
        **SUMMARY**

        Calculates the grayscale value of R,G,B according to Lightness Method

        **PARAMETERS**

        * *rgb* - a tuple of RGB values

        **RETURNS**

        Grayscale value according to the Lightness Method

        **EXAMPLE**

        >>> c = Color.getLightness((22,35,230))

        **NOTES**
        
        Lightness Method: value = (max(R,G,B)+min(R,G,B))/2

        """
        return int(((max(rgb)+min(rgb))/2))

    @classmethod
    def getLuminosity(self,rgb):
        """
        **SUMMARY**

        Calculates the grayscale value of R,G,B according to Luminosity Method

        **PARAMETERS**

        * *rgb* - a tuple of RGB values

        **RETURNS**

        Grayscale value according to the Luminosity Method

        **EXAMPLE**

        >>> c = Color.getLuminosity((22,35,230))

        **NOTES**
        
        Luminosity Method: value = 0.21*R + 0.71*G + 0.07*B

        """
        return int((0.21*rgb[0] + 0.71*rgb[1] + 0.07*rgb[2]))

class ColorCurve:
    """
    **SUMMARY**

    ColorCurve is a color spline class for performing color correction.
    It can takeas parameters a SciPy Univariate spline, or an array with at
    least 4 point pairs.  Either of these must map in a 255x255 space.  The curve
    can then be used in the applyRGBCurve, applyHSVCurve, and
    applyInstensityCurve functions.
    
    Note:
    The points should be in strictly increasing order of their first elements
    (X-coordinates)

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
            #nothing above 255, nothing below 0
            self.mCurve = np.maximum(np.minimum(aSpline(inBins),255),0) 


class ColorMap:
    """
    **SUMMARY**

    A ColorMap takes in a tuple of colors along with the start and end points
    and it lets you map colors with a range of numbers.

    If only one Color is passed second color by default is set to White

    **PARAMETERS**

    * *color* - Tuple of colors which need to be mapped

    * *startmap* * - This is the starting of the range of number with which we map the colors

    * *endmap* * - This is the end of the range of the nmber with which we map the colors

    **EXAMPLE**

    This is useful for color coding elements by an attribute:

    >>> blobs = image.findBlobs()
    >>> cm = ColorMap(color = (Color.RED,Color.YELLOW,Color.BLUE),min(blobs.area()),max(blobs.area()))
    >>>  for b in blobs:
    >>>    b.draw(cm[b.area()])

    """
    color = ()
    endcolor = ()
    startmap = 0
    endmap = 0
    colordistance = 0
    valuerange = 0


    def __init__(self, color, startmap, endmap):
        self.color = np.array(color)
        if self.color.ndim == 1:  # To check if only one color was passed
            color = ((color[0],color[1],color[2]),Color.WHITE)
            self.color = np.array(color)
        self.startmap = float(startmap)
        self.endmap = float(endmap)
        self.valuerange = float(endmap - startmap) #delta
        self.colordistance = self.valuerange / float(len(self.color)-1) #gap between colors

    def __getitem__(self, value):
        if value > self.endmap:
            value = self.endmap
        elif value < self.startmap:
            value = self.startmap
        val = (value - self.startmap)/self.colordistance
        alpha = float(val - int(val))
        index = int(val)
        if index == len(self.color)-1:
            color = tuple(self.color[index])
            return (int(color[0]), int(color[1]), int(color[2]))
        color = tuple(self.color[index] * (1-alpha) + self.color[index+1] * (alpha))
        return (int(color[0]), int(color[1]), int(color[2]))
