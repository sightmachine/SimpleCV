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
from math import *
from math import pi


######################################################################
class Corner(Feature):
    """
    The Corner feature is a point returned by the FindCorners function
    Corners are used in machine vision as a very computationally low way
    to find unique features in an image.  These corners can be used in
    conjunction with many other algorithms.
    """
    def __init__(self, i, at_x, at_y):
        super(Corner, self).__init__(i, at_x, at_y)
        self.points = [(at_x,at_y)]
        #not sure if we need all four
        self.boundingBox = [(at_x-1,at_y-1),(at_x-1,at_y+1),(at_x+1,at_y+1),(at_x+1,at_y-1)]
        self.points = self.boundingBox
        #can we look at the eigenbuffer and find direction?
  
    def draw(self, color = (255, 0, 0),width=1):
        """
        Draw a small circle around the corner.  Color tuple is single parameter, default Red 
        """
        self.image.drawCircle((self.x, self.y), 4, color,width)

######################################################################
class Line(Feature):
    """
    The Line class is returned by the findLines function, but can also be initialized with any two points:
  
    l = Line(Image, point1, point2) 
    Where point1 and point2 are coordinate tuples
  
    l.points will be a tuple of the two points
    """
    #TODO - A nice feature would be to calculate the endpoints of the line.

    def __init__(self, i, line):
        self.image = i
        #coordinate of the line object is the midpoint
        self.x = (line[0][0] + line[1][0]) / 2
        self.y = (line[0][1] + line[1][1]) / 2
        self.points = copy(line)
        #not sure if this is going to work
        self.boundingBox = self.points
 
    def draw(self, color = (0, 0, 255),width=1):
        """
        Draw the line, default color is blue
        """
        self.image.drawLine(self.points[0], self.points[1], color,width)
      
    def length(self):
        """
        Compute the length of the line
        """
        return spsd.euclidean(self.points[0], self.points[1])  
 
    def meanColor(self):
        """
        Returns the mean color of pixels under the line.  Note that when the line falls "between" pixels, each pixels color contributes to the weighted average.
        """
     
        #we're going to walk the line, and take the mean color from all the px
        #points -- there's probably a much more optimal way to do this
        #also note, if you've already called "draw()" you've destroyed this info
        (pt1, pt2) = self.points
        maxy = max(pt1[1], pt2[1])
        miny = min(pt1[1], pt2[1])
        maxx = max(pt1[0], pt2[0])
        minx = min(pt1[0], pt2[0])
    
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
    
        return sum(weighted_clrs) / sum(weight_arr)  #return the weighted avg
 
    def angle(self):
        """
        This is the angle of the line, from the leftmost point to the rightmost point
        Returns angle (theta) in radians, with 0 = horizontal, -pi/2 = vertical positive slope, pi/2 = vertical negative slope
        """
        #first find the leftmost point 
        a = 0
        b = 1
        if (self.points[a][0] > self.points[b][0]):
            b = 0 
            a = 1
          
        d_x = self.points[b][0] - self.points[a][0]
        d_y = self.points[b][1] - self.points[a][1]
        #our internal standard is degrees
        return (360.00 * (atan2(d_y, d_x)/(2 * np.pi))) #formerly 0 was west
  
######################################################################
class Barcode(Feature):
    """
    The Barcode Feature wrappers the object returned by findBarcode(), a python-zxing object.
  
    - The x,y coordinate is the center of the code
    - points represents the four boundary points of the feature.  Note: for QR codes, these points are the reference rectangles, and are quadrangular, rather than rectangular with other datamatrix types. 
    - data is the parsed data of the code
    """
    data = ""
  
    #given a ZXing bar
    def __init__(self, i, zxbc):
        self.image = i 
        self.data = zxbc.data 
        self.points = copy(zxbc.points)
        self.boundingBox = self.points 
        numpoints = len(self.points)
        self.x = 0
        self.y = 0
    
        for p in self.points:
            self.x += p[0]
            self.y += p[1]
      
        if (numpoints):
            self.x /= numpoints
            self.y /= numpoints
  
    def draw(self, color = (255, 0, 0),width=1): 
        """
        Draws the bounding area of the barcode, given by points.  Note that for
        QR codes, these points are the reference boxes, and so may "stray" into 
        the actual code.
        """
        self.image.drawLine(self.points[0], self.points[1], color,width)
        self.image.drawLine(self.points[1], self.points[2], color,width)
        self.image.drawLine(self.points[2], self.points[3], color,width)
        self.image.drawLine(self.points[3], self.points[0], color,width)
  
    def length(self):
        """
        Returns the longest side of the quandrangle formed by the boundary points 
        """
        sqform = spsd.squareform(spsd.pdist(self.points, "euclidean"))
        #get pairwise distances for all points
        #note that the code is a quadrilateral
        return max(sqform[0][1], sqform[1][2], sqform[2][3], sqform[3][0])
  
    def area(self):
        """
        Returns the area defined by the quandrangle formed by the boundary points 
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
    The HaarFeature is a rectangle returned by the FindHaarFeature() function.
  
    - The x,y coordinates are defined by the center of the bounding rectangle
    - the classifier property refers to the cascade file used for detection 
    - points are the clockwise points of the bounding rectangle, starting in upper left
    """
    classifier = "" 
    _width = ""
    _height = ""
    neighbors = ''
    featureName = 'None'
    
    def __init__(self, i, haarobject, haarclassifier = None):
        self.image = i
        ((x, y, self._width, self._height), self.neighbors) = haarobject
        self.x = x + self._width/2
        self.y = y + self._height/2 #set location of feature to middle of rectangle
        self.points = ((x, y), (x + self._width, y), (x + self._width, y + self._height), (x, y + self._height))
        self.boundingBox = self.points
        #set bounding points of the rectangle
        self.classifier = haarclassifier
        if( haarclassifier is not None ):
            self.featureName = haarclassifier.getName()
    
    def draw(self, color = (0, 255, 0),width=1):
        """
        Draw the bounding rectangle, default color green
        """
        self.image.drawLine(self.points[0], self.points[1], color,width)
        self.image.drawLine(self.points[1], self.points[2], color,width)
        self.image.drawLine(self.points[2], self.points[3], color,width)
        self.image.drawLine(self.points[3], self.points[0], color,width)
      
    def __getstate__(self):
        dict = self.__dict__.copy()
        del dict["classifier"]
              
      
    def meanColor(self):
        """
        Find the mean color of the boundary rectangle 
        """
        crop = self.image[self.points[0][0]:self.points[1][0], self.points[0][1]:self.points[2][1]]
        return crop.meanColor()
  
    def length(self):
        """
        Returns the longest dimension of the HaarFeature, either width or height
        """
        return max(self._width, self._height)
  
    def area(self):
        """
        Returns the area contained within the HaarFeature's bounding rectangle 
        """
        return self._width * self._height
  
    def angle(self):
        """
        Returns the angle of the rectangle -- horizontal if wide, vertical if tall
        """
        #Note this is misleading
        # I am not sure I like this 
        if (self._width > self._height):
            return 0.00
        else:
            return 90.00
  
    def width(self):
        """
        Get the width of the line.
        """
        return self._width
      
    def height(self):
        """
        Get the height of the line
        """    
        return self._height
######################################################################  
class Chessboard(Feature):
    """
    This class is used for Calibration, it uses a chessboard
    to calibrate from pixels to real world measurements
    """
    spCorners = []
    dimensions = ()
    
    def __init__(self, i, dim, subpixelCorners):
        self.dimensions = dim
        self.spCorners = subpixelCorners
        self.image = i
        self.x = np.average(np.array(self.spCorners)[:, 0])
        self.y = np.average(np.array(self.spCorners)[:, 1])
        
        posdiagsorted = sorted(self.spCorners, key = lambda corner: corner[0] + corner[1])
        #sort corners along the x + y axis
        negdiagsorted = sorted(self.spCorners, key = lambda corner: corner[0] - corner[1])
        #sort corners along the x - y axis
        
        self.points = (posdiagsorted[0], negdiagsorted[-1], posdiagsorted[-1], negdiagsorted[0])
        self.boundingBox = self.points
      #return the exterior points in clockwise order
      
    def draw(self, no_needed_color = None):
        """
        Draws the chessboard corners.  We take a color param, but ignore it
        """
        cv.DrawChessboardCorners(self.image.getBitmap(), self.dimensions, self.spCorners, 1)
      
    def area(self):
        """
        Returns the mean of the distance between corner points in the chessboard
        Given that the chessboard is of a known size, this can be used as a
        proxy for distance from the camera
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
    This class is used for template (pattern) matching in images
    The template matching cannot handle scale or rotation
    """

    template_image = None
    quality = 0
    w = 0
    h = 0 

    def __init__(self, image, template, location, quality):
        self.template_image = template
        self.image = image
        self.quality = quality
        self.x = location[0]
        self.y = location[1]
        self.points = [location,
                        (location[0] + template.width, location[1]),
                        (location[0] + template.width, location[1] + template.height),
                        (location[0], location[1] + template.height)]
        self.boundingBox = self.points

    def getExtents(self):
        """
        Returns max x, max y, min x, min y
        """
        w = self.width()
        h = self.height()
        return (self.x+w, 
                self.y+w,
                self.x,
                self.y)

    def _templateOverlaps(self,other):
        """
        Returns true if this feature overlaps another template feature.
        """
        (maxx,maxy,minx,miny) = self.getExtents()
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
        (maxx,maxy,minx,miny) = self.getExtents()
        (maxx0,maxy0,minx0,miny0) = other.getExtents()

        maxx = max(maxx,maxx0)
        minx = min(minx,minx0)
        maxy = max(maxy,maxy0)
        miny = min(miny,miny0)
        self.x = minx
        self.y = miny
        self.points = ((minx,miny),(minx,maxy),(maxx,maxy),(maxx,miny))
    
 
    def rescale(self,w,h):
        """
        This method keeps the feature's center the same but sets a new width and height
        """
        (maxx,maxy,minx,miny) = self.getExtents()
        xc = minx+((maxx-minx)/2)
        yc = miny+((maxy-miny)/2)
        x = xc-(w/2)
        y = yc-(h/2)
        self.x = x
        self.y = y
        self.points = ((x,y),
                       (x+w,y),
                       (x+w,y+h),
                       (x,y+h))

    def draw(self, color = Color.GREEN, width = 1):
        self.image.dl().rectangle((self.x,self.y), (self.width(), self.height()), color = color, width=width)
######################################################################
class Circle(Feature):
    """
    Class for a general circle feature with a center at (x,y) and a radius r
    """
    x = 0.00
    y = 0.00 
    r = 0.00
    image = "" #parent image
    points = []
    avgColor = None
  
    def __init__(self, i, at_x, at_y, r):
        self.x = at_x
        self.y = at_y
        self.r = r
        self.avgColor = None
        self.image = i
        self.boundingBox = [(at_x-r,at_y-r),(at_x+r,at_y-r),(at_x+r,at_y+r),(at_x-r,at_y+r)]
        segments = 18
        rng = range(1,segments+1)
        self.points = []
        for theta in rng:
            rp = 2.0*math.pi*float(theta)/float(segments)
            x = (r*math.sin(rp))+at_x
            y = (r*math.cos(rp))+at_y
            self.points.append((x,y))
  
    def coordinates(self):
        """
        Return a an array of x,y
        """
        return np.array([self.x, self.y])  
  
    def draw(self, color = Color.GREEN,width=1):
        """
        With no dimension information, color the x,y point for the featuer 
        """
        self.image.drawCircle((self.x,self.y),self.r,color=color,thickness=width)
    
    def show(self, color = Color.GREEN):
        """
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
        Given a point (default to center of the image), return the euclidean distance of x,y from this point
        """
        if (point[0] == -1 or point[1] == -1):
            point = np.array(self.image.size()) / 2
        return spsd.euclidean(point, [self.x, self.y]) 
  
    def meanColor(self):
        """
        return the average color within the circle
        """
        #generate the mask
        if( self.avgColor is None):
            mask = self.image.getEmpty(1)
            cv.Zero(mask)
            cv.Circle(mask,(self.x,self.y),self.r,color=(255,255,255),thickness=-1)
            temp = cv.Avg(self.image.getBitmap(),mask)
            self.avgColor = (temp[0],temp[1],temp[2])
        return self.avgColor
  
    def colorDistance(self, color = (0, 0, 0)): 
        """
          Return the euclidean color distance of the color tuple at x,y from a given color (default black)
        """
        return spsd.euclidean(np.array(color), np.array(self.meanColor())) 
  
  
    def area(self):
        """
        Area covered by the feature -- for a pixel, 1
        """
        return self.r*self.r*pi

    def perimeter(self):
        """
        Perimeter of the feature in pixels
        """
        return 2*pi*self.r
  
    def width(self):
        """
        Width of the feature -- for compliance just r*2
        """
        return self.r*2
  
    def height(self):
        """
        Height of the feature -- for compliance just r*2
        """
        return self.r*2
  
    def radius(self):
        """
        Radius of the circle in pixels.
        """
        return self.r
    
    def diameter(self):
        """
        Diameter of the circle in pixels
        """
        return self.r*2
    
    def crop(self,noMask=False):
        """
        This function returns the largest bounding box for an image.
        if noMask=True we return the bounding box image of the circle.
        if noMask=False (default) we return the masked circle with the rest of the area set to black
        Returns Image
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
    Class for a SURF/SIFT/ORB/STAR keypoint
    """
    x = 0.00
    y = 0.00 
    r = 0.00
    image = "" #parent image
    points = []
    avgColor = None
    mAngle = 0
    mOctave = 0
    mResponse = 0.00
    mFlavor = ""
    mDescriptor = None
    mKeyPoint = None
    def __init__(self, i, keypoint, descriptor=None, flavor="SURF" ):
#i, point, diameter, descriptor=None,angle=-1, octave=0,response=0.00,flavor="SURF"):
        self.mKeyPoint = keypoint
        self.x = keypoint.pt[1]
        self.y = keypoint.pt[0]
        self.r = keypoint.size/2.0
        self.avgColor = None
        self.image = i
        self.mAngle = keypoint.angle
        self.mOctave = keypoint.octave
        self.mResponse = keypoint.response
        self.mFlavor = flavor
        self.mDescriptor = descriptor
        x = self.x
        y = self.y
        r = self.r
        self.boundingBox = ((x+r,y+r),(x+r,y-r),(x-r,y-r),(x-r,y+r))
        segments = 18
        rng = range(1,segments+1)
        self.points = []
        for theta in rng:
            rp = 2.0*math.pi*float(theta)/float(segments)
            x = (r*math.sin(rp))+self.x
            y = (r*math.cos(rp))+self.y
            self.points.append((x,y))
 

    def getObject(self):
        return self.mKeyPoint

    def descriptor(self):
        return self.mDescriptor

    def quality(self):
        return self.mResponse 

    def octave(self):
        return self.mOctave

    def flavor(self):
        return self.mFlavor

    def angle(self):
        return self.mAngle

    def coordinates(self):
        """
        Return a an array of x,y
        """
        return np.array([self.x, self.y])  
  
    def draw(self, color = Color.GREEN, width=1):
        """
        With no dimension information, color the x,y point for the featuer 
        """
        self.image.drawCircle((self.x,self.y),self.r,color=color,thickness=width)
        pt1 = (int(self.x),int(self.y))
        pt2 = (int(self.x+(self.radius()*sin(radians(self.angle())))),
               int(self.y+(self.radius()*cos(radians(self.angle())))))
        self.image.drawLine(pt1,pt2,color,thickness=width)
    
    def show(self, color = Color.GREEN):
        """
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
        Given a point (default to center of the image), return the euclidean distance of x,y from this point
        """
        if (point[0] == -1 or point[1] == -1):
            point = np.array(self.image.size()) / 2
        return spsd.euclidean(point, [self.x, self.y]) 
  
    def meanColor(self):
        """
        return the average color within the circle
        """
        #generate the mask
        if( self.avgColor is None):
            mask = self.image.getEmpty(1)
            cv.Zero(mask)
            cv.Circle(mask,(int(self.x),int(self.y)),int(self.r),color=(255,255,255),thickness=-1)
            temp = cv.Avg(self.image.getBitmap(),mask)
            self.avgColor = (temp[0],temp[1],temp[2])
        return self.avgColor
  
    def colorDistance(self, color = (0, 0, 0)): 
        """
          Return the euclidean color distance of the color tuple at x,y from a given color (default black)
        """
        return spsd.euclidean(np.array(color), np.array(self.meanColor())) 
  
  
    def area(self):
        """
        Area covered by the feature -- for a pixel, 1
        """
        return self.r*self.r*pi

    def perimeter(self):
        """
        Perimeter of the feature in pixels
        """
        return 2*pi*self.r
  
    def width(self):
        """
        Width of the feature -- for compliance just r*2
        """
        return self.r*2
  
    def height(self):
        """
        Height of the feature -- for compliance just r*2
        """
        return self.r*2
  
    def radius(self):
        """
        Radius of the circle in pixels.
        """
        return self.r
    
    def diameter(self):
        """
        Diameter of the circle in pixels
        """
        return self.r*2
    
    def crop(self,noMask=False):
        """
        This function returns the largest bounding box for an image.
        if noMask=True we return the bounding box image of the circle.
        if noMask=False (default) we return the masked circle with the rest of the area set to black
        Returns Image
        """
        if( noMask ):
            return self.image.crop(self.x, self.y, self.width(), self.height(), centered = True)
        else:
            mask = self.image.getEmpty(1)
            result = self.image.getEmpty()
            cv.Zero(mask)
            cv.Zero(result)
            #if you want to shave a bit of time we go do the crop before the blit
            cv.Circle(mask,(int(self.x),int(self.y)),int(self.r),color=(255,255,255),thickness=-1)
            cv.Copy(self.image.getBitmap(),result,mask)
            retVal = Image(result)
            retVal = retVal.crop(self.x, self.y, self.width(), self.height(), centered = True)
            return retVal

######################################################################    
class Motion(Feature):
    """
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
        self.x = at_x # the sample point of the flow vector
        self.y = at_y
        self.dx = dx  # the direction of the vector
        self.dy = dy 
        self.image = i # the source image
        self.window = wndw # the size of the sample window
        sz = wndw/2
        # so we center at the flow vector
        self.points  = [(at_x+sz,at_y+sz),(at_x-sz,at_y+sz),(at_x+sz,at_y-sz),(at_x-sz,at_y-sz)]
        self.bounds = self.points

    def draw(self, color = Color.GREEN, width=1,normalize=True):
        """
        Draw the optical flow vector going from the sample point along the length of the motion vector
        
        normalize - normalize the vector size to the size of the block (i.e. the biggest optical flow
                    vector is scaled to the size of the block, all other vectors are scaled relative to
                    the longest vector. 

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

        self.image.drawLine((self.x,self.y),(new_x,new_y),color,width)

    
    def normalizeTo(self, max_mag):
        """
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
    minRect = []
    avgColor = None
    homography = []
    template = None
    def __init__(self, image,template,minRect,homography):
        self.image = image
        self.template = template
        self.minRect = minRect
        self.homography = homography
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

        self.points = ((xmin,ymin),(xmin,ymax),(xmax,ymax),(xmax,ymin))
        self.width = (xmax-xmin)
        self.height = (ymax-ymin)
        self.x = xmin + (self.width/2)
        self.y = ymin + (self.height/2)
   
    def coordinates(self):
        """
        Return a an array of x,y
        """
        return np.array([self.x, self.y])  
  
    def draw(self, color = Color.GREEN,width=1):
        """
        The default drawing operation is to draw the min bounding 
        rectangle in an image. 
        """
        self.image.drawLine(self.minRect[0],self.minRect[1],color=color,thickness=width)
        self.image.drawLine(self.minRect[1],self.minRect[2],color=color,thickness=width)
        self.image.drawLine(self.minRect[2],self.minRect[3],color=color,thickness=width)
        self.image.drawLine(self.minRect[3],self.minRect[0],color=color,thickness=width)

    def drawRect(self, color = Color.GREEN,width=1):
        """
        This method draws the axes alligned square box of the template 
        match. This box holds the minimum bounding rectangle that describes
        the object. If the minimum bounding rectangle is axes aligned
        then the two bounding rectangles will match. 
        """
        self.image.drawLine(self.points[0],self.points[1],color=color,thickness=width)
        self.image.drawLine(self.points[1],self.points[2],color=color,thickness=width)
        self.image.drawLine(self.points[2],self.points[3],color=color,thickness=width)
        self.image.drawLine(self.points[3],self.points[0],color=color,thickness=width)
        
    
    def crop(self):
        """
        Returns a cropped image of the feature match. This cropped version is the 
        axes aligned box masked to just include the image data of the minimum bounding
        rectangle.
        """
        TL = self.points[0]
        raw = self.image.crop(TL[0],TL[0],self.width,self.height) # crop the minbouding rect
        mask = Image((self.width,self.height))
        mask.dl().polygon(self.minRect,color=Color.WHITE,filled=TRUE)
        mask = mask.applyLayers()
        mask.blit(raw,(0,0),alpha=None,mask=mask) 
        return mask
    
    def meanColor(self):
        """
        return the average color within the circle
        """
        if( self.avgColor is None ):
            TL = self.points[0]
            raw = self.image.crop(TL[0],TL[0],self.width,self.height) # crop the minbouding rect
            mask = Image((self.width,self.height))
            mask.dl().polygon(self.minRect,color=Color.WHITE,filled=TRUE)
            mask = mask.applyLayers()
            retVal = cv.Avg(raw.getBitmap(),mask._getGrayscaleBitmap())
            self.avgColor = retVal
        else:
            retVal = self.avgColor
        return retVal 

  
    def getMinRect(self):
        """
        Returns the minimum bounding rectangle of the feature as a list
        of (x,y) tuples. 
        """
        return self.minRect
    
    def getHomography(self):
        """
        Returns the homography matrix used to calulate the minimum bounding
        rectangle. 
        """
        return self.homography
