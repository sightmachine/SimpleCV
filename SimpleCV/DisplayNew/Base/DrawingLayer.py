from abc import ABCMeta,abstractmethod
from shapes import *


class DrawingLayerBase:
    
    __metaclass__ = ABCMeta
    """
    DrawingLayer gives you a way to mark up Image classes without changing
    the image data itself.
    """
    _defaultColor = 0
    _fontColor = 0
    _clearColor = 0
    _font = 0
    _fontName = ""
    _fontSize = 0
    _defaultAlpha = 255
    width = 0
    height = 0
    _shapes = []

    #TODO
    #include buffers for alpha related stuff
    #look into anti aliasing in gtk
    def __repr__(self):
        return "<SimpleCV %s resolution:(%s), Image Resolution: (%d, %d) at memory location: (%s)>" % (self.name(),self.size, self.imgSize[0], self.imgSize[1], hex(id(self)))

    @abstractmethod
    def __init__(self, (width,height)) :
        """
        Sets all buffers
        """
        selg.imgSize = (width,height)

    @abstractmethod
    def name(self):
        pass
        

    @abstractproperty
    def getDefaultAlpha(self):
        """
        Returns the default alpha value.
        """

    @abstractproperty
    def setLayerAlpha(self, alpha):
        """
        This method sets the alpha value of the entire layer in a single
        pass. This is helpful for merging layers with transparency.
        """

    @abstractproperty
    def setDefaultColor(self, color):
        """
        This method sets the default rendering color.

        Parameters:
            color - Color object or Color Tuple
        """

    @abstractmethod
    def line(self, start, stop, color = Color.DEFAULT, width = 1, antialias = True, alpha = -1 ):
        """
        Draw a single line from the (x,y) tuple start to the (x,y) tuple stop.
        Optional parameters:

        color - Color object or Color Tuple

        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent.

        width - The line width in pixels.

        antialias - Draw an antialiased object of width one.

        """
        _shapes.append(Line(start,stop,color,width,antialias,alpha))


    @abstractmethod
    def lines(self, points, color = Color.DEFAULT, antialias = True, alpha = -1, width = 1 ):
        """
        Draw a set of lines from the list of (x,y) tuples points. Lines are draw
        between each successive pair of points.

        Optional parameters:

        color - Color object or Color Tuple

        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent.

        width - The line width in pixels.

        antialias - Draw an antialiased object of width one.

        """
        for i in range(len(points)-1):
        	line(points[i],points[i+1],color,width,antialias,alpha)

    @abstractmethod
    def rectangle(self, topLeft, dimensions, color = Color.DEFAULT,antialias = True, width = 1, filled = False, alpha = -1 ):
        """
        Draw a rectangle given the topLeft the (x,y) coordinate of the top left
        corner and dimensions (w,h) tge width and height

        color - Color object or Color Tuple

        antialias - Draw the edges of the object antialiased. Note this does not work when the object is filled.

        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent.

        width -     The line width in pixels. This does not work if antialiasing is enabled.

        filled -The rectangle is filled in
        """
        p0 = topLeft
        p1 = (topLeft[0]+dimensions[0],topLeft[1]+dimensions[1])
        rectangle2pts(p0,p1,color,antialias,width,filled,alpha)

    @abstractmethod
    def rectangle2pts(self, pt0, pt1, color = Color.DEFAULT,antialias = True, width = 1, filled = False, alpha = -1 ):
        """
        Draw a rectangle given two (x,y) points

        color - Color object or Color Tuple

        antialias - Draw the edges of the object antialiased. Note this does not work when the object is filled.

        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent.

        width -     The line width in pixels. This does not work if antialiasing is enabled.

        filled -The rectangle is filled in
        """
        _shapes.append(Rectangle(pt1,pt2,color,width,filled,antialias,alpha))

    @abstractmethod
    def centeredRectangle(self, center, dimensions, color = Color.DEFAULT,antialias = True, width = 1, filled = False, alpha = -1 ):
        """
        Draw a rectangle given the center (x,y) of the rectangle and dimensions (width, height)

        color - Color object or Color Tuple

        antialias - Draw the edges of the object antialiased. Note this does not work when the object is filled.

        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent.

        width -     The line width in pixels. This does not work if antialiasing is enabled.

        filled -The rectangle is filled in
        """
        p0 = (center[0]-dimensions[0]/2.0,center[1]-dimensions[1]/2.0)
        p1 = (center[0]+dimensions[0]/2.0,center[1]+dimensions[1]/2.0)
        rectangle2pts(p0,p1,color,antialias,width,filled,alpha)

    @abstractmethod
    def polygon(self, points, color = Color.DEFAULT, antialias = True, width = 1, filled = False, alpha = -1):
        """
        Draw a polygon from a list of (x,y)

        color - Color object or Color Tuple 

        antialias - Draw the edges of the object antialiased. Note this does not work when the object is filled.

        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent.

        width - The width in pixels. This does not work if antialiasing is enabled.

        filled -The object is filled in


        """
        _shapes.append(Polygon(points,color,width,filled,antialias,alpha))

    @abstractmethod
    def circle(self, center, radius, color = Color.DEFAULT, antialias = True, width = 1, filled = False, alpha = -1):
        """
        Draw a circle given a location and a radius.

        color - Color object or Color Tuple

        antialias - Draw the edges of the object antialiased. Note this does not work when the object is filled.

        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent.

        width - The line width in pixels. This does not work if antialiasing is enabled.

        filled -The object is filled in

        """
        _shapes.append(Circle(center,radius,color,width,filled,antialias,alpha))

    @abstractmethod
    def ellipse(self, center, dimensions, color = Color.DEFAULT,antialias = True, width = 1, filled = False, alpha = -1):
        """
        Draw an ellipse given a location and a dimensions.

        color - Color object or Color Tuple

        antialias - Draw the edges of the object antialiased. Note this does not work when the object is filled.

        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent.

        width - The line width in pixels. This does not work if antialiasing is enabled.

        filled -The object is filled in

        """
        _shapes.append(Ellipse(center,dimensions,color,width,filled,antialias,alpha))
       

    @abstractmethod
    def bezier(self, points, steps, color = Color.DEFAULT,antialias = True, alpha = -1):
        """
        Draw a bezier curve based on a control point and the a number of steps

        color - Color object or Color Tuple

        antialias - Draw the edges of the object antialiased. Note this does not work when the object is filled.

        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent

        """
        _shapes.append(Bezier(points,steps,color,width,antialias,alpha))
    
    @abstractmethod
    def text(self, text, location, color = Color.DEFAULT, alpha = -1):
        """
        Write the a text string at a given location

        text -  A text string to print.

        location-The location to place the top right corner of the text

        color - Color object or Color Tuple

        alpha - The alpha blending for the object. If this value is -1 then the
                layer default value is used. A value of 255 means opaque, while 0
                means transparent.

        """
    
    @abstractmethod
    def setFontBold(self, doBold):
        """
        This method sets and unsets the current font to be bold.
        """
        
    @abstractmethod
    def setFontItalic(self, doItalic):
        """
        This method sets and unsets the current font to be italic.
        """
        
    @abstractmethod
    def setFontUnderline(self, doUnderline):
        """
        This method sets and unsets the current font to be underlined
        """
       
    @abstractmethod
    def selectFont(self, fontName):
        """
        This method attempts to set the font from a font file. It is advisable
        to use one of the fonts listed by the listFonts() method. The input
        is a string with the font name.
        """
        
    @abstractmethod
    def listFonts(self):
        """
        This method returns a list of strings corresponding to the fonts available
        on the current system.
        """

    @abstractmethod
    def setFontSize(self, sz):
        """
        This method sets the font size roughly in points. A size of 10 is almost
        too small to read. A size of 20 is roughly 10 pixels high and a good choice.

        Parameters:
            sz = Int
        """

    @abstractmethod
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


    @abstractmethod
    def blit(self, img, coordinates = (0,0)):
        """
        Blit one image onto the drawing layer at upper left coordinates

        Parameters:
            img - Image
            coordinates - Tuple

        """

    @abstractmethod
    def clear(self):
        """
        This method removes all of the drawing on this layer (i.e. the layer is
        erased completely)
        """
