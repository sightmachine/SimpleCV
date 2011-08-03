# SimpleCV Feature library
#
# Tools return basic features in feature sets


#load system libraries
from SimpleCV.base import *


class FeatureSet(list):
    """
    FeatureSet is a class extended from Python's list which has special
    functions so that it is useful for handling feature metadata on an image.
    
    In general, functions dealing with attributes will return numpy arrays, and
    functions dealing with sorting or filtering will return new FeatureSets.

    Example:

    image = Image("/path/to/image.png")
    lines = image.findLines()  #lines are the feature set
    lines.draw()
    lines.x()
    lines.crop()
    """
  
    def draw(self, color = (255, 0, 0)):
        """
        Call draw() on each feature in the FeatureSet. 
        """
        for f in self:
            f.draw(color) 
  
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
        return np.array([f.distanceFrom(point) for f in self ])
  
    def sortDistance(self, point = (-1, -1)):
        """
        Returns a sorted FeatureSet with the features closest to a given coordinate first.
        Default is from the center of the image. 
        """
        return FeatureSet(sorted(self, key = lambda f: f.distanceFrom(point)))
  
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
        return np.array([f.colorDistance(color) for f in self])
    
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
    
        Some examples::
    
        my_lines.filter(my_lines.length() < 200) # returns all lines < 200px
        my_blobs.filter(my_blobs.area() > 0.9 * my_blobs.length**2) # returns blobs that are nearly square    
        my_lines.filter(abs(my_lines.angle()) < numpy.pi / 4) #any lines within 45 degrees of horizontal
        my_corners.filter(my_corners.x() - my_corners.y() > 0) #only return corners in the upper diagonal of the image
    
        """
        return FeatureSet(list(np.array(self)[filterarray]))
  
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
        Returns a nparray which is the height of all the objects in the FeatureSet
        """
        return np.array([f.crop() for f in self])  
    
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
    x = 0.0
    y = 0.0 
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
  
    def draw(self, color = (255.0, 0.0, 0.0)):
        """
        With no dimension information, color the x,y point for the featuer 
        """
        self.image[self.x, self.y] = color
  
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
        return 1
  
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
