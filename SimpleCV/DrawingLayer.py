#!/usr/bin/env python

import sys
import os
#from SimpleCV.base import *
from SimpleCV.Color import *
#from SimpleCV import *
from numpy import int32
from numpy import uint8
from pygame import gfxdraw
try:
    import pygame as pg
    
#DOCS
#TESTS
#IMAGE AGNOSTIC
#RESIZE
#ADD IMAGE INTERFACE

except ImportError:
    raise ImportError('Error Importing Pygame/surfarray')

class DrawingLayer:
    """
    DrawingLayer gives you a way to mark up Image classes without changing
    the image data itself. This class wraps pygame's Surface class and
    provides basic drawing and text rendering functions


    Example:
    image = Image("/path/to/image.png")
    image2 = Image("/path/to/image2.png")
    image.dl().blit(image2) #write image 2 on top of image
    """
    _mSurface = []
    _mDefaultColor = 0
    _mFontColor = 0
    _mClearColor = 0
    _mFont = 0
    _mFontName = ""
    _mFontSize = 0
    _mDefaultAlpha = 255
    width = 0
    height = 0

    def __init__(self, (width, height)):
        #pg.init()  
        if( not pg.font.get_init() ):
            pg.font.init()
            
        self.width = width
        self.height = height
        self._mSurface = pg.Surface((width, height), flags = pg.SRCALPHA)
        self._mDefaultAlpha = 255
        self._mClearColor = pg.Color(0, 0, 0, 0)
        
        self._mSurface.fill(self._mClearColor)
        self._mDefaultColor = Color.BLACK

        self._mFontSize = 18
        self._mFontName = None
        self._mFont = pg.font.Font(self._mFontName, self._mFontSize)    
    
     
    def setDefaultAlpha(self, alpha):
        """
        This method sets the default alpha value for all methods called on this
        layer. The default value starts out at 255 which is completely transparent.
        """
        if(alpha >= 0 and alpha <= 255 ):
            self._mDefaultAlpha = alpha 
        return None
    
    def getDefaultAlpha(self):
        """
        Returns the default alpha value. 
        """ 
        return self._mDefaultAlpha

    def setLayerAlpha(self, alpha):
        """
        This method sets the alpha value of the entire layer in a single
        pass. This is helpful for merging layers with transparency.
        """
        self._mSurface.set_alpha(alpha)
        # Get access to the alpha band of the image.
        pixels_alpha = pg.surfarray.pixels_alpha(self._mSurface)
        # Do a floating point multiply, by alpha 100, on each alpha value.
        # Then truncate the values (convert to integer) and copy back into the surface.
        pixels_alpha[...] = (pixels_alpha * (alpha / 255.0)).astype(np.uint8)
        # Unlock the surface.
        
        del pixels_alpha        
        return None
    
    def _getSurface(self):
        return(self._mSurface)
        
    def _csvRGB2pgColor(self, color, alpha = -1):
        if(alpha == -1):
            alpha = self._mDefaultAlpha

        if(color == Color.DEFAULT):
            color = self._mDefaultColor
        retVal = pg.Color(color[0], color[1], color[2], alpha)
        return retVal
    
    def setDefaultColor(self, color):
        """
        This method sets the default rendering color. 
        """
        self._mDefaultColor = color
        
    def line(self, start, stop, color = Color.DEFAULT, width = 1, antialias = True, alpha = -1 ):
        """
        Draw a single line from the (x,y) tuple start to the (x,y) tuple stop.
        Optional parameters:
        
        color - The object's color as a simple CVColor object, if no value  is sepcified
                the default is used.
        
        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent. 
        
        width - The line width in pixels. 
        
        antialias - Draw an antialiased object of width one.
        
        """
        if(antialias and width == 1):           
            pg.draw.aaline(self._mSurface, self._csvRGB2pgColor(color, alpha), start, stop, width)
        else:
            pg.draw.line(self._mSurface, self._csvRGB2pgColor(color, alpha), start, stop, width)        
        return None
    
    def lines(self, points, color = Color.DEFAULT, antialias = True, alpha = -1, width = 1 ):
        """
        Draw a set of lines from the list of (x,y) tuples points. Lines are draw
        between each successive pair of points.
        
        Optional parameters:
        
        color - The object's color as a simple CVColor object, if no value  is sepcified
                the default is used.
        
        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent. 
        
        width - The line width in pixels. 
        
        antialias - Draw an antialiased object of width one.
        """        
        if(antialias and width == 1):
            pg.draw.aalines(self._mSurface, self._csvRGB2pgColor(color, alpha), 0, points, width)
        else:
            pg.draw.lines(self._mSurface, self._csvRGB2pgColor(color, alpha), 0, points, width)                
        return None
    
    #need two points(TR,BL), center+W+H, and TR+W+H
    def rectangle(self, topLeft, dimensions, color = Color.DEFAULT, width = 1, filled = False, alpha = -1 ):
        """
        Draw a rectangle given the topLeft the (x,y) coordinate of the top left
        corner and dimensions (w,h) tge width and height
        
        color - The object's color as a simple CVColor object, if no value  is sepcified
                the default is used.
        
        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent. 
        
        w -     The line width in pixels. This does not work if antialiasing is enabled.
        
        filled -The rectangle is filled in 
        """
        if(filled):
            width = 0
        r = pg.Rect((topLeft[0], topLeft[1]), (dimensions[0], dimensions[1]))
        pg.draw.rect(self._mSurface, self._csvRGB2pgColor(color, alpha), r, width)
        return None
 
   
    def centeredRectangle(self, center, dimensions, color = Color.DEFAULT, width = 1, filled = False, alpha = -1 ):
        """
        Draw a rectangle given the center (x,y) of the rectangle and dimensions (width, height)
        
        color - The object's color as a simple CVColor object, if no value  is sepcified
                the default is used.
        
        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent. 
        
        w -     The line width in pixels. This does not work if antialiasing is enabled.
        
        filled -The rectangle is filled in 
        """
        if(filled):
            width = 0
        xtl = center[0] - (dimensions[0] / 2)
        ytl = center[1] - (dimensions[1] / 2)
        r = pg.Rect(xtl, ytl, dimensions[0], dimensions[1])
        pg.draw.rect(self._mSurface, self._csvRGB2pgColor(color, alpha), r, width)
        return None    
    
    
    def polygon(self, points, color = Color.DEFAULT, width = 1, filled = False, antialias = True, alpha = -1):
        """
        Draw a polygon from a list of (x,y)
        
        color - The object's color as a simple CVColor object, if no value  is sepcified
                the default is used.
        
        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent. 
        
        width - The 
        width in pixels. This does not work if antialiasing is enabled.
        
        filled -The object is filled in
        
        antialias - Draw the edges of the object antialiased. Note this does not work when the object is filled. 
        """    
        if(filled):
            width = 0
        if(not filled):
            if(antialias and width == 1):
                pg.draw.aalines(self._mSurface, self._csvRGB2pgColor(color, alpha), True, points, width)
            else:
                pg.draw.lines(self._mSurface, self._csvRGB2pgColor(color, alpha), True, points, width)
        else:
            pg.draw.polygon(self._mSurface, self._csvRGB2pgColor(color, alpha), points, width)
        return None
    
    def circle(self, center, radius, color = Color.DEFAULT, width = 1, filled = False, alpha = -1, antialias = True):
        """
        Draw a circle given a location and a radius. 
        
        color - The object's color as a simple CVColor object, if no value  is sepcified
                the default is used.
        
        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent. 
        
        width - The line width in pixels. This does not work if antialiasing is enabled.
        
        filled -The object is filled in
        """           
        if(filled):
            width = 0
        if antialias == False or width > 1:
            pg.draw.circle(self._mSurface, self._csvRGB2pgColor(color, alpha), center, radius, width)
        else:
            pg.gfxdraw.aacircle(self._mSurface, center[0], center[1], radius, self._csvRGB2pgColor(color, alpha))
        return None
    
    def ellipse(self, center, dimensions, color = Color.DEFAULT, width = 1, filled = False, alpha = -1):
        """
        Draw an ellipse given a location and a dimensions. 
        
        color - The object's color as a simple CVColor object, if no value  is sepcified
                the default is used.
        
        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent. 
        
        width - The line width in pixels. This does not work if antialiasing is enabled.
        
        filled -The object is filled in
        """          
        if(filled):
            width = 0
        r = pg.Rect(center[0] - (dimensions[0] / 2), center[1] - (dimensions[1] / 2), dimensions[0], dimensions[1])
        pg.draw.ellipse(self._mSurface, self._csvRGB2pgColor(color, alpha), r, width)
        return None
    
    def bezier(self, points, steps, color = Color.DEFAULT, alpha = -1):
        """
        Draw a bezier curve based on a control point and the a number of stapes 
        
        color - The object's color as a simple CVColor object, if no value  is sepcified
                the default is used.
        
        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent. 
        
        """      
        pg.gfxdraw.bezier(self._mSurface, points, steps, self._csvRGB2pgColor(color, alpha))
        return None
        
    def setFontBold(self, doBold):
        """
        This method sets and unsets the current font to be bold. 
        """
        self._mFont.set_bold(doBold)
        return None

    def setFontItalic(self, doItalic):
        """
        This method sets and unsets the current font to be italic. 
        """
        self._mFont.set_italic(doItalic)
        return None
    
    def setFontUnderline(self, doUnderline):
        """
        This method sets and unsets the current font to be underlined 
        """
        self._mFont.set_underline(doUnderline)
        return None
    
    def selectFont(self, fontName):
        """
        This method attempts to set the font from a font file. It is advisable
        to use one of the fonts listed by the listFonts() method. The input
        is a string with the font name. 
        """
        fullName = pg.font.match_font(fontName)
        self._mFontName = fullName
        self._mFont = pg.font.Font(self._mFontName, self._mFontSize)
        return None
        
    def listFonts(self):
        """
        This method returns a list of strings corresponding to the fonts available
        on the current system. 
        """
        return pg.font.get_fonts()

    
    def setFontSize(self, sz):
        """
        This method sets the font size roughly in points. A size of 10 is almost
        too small to read. A size of 20 is roughly 10 pixels high and a good choice. 
        """
        self._mFontSize = sz
        self._mFont = pg.font.Font(self._mFontName, self._mFontSize)
        return None
    
    def text(self, text, location, color = Color.DEFAULT, alpha = -1):
        """
        Write the a text string at a given location
        
        text -  A text string to print.
        
        location-The location to place the top right corner of the text
        
        color - The object's color as a simple CVColor object, if no value  is sepcified
                the default is used.
        
        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent. 
        
        """
        if(len(text)<0):
            return None
        tsurface = self._mFont.render(text, True, self._csvRGB2pgColor(color, alpha))
        if(alpha == -1):
            alpha = self._mDefaultAlpha
        #this is going to be slow, dumb no native support.
        #see http://www.mail-archive.com/pygame-users@seul.org/msg04323.html
        # Get access to the alpha band of the image.
        pixels_alpha = pg.surfarray.pixels_alpha(tsurface)
        # Do a floating point multiply, by alpha 100, on each alpha value.
        # Then truncate the values (convert to integer) and copy back into the surface.
        pixels_alpha[...] = (pixels_alpha * (alpha / 255.0)).astype(np.uint8)
        # Unlock the surface.
        del pixels_alpha
        self._mSurface.blit(tsurface, location)        
        return None        

    def textDimensions(self, text):
        """
        The textDimensions function takes a string and returns the dimensions (width, height)
        of this text being rendered on the screen.
        """
        tsurface = self._mFont.render(text, True, self._csvRGB2pgColor(Color.WHITE, 255))
        return (tsurface.get_width(), tsurface.get_height())
    
    def ezViewText(self, text, location, fgcolor = Color.WHITE, bgcolor = Color.BLACK):
        """
        ezViewText works just like text but it sets both the foreground and background
        color and overwrites the image pixels. Use this method to make easily
        viewable text on a dynamic video stream.
        
        fgcolor - The color of the text. 
        
        bgcolor - The background color for the text are. 
        """
        if(len(text)<0):
            return None
        alpha = 255
        tsurface = self._mFont.render(text, True, self._csvRGB2pgColor(fgcolor, alpha), self._csvRGB2pgColor(bgcolor, alpha))
        self._mSurface.blit(tsurface, location)        
        return None

    def sprite(self,img,pos=(0,0),scale=1.0,rot=0.0,alpha=255):
        """
        sprite draws a sprite (a second small image) onto the current layer.
        The sprite can be loaded directly from a supported image file like a
        gif, jpg, bmp, or png, or loaded as a surface or SCV image.
        
        pos - the (x,y) position of the upper left hand corner of the sprite

        scale - a scale multiplier as a float value. E.g. 1.1 makes the sprite 10% bigger
        
        rot = a rotation angle in degrees
        
        alpha = an alpha value 255=opaque 0=transparent. 
        """
        if(img.__class__.__name__=='str'):
            image = pg.image.load(img, "RGB")
        else:
            image = img # we assume we have a surface
        image = image.convert(self._mSurface)
        if(rot != 0.00):    
            image = pg.transform.rotate(image,rot)
        if(scale != 1.0):
            image = pg.transform.scale(image,(int(image.get_width()*scale),int(image.get_height()*scale)))
        pixels_alpha = pg.surfarray.pixels_alpha(image)
        pixels_alpha[...] = (pixels_alpha * (alpha / 255.0)).astype(np.uint8)
        del pixels_alpha
        self._mSurface.blit(image,pos)

        
    def blit(self, img, coordinates = (0,0)):
      """
Blit one image onto the drawing layer at upper left coordinates
      """
      
      #can we set a color mode so we can do a little bit of masking here?
      self._mSurface.blit(img.getPGSurface(), coordinates)
        
    def replaceOverlay(self, overlay):
        """
        This method allows you to set the surface manually. 
        """
        self._mSurface = overlay
        return None
    
    #get rid of all drawing
    def clear(self):
        """
        This method removes all of the drawing on this layer (i.e. the layer is
        erased completely)
        """
        self._mSurface = pg.Surface((int(self._mImage.width), int(self._mImage.height)))
        return None
    
    def renderToSurface(self, surf):
        """
        Blit this layer to another surface.
        """
        surf.blit(self._mSurface, (0, 0))
        return(surf)
        
    
    def renderToOtherLayer(self, otherLayer):
        """
        Add this layer to another layer. 
        """
        otherLayer._mSurface.blit(self._mSurface, (0, 0))
