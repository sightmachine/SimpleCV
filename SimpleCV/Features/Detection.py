# SimpleCV Detection Library
#
# This library includes classes for finding things in images
#
# FYI - 
 # All angles shalt be described in degrees with zero pointing east in the
# plane of the image with all positive rotations going counter-clockwise.
# Therefore a rotation from the x-axis to to the y-axis is positive and follows
# the right hand rule. 
#
#load required libraries
from SimpleCV.base import *
from SimpleCV.ImageClass import *
from SimpleCV.Color import * 
from SimpleCV.Features.Features import Feature, FeatureSet



######################################################################
class Corner(Feature):
    """
    **SUMMARY**

    The Corner feature is a point returned by the FindCorners function
    Corners are used in machine vision as a very computationally efficient way
    to find unique features in an image.  These corners can be used in
    conjunction with many other algorithms.

    **SEE ALSO**

    :py:meth:`findCorners`
    """
    def __init__(self, i, at_x, at_y):

        points = [(at_x-1,at_y-1),(at_x-1,at_y+1),(at_x+1,at_y+1),(at_x+1,at_y-1)]
        super(Corner, self).__init__(i, at_x, at_y,points)
        #can we look at the eigenbuffer and find direction?
  
    def draw(self, color = (255, 0, 0),width=1):
        """
        **SUMMARY**

        Draw a small circle around the corner.  Color tuple is single parameter, default is Red.

        **PARAMETERS**
        
        * *color* - An RGB color triplet. 
        * *width* - if width is less than zero we draw the feature filled in, otherwise we draw the
          contour using the specified width.

          
        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer. 

        """
        self.image.drawCircle((self.x, self.y), 4, color,width)

######################################################################
class Line(Feature):
    """
    **SUMMARY**

    The Line class is returned by the findLines function, but can also be initialized with any two points.
  
    >>> l = Line(Image, point1, point2) 
    
    Where point1 and point2 are (x,y) coordinate tuples.
  
    >>> l.points 
    
    Returns a tuple of the two points


    """
    #TODO - A nice feature would be to calculate the endpoints of the line.

    def __init__(self, i, line):
        self.image = i
        self.end_points = copy(line)
        #coordinate of the line object is the midpoint
        at_x = (line[0][0] + line[1][0]) / 2
        at_y = (line[0][1] + line[1][1]) / 2
        xmin = int(np.min([line[0][0],line[1][0]]))
        xmax = int(np.max([line[0][0],line[1][0]]))
        ymax = int(np.min([line[0][1],line[1][1]]))
        ymin = int(np.max([line[0][1],line[1][1]]))
        points = [(xmin,ymin),(xmin,ymax),(xmax,ymax),(xmax,ymin)]
        super(Line, self).__init__(i, at_x, at_y,points)

    def draw(self, color = (0, 0, 255),width=1):
        """
        Draw the line, default color is blue

        **SUMMARY**

        Draw a small circle around the corner.  Color tuple is single parameter, default is Red.

        **PARAMETERS**
        
        * *color* - An RGB color triplet. 
        * *width* - Draw the line using the specified width.
          
        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer. 


        """
        self.image.drawLine(self.end_points[0], self.end_points[1], color,width)
      
    def length(self):
        """

        **SUMMARY**
        
        This method returns the length of the line.
        
        **RETURNS**
        
        A floating point length value. 

        **EXAMPLE**
       
        >>> img = Image("OWS.jpg")
        >>> lines = img.findLines
        >>> for l in lines:
        >>>    if l.length() > 100:
        >>>       print "OH MY! - WHAT A BIG LINE YOU HAVE!" 
        >>>       print "---I bet you say that to all the lines."

        """
        return float(spsd.euclidean(self.end_points[0], self.end_points[1]))

    def crop(self):
        """
        **SUMMARY**

        This function crops the source image to the location of the feature and returns 
        a new SimpleCV image.
        
        **RETURNS**
        
        A SimpleCV image that is cropped to the feature position and size.

        **EXAMPLE**

        >>> img = Image("../sampleimages/EdgeTest2.png")
        >>> l = img.findLines()
        >>> myLine = l[0].crop()

        """
        tl = self.topLeftCorner()
        return self.image.crop(tl[0],tl[1],self.width(),self.height())

    def meanColor(self):
        """
        **SUMMARY**

        Returns the mean color of pixels under the line.  Note that when the line falls "between" pixels, each pixels color contributes to the weighted average.


        **RETURNS**

        Returns an RGB triplet corresponding to the mean color of the feature.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> l = img.findLines()
        >>> c = l[0].meanColor()

        """
        (pt1, pt2) = self.end_points     
        #we're going to walk the line, and take the mean color from all the px
        #points -- there's probably a much more optimal way to do this
        (maxx,minx,maxy,miny) = self.extents()
    
        d_x = maxx - minx
        d_y = maxy - miny 
        #orient the line so it is going in the positive direction
    
        #if it's a straight one, we can just get mean color on the slice
        if (d_x == 0.0):
            return self.image[pt1[0]:pt1[0] + 1, miny:maxy].meanColor()
        if (d_y == 0.0):
            return self.image[minx:maxx, pt1[1]:pt1[1] + 1].meanColor()
        
        error = 0.0
        d_err = d_y / d_x  #this is how much our "error" will increase in every step
        px = [] 
        weights = []
        if (d_err < 1):
            y = miny
            #iterate over X
            for x in range(minx, maxx):
                #this is the pixel we would draw on, check the color at that px 
                #weight is reduced from 1.0 by the abs amount of error
                px.append(self.image[x, y])
                weights.append(1.0 - abs(error))
                
                #if we have error in either direction, we're going to use the px
                #above or below
                if (error > 0): #
                    px.append(self.image[x, y+1])
                    weights.append(error)
          
                if (error < 0):
                    px.append(self.image[x, y-1])
                    weights.append(abs(error))
          
                error = error + d_err
                if (error >= 0.5):
                    y = y + 1
                    error = error - 1.0
        else: 
            #this is a "steep" line, so we iterate over X
            #copy and paste.  Ugh, sorry.
            x = minx
            for y in range(miny, maxy):
                #this is the pixel we would draw on, check the color at that px 
                #weight is reduced from 1.0 by the abs amount of error
                px.append(self.image[x, y])
                weights.append(1.0 - abs(error))
                
                #if we have error in either direction, we're going to use the px
                #above or below
                if (error > 0): #
                    px.append(self.image[x + 1, y])
                    weights.append(error)
          
                if (error < 0):
                    px.append(self.image[x - 1, y])
                    weights.append(abs(error))
            
                error = error + (1.0 / d_err) #we use the reciprocal of error
                if (error >= 0.5):
                    x = x + 1
                    error = error - 1.0
    
        #once we have iterated over every pixel in the line, we avg the weights
        clr_arr = np.array(px)
        weight_arr = np.array(weights)
          
        weighted_clrs = np.transpose(np.transpose(clr_arr) * weight_arr) 
        #multiply each color tuple by its weight
    
        temp = sum(weighted_clrs) / sum(weight_arr)  #return the weighted avg
        return (float(temp[0]),float(temp[1]),float(temp[2]))

    def angle(self):
        """
        **SUMMARY**

        This is the angle of the line, from the leftmost point to the rightmost point
        Returns angle (theta) in radians, with 0 = horizontal, -pi/2 = vertical positive slope, pi/2 = vertical negative slope
         
        **RETURNS**
        
        An angle value in degrees. 

        **EXAMPLE**
        
        >>> img = Image("OWS.jpg")
        >>> ls = img.findLines
        >>> for l in ls:
        >>>    if l.angle() == 0:
        >>>       print "I AM HORIZONTAL."


        """
        #first find the leftmost point 
        a = 0
        b = 1
        if (self.end_points[a][0] > self.end_points[b][0]):
            b = 0 
            a = 1
          
        d_x = self.end_points[b][0] - self.end_points[a][0]
        d_y = self.end_points[b][1] - self.end_points[a][1]
        #our internal standard is degrees
        return float(360.00 * (atan2(d_y, d_x)/(2 * np.pi))) #formerly 0 was west
  
######################################################################
class Barcode(Feature):
    """
    **SUMMARY**

    The Barcode Feature wrappers the object returned by findBarcode(), a zbar symbol
  
    * The x,y coordinate is the center of the code.
    * points represents the four boundary points of the feature.  Note: for QR codes, these points are the reference rectangls, and are quadrangular, rather than rectangular with other datamatrix types. 
    * data is the parsed data of the code.

    **SEE ALSO**

    :py:meth:`ImageClass.findBarcodes()`
    """
    data = ""
  
    #given a ZXing bar
    def __init__(self, i, zbsymbol):
        self.image = i

        locs = zbsymbol.location
        if len(locs) > 4:
          xs = [l[0] for l in locs]
          ys = [l[1] for l in locs]
          xmax = np.max(xs)
          xmin = np.min(xs)
          ymax = np.max(ys)
          ymin = np.min(ys)
          points = ((xmin, ymin),(xmin,ymax),(xmax, ymax),(xmax,ymin))
        else:
          points = copy(locs) # hopefully this is in tl clockwise order
          
        super(Barcode, self).__init__(i, 0, 0,points)        
        self.data = zbsymbol.data
        self.points = copy(points)
        numpoints = len(self.points)
        self.x = 0
        self.y = 0
    
        for p in self.points:
            self.x += p[0]
            self.y += p[1]
      
        if (numpoints):
            self.x /= numpoints
            self.y /= numpoints

    def __repr__(self):
        return "%s.%s at (%d,%d), read data: %s" % (self.__class__.__module__, self.__class__.__name__, self.x, self.y, self.data)
  
    def draw(self, color = (255, 0, 0),width=1): 
        """

        **SUMMARY**

        Draws the bounding area of the barcode, given by points.  Note that for
        QR codes, these points are the reference boxes, and so may "stray" into 
        the actual code.


        **PARAMETERS**
        
        * *color* - An RGB color triplet. 
        * *width* - if width is less than zero we draw the feature filled in, otherwise we draw the
          contour using the specified width.

          
        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer. 


        """
        self.image.drawLine(self.points[0], self.points[1], color,width)
        self.image.drawLine(self.points[1], self.points[2], color,width)
        self.image.drawLine(self.points[2], self.points[3], color,width)
        self.image.drawLine(self.points[3], self.points[0], color,width)
  
    def length(self):
        """
        **SUMMARY**

        Returns the longest side of the quandrangle formed by the boundary points.         
        
        **RETURNS**
        
        A floating point length value. 

        **EXAMPLE**
       
        >>> img = Image("mycode.jpg")
        >>> bc = img.findBarcode()
        >>> print bc[-1].length()

        """
        sqform = spsd.squareform(spsd.pdist(self.points, "euclidean"))
        #get pairwise distances for all points
        #note that the code is a quadrilateral
        return max(sqform[0][1], sqform[1][2], sqform[2][3], sqform[3][0])
  
    def area(self):
        """
        **SUMMARY**

        Returns the area defined by the quandrangle formed by the boundary points 


        **RETURNS**
        
        An integer area value. 

        **EXAMPLE**

        >>> img = Image("mycode.jpg")
        >>> bc = img.findBarcode()
        >>> print bc[-1].area()


        """
        #calc the length of each side in a square distance matrix
        sqform = spsd.squareform(spsd.pdist(self.points, "euclidean"))
    
        #squareform returns a N by N matrix 
        #boundry line lengths
        a = sqform[0][1] 
        b = sqform[1][2] 
        c = sqform[2][3] 
        d = sqform[3][0] 
    
        #diagonals
        p = sqform[0][2] 
        q = sqform[1][3] 
        
        #perimeter / 2
        s = (a + b + c + d)/2.0 
    
        #i found the formula to do this on wikihow.  Yes, I am that lame.
        #http://www.wikihow.com/Find-the-Area-of-a-Quadrilateral
        return sqrt((s - a) * (s - b) * (s - c) * (s - d) - (a * c + b * d + p * q) * (a * c + b * d - p * q) / 4)
    
###################################################################### 
class HaarFeature(Feature):
    """
    **SUMMARY**

    The HaarFeature is a rectangle returned by the FindHaarFeature() function.
  
    * The x,y coordinates are defined by the center of the bounding rectangle.
    * The classifier property refers to the cascade file used for detection .
    * Points are the clockwise points of the bounding rectangle, starting in upper left.

    """
    classifier = "" 
    _width = ""
    _height = ""
    neighbors = ''
    featureName = 'None'
    
    def __init__(self, i, haarobject, haarclassifier = None):
        self.image = i
        ((x, y, width, height), self.neighbors) = haarobject
        at_x = x + width/2
        at_y = y + height/2 #set location of feature to middle of rectangle
        points = ((x, y), (x + width, y), (x + width, y + height), (x, y + height))
 
         #set bounding points of the rectangle
        self.classifier = haarclassifier
        if( haarclassifier is not None ):
            self.featureName = haarclassifier.getName()
            
        super(HaarFeature, self).__init__(i, at_x, at_y, points)                

    
    def draw(self, color = (0, 255, 0),width=1):
        """
        **SUMMARY**

        Draw the bounding rectangle, default color green.

        **PARAMETERS**
        
        * *color* - An RGB color triplet. 
        * *width* - if width is less than zero we draw the feature filled in, otherwise we draw the
          contour using the specified width.

          
        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer. 

        """
        self.image.drawLine(self.points[0], self.points[1], color,width)
        self.image.drawLine(self.points[1], self.points[2], color,width)
        self.image.drawLine(self.points[2], self.points[3], color,width)
        self.image.drawLine(self.points[3], self.points[0], color,width)
      
    def __getstate__(self):
        dict = self.__dict__.copy()
        del dict["classifier"]
        return dict
              
      
    def meanColor(self):
        """
        **SUMMARY**

        Find the mean color of the boundary rectangle.

        **RETURNS**

        Returns an  RGB triplet that corresponds to the mean color of the feature.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> face = HaarCascade("face.xml")
        >>> faces = img.findHaarFeatures(face)
        >>> print faces[-1].meanColor()

        """
        crop = self.image[self.points[0][0]:self.points[1][0], self.points[0][1]:self.points[2][1]]
        return crop.meanColor()
  

    def area(self):
        """
        **SUMMARY**

        Returns the area of the feature in pixels.

        **RETURNS**
        
        The area of the feature in pixels. 

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> face = HaarCascade("face.xml")
        >>> faces = img.findHaarFeatures(face)
        >>> print faces[-1].area()

        """
        return self.width() * self.height()
  
######################################################################  
class Chessboard(Feature):
    """
    **SUMMARY**

    This class is used for Calibration, it uses a chessboard
    to calibrate from pixels to real world measurements.
    """
    spCorners = []
    dimensions = ()
    
    def __init__(self, i, dim, subpixelCorners):
        self.dimensions = dim
        self.spCorners = subpixelCorners
        at_x = np.average(np.array(self.spCorners)[:, 0])
        at_y = np.average(np.array(self.spCorners)[:, 1])
        
        posdiagsorted = sorted(self.spCorners, key = lambda corner: corner[0] + corner[1])
        #sort corners along the x + y axis
        negdiagsorted = sorted(self.spCorners, key = lambda corner: corner[0] - corner[1])
        #sort corners along the x - y axis
        
        points = (posdiagsorted[0], negdiagsorted[-1], posdiagsorted[-1], negdiagsorted[0])
        super(Chessboard, self).__init__(i, at_x, at_y, points)                        

        
    def draw(self, no_needed_color = None):
        """
        **SUMMARY**


        Draws the chessboard corners.  We take a color param, but ignore it.

        **PARAMETERS**
        
        * *no_needed_color* - An RGB color triplet that isn't used 

          
        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer. 

        """
        cv.DrawChessboardCorners(self.image.getBitmap(), self.dimensions, self.spCorners, 1)
      
    def area(self):
        """
        **SUMMARY**

        Returns the mean of the distance between corner points in the chessboard
        Given that the chessboard is of a known size, this can be used as a
        proxy for distance from the camera

        **RETURNS**
        
        Returns the mean distance between the corners. 

        **EXAMPLE**

        >>> img = Image("corners.jpg")
        >>> feats = img.findChessboardCorners()
        >>> print feats[-1].area()

        """
        #note, copying this from barcode means we probably need a subclass of
        #feature called "quandrangle"
        sqform = spsd.squareform(spsd.pdist(self.points, "euclidean"))
        a = sqform[0][1] 
        b = sqform[1][2] 
        c = sqform[2][3] 
        d = sqform[3][0] 
        p = sqform[0][2] 
        q = sqform[1][3] 
        s = (a + b + c + d)/2.0 
        return 2 * sqrt((s - a) * (s - b) * (s - c) * (s - d) - (a * c + b * d + p * q) * (a * c + b * d - p * q) / 4)
 
######################################################################
class TemplateMatch(Feature):
    """
    **SUMMARY**

    This class is used for template (pattern) matching in images.
    The template matching cannot handle scale or rotation.

    """

    template_image = None
    quality = 0
    w = 0
    h = 0 

    def __init__(self, image, template, location, quality):
        self.template_image = template # -- KAT - TRYING SOMETHING
        self.image = image
        self.quality = quality
        w = template.width
        h = template.height
        at_x = location[0]
        at_y = location[1]
        points = [(at_x,at_y),(at_x+w,at_y),(at_x+w,at_y+h),(at_x,at_y+h)]
 
        super(TemplateMatch, self).__init__(image, at_x, at_y, points)                        

    def _templateOverlaps(self,other):
        """
        Returns true if this feature overlaps another template feature.
        """
        (maxx,minx,maxy,miny) = self.extents()
        overlap = False
        for p in other.points:
            if( p[0] <= maxx and p[0] >= minx and p[1] <= maxy and p[1] >= miny ):
               overlap = True 
               break 

        return overlap
    

    def consume(self, other):
        """ 
        Given another template feature, make this feature the size of the two features combined.
        """
        (maxx,minx,maxy,miny) = self.extents()
        (maxx0,minx0,maxy0,miny0) = other.extents()

        maxx = max(maxx,maxx0)
        minx = min(minx,minx0)
        maxy = max(maxy,maxy0)
        miny = min(miny,miny0)
        self.x = minx
        self.y = miny
        self.points = [(minx,miny),(minx,maxy),(maxx,maxy),(maxx,miny)]
        self._updateExtents()
   
 
    def rescale(self,w,h):
        """
        This method keeps the feature's center the same but sets a new width and height
        """
        (maxx,minx,maxy,miny) = self.extents()
        xc = minx+((maxx-minx)/2)
        yc = miny+((maxy-miny)/2)
        x = xc-(w/2)
        y = yc-(h/2)
        self.x = x
        self.y = y
        self.points = [(x,y),
                       (x+w,y),
                       (x+w,y+h),
                       (x,y+h)]
        self._updateExtents()

    def draw(self, color = Color.GREEN, width = 1):      
        """  
        **SUMMARY**
        
        Draw the bounding rectangle, default color green.
        
        **PARAMETERS**
        
        * *color* - An RGB color triplet. 
        * *width* - if width is less than zero we draw the feature filled in, otherwise we draw the
          contour using the specified width.
        
        **RETURNS**
        
        Nothing - this is an inplace operation that modifies the source images drawing layer. 
        """
        self.image.dl().rectangle((self.x,self.y), (self.width(), self.height()), color = color, width=width)
######################################################################
class Circle(Feature):
    """
    **SUMMARY**

    Class for a general circle feature with a center at (x,y) and a radius r

    """
    x = 0.00
    y = 0.00 
    r = 0.00
    image = "" #parent image
    points = []
    avgColor = None
  
    def __init__(self, i, at_x, at_y, r):
        self.r = r
        self.avgColor = None
        points = [(at_x-r,at_y-r),(at_x+r,at_y-r),(at_x+r,at_y+r),(at_x-r,at_y+r)]
        super(Circle, self).__init__(i, at_x, at_y, points)                                
        segments = 18
        rng = range(1,segments+1)
        self.mContour = []
        for theta in rng:
            rp = 2.0*math.pi*float(theta)/float(segments)
            x = (r*math.sin(rp))+at_x
            y = (r*math.cos(rp))+at_y
            self.mContour.append((x,y))
   
  
  
    def draw(self, color = Color.GREEN,width=1):
        """
        **SUMMARY**

        With no dimension information, color the x,y point for the feature.

        **PARAMETERS**
        
        * *color* - An RGB color triplet. 
        * *width* - if width is less than zero we draw the feature filled in, otherwise we draw the
          contour using the specified width.
          
        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer. 

        """
        self.image.dl().circle((self.x,self.y),self.r,color,width)
    
    def show(self, color = Color.GREEN):
        """
        **SUMMARY**

        This function will automatically draw the features on the image and show it.
        It is a basically a shortcut function for development and is the same as:

        **PARAMETERS**
        
        * *color* - the color of the feature as an rgb triplet. 

        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer. 

        **EXAMPLE**
        
        >>> img = Image("logo")
        >>> feat = img.findCircle()
        >>> feat[0].show()

        """
        self.draw(color)
        self.image.show()
  
    def distanceFrom(self, point = (-1, -1)): 
        """
        **SUMMARY**

        Given a point (default to center of the image), return the euclidean distance of x,y from this point. 

        **PARAMETERS**
        
        * *point* - The point, as an (x,y) tuple on the image to measure distance from. 

        **RETURNS**
        
        The distance as a floating point value in pixels. 

        **EXAMPLE**
        
        >>> img = Image("OWS.jpg")
        >>> blobs = img.findCircle()
        >>> blobs[-1].distanceFrom(blobs[-2].coordinates())

        """
        if (point[0] == -1 or point[1] == -1):
            point = np.array(self.image.size()) / 2
        return spsd.euclidean(point, [self.x, self.y]) 
  
    def meanColor(self):
        """

        **SUMMARY**

        Returns the average color within the circle.

        **RETURNS**

        Returns an RGB triplet that corresponds to the mean color of the feature.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> c = img.findCircle()
        >>> c[-1].meanColor()

        """
        #generate the mask
        if( self.avgColor is None):
            mask = self.image.getEmpty(1)
            cv.Zero(mask)
            cv.Circle(mask,(self.x,self.y),self.r,color=(255,255,255),thickness=-1)
            temp = cv.Avg(self.image.getBitmap(),mask)
            self.avgColor = (temp[0],temp[1],temp[2])
        return self.avgColor
  
    def area(self):
        """
        Area covered by the feature -- for a pixel, 1

        **SUMMARY**

        Returns a numpy array of the area of each feature in pixels.

        **RETURNS**
        
        A numpy array of all the positions in the featureset. 

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> xs = feats.coordinates()
        >>> print xs


        """
        return self.r*self.r*pi

    def perimeter(self):
        """
        **SUMMARY**
        
        Returns the perimeter of the circle feature in pixels.
        """
        return 2*pi*self.r
  
    def width(self):
        """
        **SUMMARY** 

        Returns the width of the feature -- for compliance just r*2

        """
        return self.r*2
  
    def height(self):
        """
        **SUMMARY**

        Returns the height of the feature -- for compliance just r*2
        """
        return self.r*2
  
    def radius(self):
        """
        **SUMMARY**
        
        Returns the radius of the circle in pixels.

        """
        return self.r
    
    def diameter(self):
        """
        **SUMMARY**

        Returns the diameter of the circle in pixels.

        """
        return self.r*2
    
    def crop(self,noMask=False):
        """
        **SUMMARY**

        This function returns the largest bounding box for an image.

        **PARAMETERS**
       
        * *noMask* - if noMask=True we return the bounding box image of the circle.
          if noMask=False (default) we return the masked circle with the rest of the area set to black
          
        **RETURNS**
        
        The masked circle image. 
          
        """
        if( noMask ):
            return self.image.crop(self.x, self.y, self.width(), self.height(), centered = True)
        else:
            mask = self.image.getEmpty(1)
            result = self.image.getEmpty()
            cv.Zero(mask)
            cv.Zero(result)
            #if you want to shave a bit of time we go do the crop before the blit
            cv.Circle(mask,(self.x,self.y),self.r,color=(255,255,255),thickness=-1)
            cv.Copy(self.image.getBitmap(),result,mask)
            retVal = Image(result)
            retVal = retVal.crop(self.x, self.y, self.width(), self.height(), centered = True)
            return retVal

##################################################################################
class KeyPoint(Feature):
    """
    **SUMMARY**

    The class is place holder for SURF/SIFT/ORB/STAR keypoints.

    """
    x = 0.00
    y = 0.00 
    r = 0.00
    image = "" #parent image
    points = []
    __avgColor = None
    mAngle = 0
    mOctave = 0
    mResponse = 0.00
    mFlavor = ""
    mDescriptor = None
    mKeyPoint = None
    def __init__(self, i, keypoint, descriptor=None, flavor="SURF" ):
#i, point, diameter, descriptor=None,angle=-1, octave=0,response=0.00,flavor="SURF"):
        self.mKeyPoint = keypoint
        x = keypoint.pt[1] #KAT
        y = keypoint.pt[0]
        self._r = keypoint.size/2.0
        self._avgColor = None
        self.image = i
        self.mAngle = keypoint.angle
        self.mOctave = keypoint.octave
        self.mResponse = keypoint.response
        self.mFlavor = flavor
        self.mDescriptor = descriptor
        r = self._r
        points  = ((x+r,y+r),(x+r,y-r),(x-r,y-r),(x-r,y+r))
        super(KeyPoint, self).__init__(i, x, y, points)                                

        segments = 18
        rng = range(1,segments+1)
        self.points = []
        for theta in rng:
            rp = 2.0*math.pi*float(theta)/float(segments)
            x = (r*math.sin(rp))+self.x
            y = (r*math.cos(rp))+self.y
            self.points.append((x,y))
 

    def getObject(self):
        """
        **SUMMARY**
        
        Returns the raw keypoint object. 

        """
        return self.mKeyPoint

    def descriptor(self):
        """
        **SUMMARY**
        
        Returns the raw keypoint descriptor. 

        """
        return self.mDescriptor

    def quality(self):
        """
        **SUMMARY**
        
        Returns the quality metric for the keypoint object. 

        """
        return self.mResponse 

    def octave(self):
        """
        **SUMMARY**
        
        Returns the raw keypoint's octave (if it has one).

        """
        return self.mOctave

    def flavor(self):
        """
        **SUMMARY**
        
        Returns the type of keypoint as a string (e.g. SURF/MSER/ETC)

        """
        return self.mFlavor

    def angle(self):
        """
        **SUMMARY**

        Return the angle (theta) in degrees of the feature. The default is 0 (horizontal).
        
        **RETURNS**
        
        An angle value in degrees. 

        """
        return self.mAngle

  
    def draw(self, color = Color.GREEN, width=1):
        """
        **SUMMARY**

        Draw a circle around the feature.  Color tuple is single parameter, default is Green.

        **PARAMETERS**
        
        * *color* - An RGB color triplet. 
        * *width* - if width is less than zero we draw the feature filled in, otherwise we draw the
          contour using the specified width.

          
        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer. 

        """
        self.image.dl().circle((self.x,self.y),self._r,color,width)
        pt1 = (int(self.x),int(self.y))
        pt2 = (int(self.x+(self.radius()*sin(radians(self.angle())))),
               int(self.y+(self.radius()*cos(radians(self.angle())))))
        self.image.dl().line(pt1,pt2,color,width)
    
    def show(self, color = Color.GREEN):
        """
        **SUMMARY**

        This function will automatically draw the features on the image and show it.
        It is a basically a shortcut function for development and is the same as:

        >>> img = Image("logo")
        >>> feat = img.findBlobs()
        >>> if feat: feat.draw()
        >>> img.show()

        """
        self.draw(color)
        self.image.show()
  
    def distanceFrom(self, point = (-1, -1)): 
        """
        **SUMMARY**

        Given a point (default to center of the image), return the euclidean distance of x,y from this point
        """
        if (point[0] == -1 or point[1] == -1):
            point = np.array(self.image.size()) / 2
        return spsd.euclidean(point, [self.x, self.y]) 
  
    def meanColor(self):
        """
        **SUMMARY**

        Return the average color within the feature's radius

        **RETURNS**

        Returns an  RGB triplet that corresponds to the mean color of the feature.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> kp = img.findKeypoints()
        >>> c = kp[0].meanColor()

        """
        #generate the mask
        if( self._avgColor is None):
            mask = self.image.getEmpty(1)
            cv.Zero(mask)
            cv.Circle(mask,(int(self.x),int(self.y)),int(self._r),color=(255,255,255),thickness=-1)
            temp = cv.Avg(self.image.getBitmap(),mask)
            self._avgColor = (temp[0],temp[1],temp[2])
        return self._avgColor
  
    def colorDistance(self, color = (0, 0, 0)): 
        """
          Return the euclidean color distance of the color tuple at x,y from a given color (default black)
        """
        return spsd.euclidean(np.array(color), np.array(self.meanColor())) 
  
    def perimeter(self):
        """
        **SUMMARY**
        
        Returns the perimeter of the circle feature in pixels.
        """
        return 2*pi*self._r
  
    def width(self):
        """
        **SUMMARY** 

        Returns the width of the feature -- for compliance just r*2

        """
        return self._r*2
  
    def height(self):
        """
        **SUMMARY**

        Returns the height of the feature -- for compliance just r*2
        """
        return self._r*2
  
    def radius(self):
        """
        **SUMMARY**
        
        Returns the radius of the circle in pixels.

        """
        return self._r
    
    def diameter(self):
        """
        **SUMMARY**

        Returns the diameter of the circle in pixels.

        """
        return self._r*2
    
    def crop(self,noMask=False):
        """
        **SUMMARY**

        This function returns the largest bounding box for an image.

        **PARAMETERS**
       
        * *noMask* - if noMask=True we return the bounding box image of the circle.
          if noMask=False (default) we return the masked circle with the rest of the area set to black
          
        **RETURNS**
        
        The masked circle image. 
          
        """
        if( noMask ):
            return self.image.crop(self.x, self.y, self.width(), self.height(), centered = True)
        else:
            mask = self.image.getEmpty(1)
            result = self.image.getEmpty()
            cv.Zero(mask)
            cv.Zero(result)
            #if you want to shave a bit of time we go do the crop before the blit
            cv.Circle(mask,(int(self.x),int(self.y)),int(self._r),color=(255,255,255),thickness=-1)
            cv.Copy(self.image.getBitmap(),result,mask)
            retVal = Image(result)
            retVal = retVal.crop(self.x, self.y, self.width(), self.height(), centered = True)
            return retVal

######################################################################    
class Motion(Feature):
    """
    **SUMMARY**

    The motion feature is used to encapsulate optical flow vectors. The feature
    holds the length and direction of the vector.

    """
    x = 0.0
    y = 0.0 
    image = "" #parent image
    points = []
    dx = 0.00
    dy = 0.00
    norm_dy = 0.00
    norm_dx = 0.00
    window = 7 

    def __init__(self, i, at_x, at_y,dx,dy,wndw):
        """
        i    - the source image.
        at_x - the sample x pixel position on the image.
        at_y - the sample y pixel position on the image.
        dx   - the x component of the optical flow vector.
        dy   - the y component of the optical flow vector.
        wndw - the size of the sample window (we assume it is square).
        """
        self.dx = dx  # the direction of the vector
        self.dy = dy 
        self.window = wndw # the size of the sample window
        sz = wndw/2
        # so we center at the flow vector
        points  = [(at_x+sz,at_y+sz),(at_x-sz,at_y+sz),(at_x+sz,at_y+sz),(at_x+sz,at_y-sz)]
        super(Motion, self).__init__(i, at_x, at_y, points)                                        

    def draw(self, color = Color.GREEN, width=1,normalize=True):
        """        
        **SUMMARY**
        Draw the optical flow vector going from the sample point along the length of the motion vector.

        **PARAMETERS**
        
        * *color* - An RGB color triplet. 
        * *width* - if width is less than zero we draw the feature filled in, otherwise we draw the
          contour using the specified width.
        * *normalize* - normalize the vector size to the size of the block (i.e. the biggest optical flow
          vector is scaled to the size of the block, all other vectors are scaled relative to
          the longest vector. 
          
        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer. 

        """
        new_x = 0
        new_y = 0
        if( normalize ):
            win = self.window/2
            w = math.sqrt((win*win)*2)
            new_x = (self.norm_dx*w) + self.x
            new_y = (self.norm_dy*w) + self.y
        else:
            new_x = self.x + self.dx
            new_y = self.y + self.dy

        self.image.dl().line((self.x,self.y),(new_x,new_y),color,width)

    
    def normalizeTo(self, max_mag):
        """
        **SUMMARY**

        This helper method normalizes the vector give an input magnitude. 
        This is helpful for keeping the flow vector inside the sample window.
        """
        if( max_mag == 0 ):
            self.norm_dx = 0
            self.norm_dy = 0
            return None
        mag = self.magnitude()
        new_mag = mag/max_mag
        unit = self.unitVector()
        self.norm_dx = unit[0]*new_mag
        self.norm_dy = unit[1]*new_mag
    
    def magnitude(self):
        """
        Returns the magnitude of the optical flow vector. 
        """
        return sqrt((self.dx*self.dx)+(self.dy*self.dy))

    def unitVector(self):
        """
        Returns the unit vector direction of the flow vector as an (x,y) tuple.
        """
        mag = self.magnitude()
        if( mag != 0.00 ):
            return (float(self.dx)/mag,float(self.dy)/mag) 
        else:
            return (0.00,0.00)

    def vector(self):
        """
        Returns the raw direction vector as an (x,y) tuple.
        """
        return (self.dx,self.dy)
    
    def windowSz(self):
        """
        Return the window size that we sampled over. 
        """
        return self.window

    def meanColor(self):
        """
        Return the color tuple from x,y
        **SUMMARY**

        Return a numpy array of the average color of the area covered by each Feature.

        **RETURNS**

        Returns an array of RGB triplets the correspond to the mean color of the feature.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> kp = img.findKeypoints()
        >>> c = kp.meanColor()

        """
        x = int(self.x-(self.window/2))
        y = int(self.y-(self.window/2))
        return self.image.crop(x,y,int(self.window),int(self.window)).meanColor()

    
    def crop(self):
        """
        This function returns the image in the sample window around the flow vector.
        
        Returns Image
        """
        x = int(self.x-(self.window/2))
        y = int(self.y-(self.window/2))
        
        return self.image.crop(x,y,int(self.window),int(self.window))


######################################################################    
class KeypointMatch(Feature):
    """
    This class encapsulates a keypoint match between images of an object.
    It is used to record a template of one image as it appears in another image
    """
    x = 0.00
    y = 0.00 
    image = "" #parent image
    points = []
    _minRect = []
    _avgColor = None
    _homography = []
    _template = None
    def __init__(self, image,template,minRect,_homography):
        self._template = template
        self._minRect = minRect
        self._homography = _homography
        xmax = 0
        ymax = 0
        xmin = image.width
        ymin = image.height
        for p in minRect:
            if( p[0] > xmax ):
                xmax = p[0]
            if( p[0] < xmin ):
                xmin = p[0]
            if( p[1] > ymax ):
                ymax = p[1]
            if( p[1] < xmin ):
                ymin = p[1]

        width = (xmax-xmin)
        height = (ymax-ymin)
        at_x = xmin + (width/2)
        at_y = ymin + (height/2)
        #self.x = at_x
        #self.y = at_y
        points = [(xmin,ymin),(xmin,ymax),(xmax,ymax),(xmax,ymin)]  
        #self._updateExtents()
        #self.image = image
        #points = 
        super(KeypointMatch, self).__init__(image, at_x, at_y, points)                                        
  
    def draw(self, color = Color.GREEN,width=1):
        """
        The default drawing operation is to draw the min bounding 
        rectangle in an image. 

        **SUMMARY**

        Draw a small circle around the corner.  Color tuple is single parameter, default is Red.

        **PARAMETERS**
        
        * *color* - An RGB color triplet. 
        * *width* - if width is less than zero we draw the feature filled in, otherwise we draw the
          contour using the specified width.

          
        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer. 


        """
        self.image.dl().line(self._minRect[0],self._minRect[1],color,width)
        self.image.dl().line(self._minRect[1],self._minRect[2],color,width)
        self.image.dl().line(self._minRect[2],self._minRect[3],color,width)
        self.image.dl().line(self._minRect[3],self._minRect[0],color,width)

    def drawRect(self, color = Color.GREEN,width=1):
        """
        This method draws the axes alligned square box of the template 
        match. This box holds the minimum bounding rectangle that describes
        the object. If the minimum bounding rectangle is axes aligned
        then the two bounding rectangles will match. 
        """
        self.image.dl().line(self.points[0],self.points[1],color,width)
        self.image.dl().line(self.points[1],self.points[2],color,width)
        self.image.dl().line(self.points[2],self.points[3],color,width)
        self.image.dl().line(self.points[3],self.points[0],color,width)
        
    
    def crop(self):
        """
        Returns a cropped image of the feature match. This cropped version is the 
        axes aligned box masked to just include the image data of the minimum bounding
        rectangle.
        """
        TL = self.topLeftCorner()
        raw = self.image.crop(TL[0],TL[0],self.width(),self.height()) # crop the minbouding rect
        mask = Image((self.width(),self.height()))
        mask.dl().polygon(self._minRect,color=Color.WHITE,filled=TRUE)
        mask = mask.applyLayers()
        mask.blit(raw,(0,0),alpha=None,mask=mask) 
        return mask
    
    def meanColor(self):
        """
        return the average color within the circle
        **SUMMARY**

        Return a numpy array of the average color of the area covered by each Feature.

        **RETURNS**

        Returns an array of RGB triplets the correspond to the mean color of the feature.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> kp = img.findKeypoints()
        >>> c = kp.meanColor()

        """
        if( self._avgColor is None ):
            TL = self.topLeftCorner()
            raw = self.image.crop(TL[0],TL[0],self.width(),self.height()) # crop the minbouding rect
            mask = Image((self.width(),self.height()))
            mask.dl().polygon(self._minRect,color=Color.WHITE,filled=TRUE)
            mask = mask.applyLayers()
            retVal = cv.Avg(raw.getBitmap(),mask._getGrayscaleBitmap())
            self._avgColor = retVal
        else:
            retVal = self._avgColor
        return retVal 

  
    def getMinRect(self):
        """
        Returns the minimum bounding rectangle of the feature as a list
        of (x,y) tuples. 
        """
        return self._minRect
    
    def getHomography(self):
        """
        Returns the _homography matrix used to calulate the minimum bounding
        rectangle. 
        """
        return self._homography
