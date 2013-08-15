from Shapes import *
from ...Color import Color


class DrawingLayer:
    
    """
    
    **SUMMARY**
    DrawingLayer gives you a way to mark up Image classes without changing
    the image data itself.

    **NOTE**
    This class should be kept picklable so that the it can be sent over a Pipe
    
    """

    

    #TODO
    #include buffers for alpha related stuff
    #look into anti aliasing in gtk
    def __repr__(self):
        return "<SimpleCV %s  Image Resolution: (%d, %d) at memory location: (%s)>" % (self.name(), self.imgSize[0], self.imgSize[1], hex(id(self)))

    def __init__(self, (width,height)) :
        """
        **SUMMARY**
        
        Initializes a drawing layer
        
        **PARAMETERS**
        * *width,height* - The dimensions of the layer
        """
        self.imgSize = (width,height)
        self.bold = False
        self.italic = False
        self.underlined = False
        self.font = "Georgia"
        self.fontSize = 20
        self._shapes = []

    def name(self):
        return "DrawingLayer"
        

    def getDefaultAlpha(self):
        """
        Returns the default alpha value.
        """
        #TODO I dont think this is really needed
        pass

    def setLayerAlpha(self, alpha):
        """
        This method sets the alpha value of the entire layer in a single
        pass. This is helpful for merging layers with transparency.
        """
        self.alpha = alpha

    def setDefaultColor(self, color):
        """
        This method sets the default rendering color.

        Parameters:
            color - Color object or Color Tuple
        """
        pass
        #TODO may not be required

    def line(self, start, stop, color = Color.DEFAULT, width = 1, antialias = True, alpha = 255 ):
        """
        
        **SUMMARY**

        Draw a single line from the (x,y) tuple start to the (x,y) tuple stop.
        Optional parameters:

        **PARAMETERS**
        
        * *start* - The starting point of the line.
        
        * *stop* - The ending point of the line.

        * *color* - Color object or Color Tuple

        * *width* - The line width in pixels.

        * *antialias* -  Whether of not the edges are antialiased.

        * *alpha* - The alpha blending for the object. A value of 255 means opaque, 
                while 0 means transparent.

        """
        self._shapes.append(Line(start,stop,color,width,antialias,alpha))

    def lines(self, points, color = Color.DEFAULT, width = 1,  antialias = True, alpha = 255):
        """

        **SUMMARY**

        Draw a set of lines from the list of (x,y) tuples points. Lines are draw
        between each successive pair of points.

        **PARAMETERS**
        
        * *points* - a sequence of points to draw lines in between.

        * *color* - Color object or Color Tuple

        * *width* - The line width in pixels.

        * *antialias* -  Whether of not the edges are antialiased.

        * *alpha* - The alpha blending for the object. A value of 255 means opaque, 
                while 0 means transparent.

        """
        for i in range(len(points)-1):
        	self.line(points[i],points[i+1],color,width,antialias,alpha)

    def rectangle(self, topLeft, dimensions, color = Color.DEFAULT,width = 1, filled = False,antialias = True,  alpha = 255 ):
        """
        **SUMMARY**

        Draw a rectangle given the topLeft the (x,y) coordinate of the top left
        corner and dimensions (w,h) tge width and height
        
        **PARAMETERS**
        
        * *topLeft* - The (x,y) coordinates of the top left corner of the rectangle

        * *dimensions* - The (width,height) pf the rectangle

        * *color* - Color object or Color Tuple.
        
        * *width* -  The width of the edges of the rectangle.

        * *filled* - Whether or not the rectangle is filled

        * *antialias* - Whether of not the edges are antialiased

        * *alpha* - The alpha blending for the object. A value of 255 means opaque, 
                while 0 means transparent.

        """
        
        _p1 = topLeft
        _p2 = (topLeft[0]+dimensions[0],topLeft[1]+dimensions[1])
        self.rectangle2pts(_p1, _p2, color, width, filled, antialias, alpha)

    def rectangle2pts(self, pt1, pt2, color = Color.DEFAULT,width = 1, filled = False,antialias = True,  alpha = 255 ):
        """
        **SUMMARY**

        Draw a rectangle given two (x,y) points

        **PARAMETERS**
                
        * *pt1* - The top left corner of the rectangle.
        
        * *pt2* - The bottom right corner of the rectangle.

        * *color* - Color object or Color Tuple.
        
        * *width* -  The width of the edges of the rectangle.

        * *filled* - Whether or not the rectangle is filled

        * *antialias* - Whether of not the edges are antialiased

        * *alpha* - The alpha blending for the object. A value of 255 means opaque, 
                while 0 means transparent.
                
        """
        self._shapes.append(Rectangle(pt1,pt2,color,width,filled,antialias,alpha))

    def centeredRectangle(self, center, dimensions, color = Color.DEFAULT,width = 1, filled = False,antialias = True, alpha = 255 ):
        """
        **SUMMARY**

        Draw a rectangle given the center (x,y) of the rectangle and dimensions (width, height)

        **PARAMETERS**
        
        * *center* - The (x,y) coordinate of the center of the rectangle
        
        * *dimensions* - The (width,height) of the rectangle
        
        * *color* - Color object or Color Tuple.
        
        * *width* -  The width of the edges of the rectangle.

        * *filled* - Whether or not the rectangle is filled

        * *antialias* - Whether of not the edges are antialiased

        * *alpha* - The alpha blending for the object. A value of 255 means opaque, 
                while 0 means transparent.
    
        """
        p0 = (center[0]-dimensions[0]/2.0,center[1]-dimensions[1]/2.0)
        p1 = (center[0]+dimensions[0]/2.0,center[1]+dimensions[1]/2.0)
        self.rectangle2pts(p0,p1,color,antialias,width,filled,alpha)

    def polygon(self, points, color = Color.DEFAULT,width = 1, filled = False,antialias = True, alpha = 255 ):
        """
        **SUMMARY**

        Draw a polygon from a list of (x,y)

        **PARAMETERS**
        
        * *points* - The list of (x,y) coordinates of the vertices of the polygon
        
        * *color* - Color object or Color Tuple.
        
        * *width* -  The width of the edges of the rectangle.

        * *filled* - Whether or not the rectangle is filled

        * *antialias* - Whether of not the edges are antialiased

        * *alpha* - The alpha blending for the object. A value of 255 means opaque, 
                while 0 means transparent..
                
        """
        self._shapes.append(Polygon(points,color,width,filled,antialias,alpha))

    def circle(self, center, radius, color = Color.DEFAULT,width = 1, filled = False,antialias = True, alpha = 255 ):
        """
        **SUMMARY**

        Draw a circle given a location and a radius.
        
        **PARAMETERS**
        
        * *center* - The (x,y) coordinates of the center.
        
        * *radius* - The radius of the circle.

        * *color* - Color object or Color Tuple.
        
        * *width* -  The width of the edges of the rectangle.

        * *filled* - Whether or not the rectangle is filled

        * *antialias* - Whether of not the edges are antialiased

        * *alpha* - The alpha blending for the object. A value of 255 means opaque, 
                while 0 means transparent.
                
        """
        self._shapes.append(Circle(center,radius,color,width,filled,antialias,alpha))

    def ellipse(self, center, dimensions, color = Color.DEFAULT,width = 1, filled = False,antialias = True, alpha = 255 ):
        """
        **SUMMARY**

        Draw an ellipse given a location and a dimensions.
        
        **PARAMETERS**
        
        * *center* - The coordinates of the center.
        
        * *dimensions* - The length of axes along horizontal and vertical

        * *color* - Color object or Color Tuple.
        
        * *width* -  The width of the edges of the rectangle.

        * *filled* - Whether or not the rectangle is filled

        * *antialias* - Whether of not the edges are antialiased

        * *alpha* - The alpha blending for the object. A value of 255 means opaque, 
                while 0 means transparent.
                
        """
        self._shapes.append(Ellipse(center,dimensions,color,width,filled,antialias,alpha))
       

    def bezier(self, points,  color = Color.DEFAULT,width = 1,antialias = True, alpha = 255 ):
        """
        **SUMMARY**

        Draw a bezier curve based on the control points

        **PARAMETERS**
        
        * *points* - Control points . You must specify 3.       

        * *color* - Color object or Color Tuple.
        
        * *width* -  The width of the edges of the rectangle.

        * *antialias* - Whether of not the edges are antialiased

        * *alpha* - The alpha blending for the object. A value of 255 means opaque, 
                while 0 means transparent.

        """
        self._shapes.append(Bezier(points,color,width,antialias,alpha))
    
    def text(self, text, location, color = Color.DEFAULT,size = 20,font = "",bold = False ,italic = False,underline = False,  alpha = 255):
        """
        **SUMMARY**

        Write the a text string at a given location

        **PARAMETERS**
        
        * *text* -  A text string to print.

        * *location* - The location to place the top right corner of the text

        * *color* - Color object or Color Tuple

        * *font* - The font to be used. 
        
        * *size* - The size of letters.
        
        * *bold* - Whether or not text is bold.
        
        * *italic* - Whether or not text is italic.
        
        * *underline* - Whether or not text is underlined

        * *alpha* - The alpha blending for the object. A value of 255 means opaque, 
                while 0 means transparent.

        """
        self._shapes.append(Text(text,location, color, size, font, bold, italic, underline, alpha,None))
    
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
        pass


    def blit(self, img, coordinates = (0,0)):
        """
        Blit one image onto the drawing layer at upper left coordinates

        Parameters:
            img - Image
            coordinates - Tuple

        """
        pass

    def shapes(self):
        """
        **SUMMARY**
        
        Returns a list of shapes drawn on this layer
        
        **RETURNS**
        
        A list of shapes
        
        """
        return self._shapes
    def clear(self):
        """
        **SUMMARY**
        
        This method removes all of the drawing on this layer (i.e. the layer is
        erased completely)
        """
        self._shapes = []
    
    def ezViewText(self,text,location,color = (255,255,255),size = 20,bgColor = (0,0,0)):
        """
        **SUMMARY**

        ezViewText works just like text but it sets both the foreground and background
        color and overwrites the image pixels. Use this method to make easily
        viewable text on a dynamic video stream.

        **PARAMETERS**
        
        * *text* -  A text string to print.

        * *location* - The location to place the top right corner of the text

        * *color* - Color of the text.
        
        * *size* - The size of letters.
        
        * *bgColor* - The colour of the background.
        """
        #TODO Maybe include all paramaters for text over here, if required
        self._shapes.append(Text(text,location, color, size, "", False, False, False, 255,bgColor))
    
    
    
    
    #TODO rotatedrectangle
