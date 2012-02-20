# SimpleCV Feature library
#
# Tools return basic features in feature sets


#load system libraries
from SimpleCV.base import *
from SimpleCV.Color import *


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
  
    def draw(self, color = Color.GREEN, autocolor = False):
        """
        Call draw() on each feature in the FeatureSet. 
        """
        for f in self:
            if(autocolor):
                color = Color().getRandom()
            f.draw(color)
    
    def show(self, color = Color.GREEN, autocolor = False):
        """
        This function will automatically draw the features on the image and show it.
        It is a basically a shortcut function for development and is the same as:
        
        >>> img = Image("logo")
        >>> feat = img.findBlobs()
        >>> if feat: feat.draw()
        >>> img.show()

        """

        self.draw(color, autocolor)
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
        
        """
        return np.appray([f.isContainedWithin(region) for f in self])

    def outside(self,region):
        """
        Returns the oposite of inside
        """
        return np.appray([f.isNotContainedWithin(region) for f in self])

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
    x = 0.000
    y = 0.00 
    mMaxX = None
    mMaxY = None
    mMinX = None
    mMinY = None
    image = "" #parent image
    points = []
  
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
            for p in points:
                if( p[0] > self.mMaxX):
                    self.mMaxX = p[0] 
                if( p[0] < self.mMinX):
                    self.mMinX = p[0]
                if( p[1] > self.mMaxY):
                    self.mMaxY = p[1]
                if( p[1] < self.mMinY):
                    self.mMinY = p[1]
        
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
            return( self.minY() > object.maxY() )
        elif( isinstance(object,tuple) or isinstance(object,'ndarray') ):
            return( self.minY() > object[1]  )
        else:
            warnings.warn("SimpleCV did not recognize the input type to feature.above(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None
    
    def below(self,object):
        """
        Given a point or another blob determine if this blob is below the other blob
        """    
        if( isinstance(object,Feature) ): 
            return( self.maxY() < object.minY() )
        elif( isinstance(object,tuple) or isinstance(object,'ndarray') ):
            return( self.maxY() < object[1]  )
        else:
            warnings.warn("SimpleCV did not recognize the input type to feature.below(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None
 
     
    def right(self,object):
        """
        Given a point or another blob determine if this blob is to the right of the other blob
        """
        if( isinstance(object,Feature) ): 
            return( self.maxX() < object.minX() )
        elif( isinstance(object,tuple) or isinstance(object,'ndarray') ):
            return( self.maxX() < object[0]  )
        else:
            warnings.warn("SimpleCV did not recognize the input type to feature.right(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None

    def left(self,object):
        """
        Given a point or another blob determine if this blob is to the left of the other blob
        """           
        if( isinstance(object,Feature) ): 
            return( self.minX() > object.maxX() )
        elif( isinstance(object,tuple) or isinstance(object,'ndarray') ):
            return( self.minX() > object[0]  )
        else:
            warnings.warn("SimpleCV did not recognize the input type to feature.left(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None

    def contains(self,other,simple=True):
        """
        Returns true if this blob contains the point, all of a collection of points, or the entire other blo in other
        """
        if( isinstance(other,Feature) ):
            retVal = False
            if( simple ): 
                if( other.minX() >=  self.minX() and other.minX() <= self.maxX() and
                    other.minY() >=  self.minY() and other.minY() <= self.maxY() and
                    other.maxX() >=  self.minX() and other.maxX() <= self.maxX() and
                    other.maxY() >=  self.minY() and other.maxY() <= self.maxY() ):
                    retVal = True            
            else:
                for p in other.pts: # this isn't completely correct - only tests if points lie in poly, not edges. 
                    retVal = self._pointInsidePolygon(p,self.pts)
                    if( not retVal ):
                        break
                
            return retVal
        elif(isinstance(other,tuple) or isinstance(other,'ndarray') ):
            if( simple ):
                return( other[0] <= self.maxX() and
                        other[0] >= self.minX() and
                        other[1] <= self.maxY() and
                        other[1] >= self.minY() )
            else:
                return self._pointInsidePolygon(other,self.pts)
        else:
            warnings.warn("SimpleCV did not recognize the input type to features.contains. This method only takes another blob, an (x,y) tuple, or a ndarray type.")
            return None  
    
    def overlaps(self, other, simple=True):
        """
        Returns true if this blob contains at least one point, part of a collection
        of points, or any part of a blob.        
        """
        retVal = False
        if( isinstance(other,Feature) ):
            if( simple ):
                if( self.contains(other.topRightCorner()) or self.contains(other.topLeftCorner()) or
                    self.contains(other.bottomLeftCorner()) or self.contains(other.bottomRightCorner())):    
                    retVal = True           
            else:
                for p in other.pts: # this isn't completely correct - only tests if points lie in poly, not edges. 
                    retVal = self._pointInsidePolygon(p,self.pts)
                    if( not retVal ):
                        break
                
        else:
            warnings.warn("SimpleCV did not recognize the input type to feature.overlap. This method only takes another blob.")
            retVal = None

        return retVal

    def doesNotContain(self, other,simple=True):
        """
        Returns true if all of features points are inside this point.
        """
        return not self.contains(other,simple)

    def doesNotOverlap( self, other,simple=True):
        """
        Returns true if none of the feature's points overlap with the other feature.
        """
        return not self.overlaps( other, simple)


    def isContainedWithin(self,other,simple=True):
        """
        Returns true if this feature is contained within the structure stored in other. Other can be one of the following 
        types:
        Any feature type
        A bounding box tuple of the form (x,y,w,h)
        A bounding circle tuple of the form (x,y,r)
        A list of (x,y) tuples defining a polygon.
        """
        retVal = True
        if( isinstance(other,Feature) ):
            retVal = other.contains(self)
        elif( isinstance(other,tuple) and len(other)==3 ):
            #assume we are in x,y, r format 
            rr = other[2]*other[2]
            x = other[0]
            y = other[1]
            for p in self.pts:
                test = ((x-pt[0])*(x-pt[0]))+((y-pt[1])*(y-pt[1]))
                if( test > rr ):
                    retVal = False
                    break
        elif( isinstance(other,tuple) and len(other)==4 and 
            ( isinstance(other[0],float) or isinstance(other[0],int))): # we assume a tuple of four is (x,y,w,h)
            retVal = ( self.maxX() <= other[0]+other[2] and
                       self.minX() >= other[0] and
                       self.maxY() <= other[1]+other[3] and
                       self.minY() >= other[1] )
        elif(isinstance(other,tuple) >= 4):
            #everything else .... 
            sz = len(other)
            if( sz > len(pts)): # easier to test if we're inside 
                for p in self.pts:
                    test = self._pointInsidePolygon(p,other)
                    if(not test):
                        retVal = False
                        break 
            else: # otherwise it cheaper to test that all of the points are outside of us
                for p in other:
                    test = self._pointInsidePolygon(p,self.pts)
                    if( test ):
                        retVal = False
                        break
        else:
            warnings.warn("SimpleCV did not recognize the input type to features.contains. This method only takes another blob, an (x,y) tuple, or a ndarray type.")
            retVal = False
        return retVal


    def isNotContainedWithin(self,shape,simple=True):
        """
        """
        return not self.isContainedWithin(shape,simple)

    def _pointInsidePolygon(self,point,polygon):
        """
        returns true if tuple point (x,y) is inside polygon of the form ((a,b),(c,d),...,(a,b)) the polygon should be closed
        Adapted for python from:
        http://paulbourke.net/geometry/insidepoly/
        """
        retval = True
        counter = 0
        p1 = None
        for p2 in polygon:
            if( p1 is None ):
                p1 = p2
            else:
                if( point[1] > np.min((p1[1],p2[1])) ):
                    if( point[1] <= np.max((p1[1],p2[1])) ):
                        if( point[0] <= np.max((p1[0],p2[0])) ):
                            if( p1[1] != p2[1] ):
                                test = (point[1]-p1[1])*(p2[0]-p1[0])/((p2[1]-p1[1])+p1[0])
                                if( p1[0] == p2[0] or point[0] <= test ):
                                    counter = counter + 1
                                
                                    
        if( counter % 2 == 0 ):
            retVal = False
        return retVal

#--------------------------------------------- 
