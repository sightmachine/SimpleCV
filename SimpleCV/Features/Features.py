# SimpleCV Feature library
#
# Tools return basic features in feature sets


#load system libraries
from SimpleCV.base import *
from SimpleCV.Color import *
import copy

class FeatureSet(list):
    """
    FeatureSet is a class extended from Python's list which has special functions so that it is useful for handling feature metadata on an image.
    
    In general, functions dealing with attributes will return numpy arrays, and functions dealing with sorting or filtering will return new FeatureSets.
    
    Example:
    >>> image = Image("/path/to/image.png")
    >>> lines = image.findLines()  #lines are the feature set
    >>> lines.draw()
    >>> lines.x()
    >>> lines.crop()
    """
  
    def draw(self, color = Color.GREEN,width=1, autocolor = False):
        """
        Call draw() on each feature in the FeatureSet. 
        """
        for f in self:
            if(autocolor):
                color = Color().getRandom()
            f.draw(color=color,width=width)
    
    def show(self, color = Color.GREEN, autocolor = False,width=1):
        """
        This function will automatically draw the features on the image and show it.
        It is a basically a shortcut function for development and is the same as:
        
        >>> img = Image("logo")
        >>> feat = img.findBlobs()
        >>> if feat: feat.draw()
        >>> img.show()

        """
        self.draw(color, width, autocolor)
        self[-1].image.show()
                
  
    def x(self):
        """
        Returns a numpy array of the x (horizontal) coordinate of each feature.
        """
        return np.array([f.x for f in self])
  
    def y(self):
        """
        Returns a numpy array of the y (vertical) coordinate of each feature.
        """
        return np.array([f.y for f in self])
  
    def coordinates(self):
        """
        Returns a 2d numpy array of the x,y coordinates of each feature.  This 
        is particularly useful if you want to use Scipy's Spatial Distance module 
        """
        return np.array([[f.x, f.y] for f in self]) 
  
    def area(self):
        """
        Returns a numpy array of the area of each feature in pixels.
        """
        return np.array([f.area() for f in self]) 
  
    def sortArea(self):
        """
        Returns a new FeatureSet, with the largest area features first. 
        """
        return FeatureSet(sorted(self, key = lambda f: f.area()))
  
    def distanceFrom(self, point = (-1, -1)):
        """
        Returns a numpy array of the distance each Feature is from a given coordinate.
        Default is the center of the image. 
        """
        if (point[0] == -1 or point[1] == -1 and len(self)):
            point = self[0].image.size()
            
        return spsd.cdist(self.coordinates(), [point])[:,0]
  
    def sortDistance(self, point = (-1, -1)):
        """
        Returns a sorted FeatureSet with the features closest to a given coordinate first.
        Default is from the center of the image. 
        """
        return FeatureSet(sorted(self, key = lambda f: f.distanceFrom(point)))
        
    def distancePairs(self):
        """
        Returns the square-form of pairwise distances for the featureset.
        The resulting N x N array can be used to quickly look up distances
        between features.
        """
        return spsd.squareform(spsd.pdist(self.coordinates()))
  
    def angle(self):
        """
        Return a numpy array of the angles (theta) of each feature.
        Note that theta is given in radians, with 0 being horizontal.
        """
        return np.array([f.angle() for f in self])
  
    def sortAngle(self, theta = 0):
        """
        Return a sorted FeatureSet with the features closest to a given angle first.
        Note that theta is given in radians, with 0 being horizontal.
        """
        return FeatureSet(sorted(self, key = lambda f: abs(f.angle() - theta)))
  
    def length(self):
        """
        Return a numpy array of the length (longest dimension) of each feature.
        """
       
        return np.array([f.length() for f in self])
  
    def sortLength(self):
        """
        Return a sorted FeatureSet with the longest features first. 
        """
        return FeatureSet(sorted(self, key = lambda f: f.length()))
  
    def meanColor(self):
        """
        Return a numpy array of the average color of the area covered by each Feature.
        """
        return np.array([f.meanColor() for f in self])
  
    def colorDistance(self, color = (0, 0, 0)):
        """
        Return a numpy array of the distance each features average color is from
        a given color tuple (default black, so colorDistance() returns intensity)
        """
        return spsd.cdist(self.meanColor(), [color])[:,0]
    
    def sortColorDistance(self, color = (0, 0, 0)):
        """
        Return a sorted FeatureSet with features closest to a given color first.
        Default is black, so sortColorDistance() will return darkest to brightest
        """
        return FeatureSet(sorted(self, key = lambda f: f.colorDistance(color)))
  
    def filter(self, filterarray):
        """
        Return a FeatureSet which is filtered on a numpy boolean array.  This
        will let you use the attribute functions to easily screen Features out
        of return FeatureSets.  
    
        Some examples:

        Return all lines < 200px
        >>> my_lines.filter(my_lines.length() < 200) # returns all lines < 200px
        >>> my_blobs.filter(my_blobs.area() > 0.9 * my_blobs.length**2) # returns blobs that are nearly square    
        >>> my_lines.filter(abs(my_lines.angle()) < numpy.pi / 4) #any lines within 45 degrees of horizontal
        >>> my_corners.filter(my_corners.x() - my_corners.y() > 0) #only return corners in the upper diagonal of the image
    
        """
        return FeatureSet(list(np.array(self)[np.array(filterarray)]))
  
    def width(self):
        """
        Returns a nparray which is the width of all the objects in the FeatureSet
        """
        return np.array([f.width() for f in self])
  
    def height(self):
        """
        Returns a nparray which is the height of all the objects in the FeatureSet
        """
        return np.array([f.height() for f in self])
  
    def crop(self):
        """
        Returns a nparray with the cropped features as Imges
        """
        return np.array([f.crop() for f in self])  

    def inside(self,region):
        """
        Return only the features inside the region, where region can be
        
        - A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
        - A bounding circle of the form (x,y,r)
        - A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
        - Any two dimensional feature (e.g. blobs, circle ...)
        
        - FAILS:
             line segment in region
             interior contour on blobs. 
        """
        fs = FeatureSet()
        for f in self:
            if(f.isContainedWithin(region)):
                fs.append(f)
        return fs

        
    def outside(self,region):
        """
        Returns the oposite of inside
        """
        fs = FeatureSet()
        for f in self:
            if(f.isNotContainedWithin(region)):
                fs.append(f)
        return fs

    def overlaps(self,region):
        """
        returns all features that overlap the region
        """
        fs = FeatureSet()
        for f in self: 
            if( f.overlaps(region) ):
                fs.append(f)
        return fs

    def above(self,region):
        """
        """
        fs = FeatureSet()
        for f in self: 
            if(f.above(region)):
                fs.append(f)
        return fs

    def below(self,region):
        """
        """
        fs = FeatureSet()
        for f in self: 
            if(f.below(region)):
                fs.append(f)
        return fs

    def left(self,region):
        """
        """
        fs = FeatureSet()
        for f in self: 
            if(f.left(region)):
                fs.append(f)
        return fs

    def right(self,region):
        """
        """
        fs = FeatureSet()
        for f in self: 
            if(f.right(region)):
                fs.append(f)
        return fs
       


class Feature(object):
    """
    The Feature object is an abstract class which real features descend from.
    Each feature object has:
    
    * a draw() method, 
    * an image property, referencing the originating Image object 
    * x and y coordinates
    * default functions for determining angle, area, meanColor, etc for FeatureSets
    * in the Feature class, these functions assume the feature is 1px  
    """
    x = 0.00
    y = 0.00 
    mMaxX = None
    mMaxY = None
    mMinX = None
    mMinY = None
    image = "" #parent image
    points = []
    boundingBox = []

    def __init__(self, i, at_x, at_y):
        self.x = at_x
        self.y = at_y
        self.image = i
  
    def coordinates(self):
        """
        Return a an array of x,y
        """
        return np.array([self.x, self.y])  
  
    def draw(self, color = Color.GREEN):
        """
        With no dimension information, color the x,y point for the featuer 
        """
        self.image[self.x, self.y] = color
    
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
          Return the color tuple from x,y
        """
        return self.image[self.x, self.y]
  
    def colorDistance(self, color = (0, 0, 0)): 
        """
          Return the euclidean color distance of the color tuple at x,y from a given color (default black)
        """
        return spsd.euclidean(np.array(color), np.array(self.meanColor())) 
  
    def angle(self):
        """
        Return the angle (theta) of the feature -- default 0 (horizontal)
        """
        return 0
  
    def length(self):
        """
        Longest dimension of the feature -- for a pixel, 1
        """
        return 1
  
    def area(self):
        """
        Area covered by the feature -- for a pixel, 1
        """
        return self.width() * self.height()
  
    def width(self):
        """
        Width of the feature -- defaults to 1
        """
        maxX = float("-infinity")
        minX = float("infinity")
        if(len(self.points) <= 0):
            return 1
        
        for p in self.points:
            if(p[0] > maxX):
                maxX = p[0]
            if(p[0] < minX):
                minX = p[0]
            
        return maxX - minX
  
    def height(self):
        """
        Height of the feature -- defaults to 1
        """
        maxY = float("-infinity")
        minY = float("infinity")
        if(len(self.points) <= 0):
            return 1
      
        for p in self.points:
            if(p[1] > maxY):
                maxY = p[1]
            if(p[1] < minY):
                minY = p[1]
        
        return maxY - minY

   
    def crop(self):
        """
        This function returns the largest bounding box for an image.
    
        Returns Image
        """
    
        return self.image.crop(self.x, self.y, self.width(), self.height(), centered = True)
    
    def __repr__(self):
        return "%s.%s at (%d,%d)" % (self.__class__.__module__, self.__class__.__name__, self.x, self.y)


    def _updateExtents(self):
        if( self.mMaxX is None or self.mMaxY is None or 
            self.mMinX is None or self.mMinY is None):
            self.mMaxX = float("-infinity")
            self.mMaxY = float("-infinity")
            self.mMinX = float("infinity")
            self.mMinY = float("infinity")
            for p in self.points:
                if( p[0] > self.mMaxX):
                    self.mMaxX = p[0] 
                if( p[0] < self.mMinX):
                    self.mMinX = p[0]
                if( p[1] > self.mMaxY):
                    self.mMaxY = p[1]
                if( p[1] < self.mMinY):
                    self.mMinY = p[1]
            
            self.boundingBox = [(self.mMinX,self.mMinY),(self.mMinX,self.mMaxY),(self.mMaxX,self.mMaxY),(self.mMaxX,self.mMinY)]
            
    def boundingBox(self):
        self._updateExtents()
        return self.boundingBox

    def extents(self):
        """
        return the max x, min x, max y, min y
        """
        self._updateExtents()
        return (self.mMaxX,self.mMaxY,self.mMinX,self.mMinY)

    def minY(self):
        """
        This method return the minimum y value of the bounding box of the
        the blob. 
        """
        self._updateExtents()
        return self.mMinY
        
    def maxY(self):
        """
        This method return the maximum y value of the bounding box of the
        the blob. 
        """       
        self._updateExtents()
        return self.mMaxY


    def minX(self):
        """
        This method return the minimum x value of the bounding box of the
        the blob. 
        """
        self._updateExtents()
        return self.mMinX
        
    def maxX(self):
        """
        This method return the maximum X value of the bounding box of the
        the blob. 
        """       
        self._updateExtents()
        return self.mMaxX

    def topLeftCorner(self):
        """
        This method returns the top left corner of the bounding box of
        the blob as an (x,y) tuple.
        """
        self._updateExtents()
        return (self.mMinX,self.mMinY)

    def bottomRightCorner(self):
        """
        This method returns the bottom right corner of the bounding box of
        the blob as an (x,y) tuple.
        """        
        self._updateExtents()
        return (self.mMaxX,self.mMaxY)
        
    def bottomLeftCorner(self):
        """
        This method returns the bottom left corner of the bounding box of
        the blob as an (x,y) tuple.
        """ 
        self._updateExtents()
        return (self.mMinX,self.mMaxY)
        
    def topRightCorner(self):
        """
        This method returns the top right corner of the bounding box of
        the blob as an (x,y) tuple.
        """        
        self._updateExtents()
        return (self.mMaxX,self.mMinY)


    def above(self,object):
        """
        Given a point or another blob determine if this blob is above the other blob
        """
        if( isinstance(object,Feature) ): 
            return( self.maxY() < object.minY() )
        elif( isinstance(object,tuple) or isinstance(object,np.ndarray) ):
            return( self.maxY() < object[1]  )
        elif( isinstance(object,float) or isinstance(object,int) ):
            return( self.maxY() < object )
        else:
            warnings.warn("SimpleCV did not recognize the input type to feature.above(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None
    
    def below(self,object):
        """
        Given a point or another blob determine if this blob is below the other blob
        """    
        if( isinstance(object,Feature) ): 
            return( self.minY() > object.maxY() )
        elif( isinstance(object,tuple) or isinstance(object,np.ndarray) ):
            return( self.minY() > object[1]  )
        elif( isinstance(object,float) or isinstance(object,int) ):
            return( self.minY() > object )
        else:
            warnings.warn("SimpleCV did not recognize the input type to feature.below(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None
 
     
    def right(self,object):
        """
        Given a point or another blob determine if this blob is to the right of the other blob
        """
        if( isinstance(object,Feature) ): 
            return( self.minX() > object.maxX() )
        elif( isinstance(object,tuple) or isinstance(object,np.ndarray) ):
            return( self.minX() > object[0]  )
        elif( isinstance(object,float) or isinstance(object,int) ):
            return( self.minX() > object )
        else:
            warnings.warn("SimpleCV did not recognize the input type to feature.right(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None

    def left(self,object):
        """
        Given a point or another blob determine if this blob is to the left of the other blob
        """           
        if( isinstance(object,Feature) ): 
            return( self.maxX() < object.minX() )
        elif( isinstance(object,tuple) or isinstance(object,np.ndarray) ):
            return( self.maxX() < object[0]  )
        elif( isinstance(object,float) or isinstance(object,int) ):
            return( self.maxX() < object )
        else:
            warnings.warn("SimpleCV did not recognize the input type to feature.left(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None

    def contains(self,other):
        """
        Returns true if this blob contains the point, all of a collection of points, or the entire other blo in other
        """
        retVal = False
        bounds = self.boundingBox

        if( isinstance(other,Feature) ):# A feature
            retVal = True
            for p in other.points: # this isn't completely correct - only tests if points lie in poly, not edges.            
                p2 = (int(p[0]),int(p[1]))
                retVal = self._pointInsidePolygon(p2,bounds)
                if( not retVal ):
                    break
        # a single point        
        elif( (isinstance(other,tuple) and len(other)==2) or ( isinstance(other,np.ndarray) and other.shape[0]==2) ):
            retVal = self._pointInsidePolygon(other,bounds)

        elif( isinstance(other,tuple) and len(other)==3 ): # A circle
            #assume we are in x,y, r format 
            retVal = True
            rr = other[2]*other[2]
            x = other[0]
            y = other[1]
            for p in bounds:
                test = ((x-p[0])*(x-p[0]))+((y-p[1])*(y-p[1]))
                if( test < rr ):
                    retVal = False
                    break

        elif( isinstance(other,tuple) and len(other)==4 and ( isinstance(other[0],float) or isinstance(other[0],int))): 
            retVal = ( self.maxX() <= other[0]+other[2] and
                       self.minX() >= other[0] and
                       self.maxY() <= other[1]+other[3] and
                       self.minY() >= other[1] )
        elif(isinstance(other,list) and len(other) >= 4): # an arbitrary polygon
            #everything else .... 
            retVal = True
            for p in other:
                test = self._pointInsidePolygon(p,bounds)
                if(not test):
                    retVal = False
                    break
        else:
            warnings.warn("SimpleCV did not recognize the input type to features.contains. This method only takes another blob, an (x,y) tuple, or a ndarray type.")
            return False  

        return retVal

    def overlaps(self, other):
        """
        Returns true if this blob contains at least one point, part of a collection
        of points, or any part of a blob.        
        """
        retVal = False
        bounds = self.boundingBox
        if( isinstance(other,Feature) ):# A feature
            retVal = True            
            for p in other.points: # this isn't completely correct - only tests if points lie in poly, not edges. 
                retVal = self._pointInsidePolygon(p,bounds)
                if( retVal ):
                    break
                
        elif( (isinstance(other,tuple) and len(other)==2) or ( isinstance(other,np.ndarray) and other.shape[0]==2) ):
            retVal = self._pointInsidePolygon(other,bounds)

        elif( isinstance(other,tuple) and len(other)==3 and not isinstance(other[0],tuple)): # A circle
            #assume we are in x,y, r format 
            print(other)
            retVal = False
            rr = other[2]*other[2]
            x = other[0]
            y = other[1]
            for p in bounds:
                test = ((x-p[0])*(x-p[0]))+((y-p[1])*(y-p[1]))
                if( test < rr ):
                    retVal = True
                    break

        elif( isinstance(other,tuple) and len(other)==4 and ( isinstance(other[0],float) or isinstance(other[0],int))): 
            retVal = ( self.contains( (other[0],other[1] ) ) or # see if we contain any corner
                       self.contains( (other[0]+other[2],other[1] ) ) or
                       self.contains( (other[0],other[1]+other[3] ) ) or
                       self.contains( (other[0]+other[2],other[1]+other[3] ) ) )
        elif(isinstance(other,list) and len(other)  >= 3): # an arbitrary polygon
            #everything else .... 
            retVal = False
            for p in other:
                test = self._pointInsidePolygon(p,bounds)
                if(test):
                    retVal = True
                    break
        else:
            warnings.warn("SimpleCV did not recognize the input type to features.overlaps. This method only takes another blob, an (x,y) tuple, or a ndarray type.")
            return False  

        return retVal

    def doesNotContain(self, other):
        """
        Returns true if all of features points are inside this point.
        """
        return not self.contains(other)

    def doesNotOverlap( self, other):
        """
        Returns true if none of the feature's points overlap with the other feature.
        """
        return not self.overlaps( other)


    def isContainedWithin(self,other):
        """
        Returns true if this feature is contained within the structure stored in other. Other can be one of the following 
        types:
        Any feature type
        A bounding box tuple of the form (x,y,w,h)
        A bounding circle tuple of the form (x,y,r)
        A list of (x,y) tuples defining a polygon.
        """
        retVal = True
        bounds = self.boundingBox

        if( isinstance(other,Feature) ): # another feature do the containment test
            retVal = other.contains(self)
        elif( isinstance(other,tuple) and len(other)==3 ): # a circle
            #assume we are in x,y, r format 
            rr = other[2]*other[2] # radius squared
            x = other[0]
            y = other[1]
            for p in bounds:
                test = ((x-p[0])*(x-p[0]))+((y-p[1])*(y-p[1]))
                if( test > rr ):
                    retVal = False
                    break
        elif( isinstance(other,tuple) and len(other)==4 and  # a bounding box
            ( isinstance(other[0],float) or isinstance(other[0],int))): # we assume a tuple of four is (x,y,w,h)
            retVal = ( self.maxX() <= other[0]+other[2] and
                       self.minX() >= other[0] and
                       self.maxY() <= other[1]+other[3] and
                       self.minY() >= other[1] )
        elif(isinstance(other,tuple) >= 4): # an arbitrary polygon
            #everything else .... 
            retVal = True
            for p in bounds:
                test = self._pointInsidePolygon(p,other)
                if(not test):
                    retVal = False
                    break

        else:
            warnings.warn("SimpleCV did not recognize the input type to features.contains. This method only takes another blob, an (x,y) tuple, or a ndarray type.")
            retVal = False
        return retVal


    def isNotContainedWithin(self,shape):
        """
        """
        return not self.isContainedWithin(shape)

    def _pointInsidePolygon(self,point,polygon):
        """
        returns true if tuple point (x,y) is inside polygon of the form ((a,b),(c,d),...,(a,b)) the polygon should be closed
        Adapted for python from:
        http://paulbourke.net/geometry/insidepoly/
        """
        if( len(polygon) < 3 ):
            warnings.warn("feature._pointInsidePolygon - this is not a valid polygon")
            return False 
 
        counter = 0
        retVal = True
        p1 = None
        
        poly = copy.deepcopy(polygon)
        poly.append(polygon[0])
        for p2 in poly:
            if( p1 is None ):
                p1 = p2
            else:
                if( point[1] > np.min((p1[1],p2[1])) ):
                    if( point[1] <= np.max((p1[1],p2[1])) ):
                        if( point[0] <= np.max((p1[0],p2[0])) ):
                            if( p1[1] != p2[1] ):
                                test = float((point[1]-p1[1])*(p2[0]-p1[0]))/float(((p2[1]-p1[1])+p1[0]))
                                if( p1[0] == p2[0] or point[0] <= test ):
                                    counter = counter + 1
                p1 = p2                
                                    
        if( counter % 2 == 0 ):
            retVal = False
        return retVal

#--------------------------------------------- 
