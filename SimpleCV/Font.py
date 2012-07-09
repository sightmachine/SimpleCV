# SimpleCV Font Library
#
# This library is used to add fonts to images

#load required libraries
from SimpleCV.base import *


class Font:
    """
    The Font class allows you to create a font object to be
    used in drawing or writing to images.
    There are some defaults available, to see them, just type
    Font.printFonts()
    """

    _fontpath = "SimpleCV/fonts/"
    _extension = ".ttf"
    _fontface = "ubuntu"
    _fontsize = 16
    _font = None
    
    # These fonts were downloaded from Google at:
    # http://www.http://www.google.com/webfonts
    _fonts = [
					    "ubuntu",
					    "astloch",
					    "carter_one",
					    "kranky",
					    "la_belle_aurore",
					    "monofett",
					    "reenie_beanie",
					    "shadows_Into_light",
					    "special_elite",
					    "unifrakturmaguntia",
					    "vt323",
					    "wallpoet",
					    "wire_one"
					    ]
    
    
    def __init__(self, fontface = "ubuntu", fontsize = 16):
        """
        This creates a new font object, it uses ubuntu as the default font
        To give it a custom font you can just pass the absolute path
        to the truetype font file.
        """
        self.setSize(fontsize)
        self.setFont(fontface)
        
    
    def getFont(self):
        """
        Get the font from the object to be used in drawing
        
        Returns: PIL Image Font
        """
        return self._font
    
    def setFont(self, new_font = 'ubuntu'):
        """
        Set the name of the font listed in the font family
        if the font isn't listed in the font family then pass it the absolute
        path of the truetype font file.
        Example: Font.setFont("/home/simplecv/my_font.ttf")
        """
        if isinstance(new_font, basestring):
            print "Please pass a string"
            return None
	        
        if find(new_font, self._fonts):
            self._fontface = new_font
            font_to_use = self._fontpath + self._fontface + "/" + self._fontface + self._extension
        else:
            self._fontface = new_font
            font_to_use = new_font
	        
        self._font = pilImageFont.truetype(font_to_use, self._fontsize)
    
    def setSize(self, size):
        """
        Set the font point size. i.e. 16pt
        """
        print type(size)
        if type(size) == int:
            self._fontsize = size
        else:
            print "please provide an integer"
    
    def getSize(self):
        """
        Gets the size of the current font
        
        Returns: Integer
        """
        
        return self._fontsize
    
    def getFonts(self):
        """
        This returns the list of fonts built into SimpleCV
        """
        
        return self._fonts
    
    def printFonts(self):
        """
        This prints a list of fonts built into SimpleCV
        """
        
        for f in self._fonts:
            print f
	    
