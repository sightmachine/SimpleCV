from SimpleCV.base import *
from SimpleCV.ImageClass import * 
from SimpleCV.Features import Feature, FeatureSet
class Blob(Feature):
    # In general the factory will get most of this stuff, or allow the user
    # to get the data if they really need it. My preference is for this is
    # that this lass holds as a little of the open CV data structures as possible
    # just because having a bunch of memory pointers around seems really unpythonic
    # the other difficulty is interior contours. Do we nest them or not?
    mContour = [] # the blob's outer perimeter as a set of (x,y) tuples 
    mConvexHull = [] # the convex hull contour as a set of (x,y) tuples
    mMinRectangle = [] #the smallest box rotated to fit the blob
    mBoundingBox = [] #get W/H and X/Y from this
    mHuMoments = [] # The seven Hu Moments
    mPerimeter = 0 # the length of the perimeter in pixels 
    mArea = 0 # the area in pixels
    m00 = 0
    m01 = 0
    m10 = 0
    m11 = 0
    m20 = 0
    m02 = 0
    m21 = 0
    m12 = 0
    mLabel = "" # A user label
    mLabelColor = [] # what color to draw the label
    mAvgColor = []#The average color of the blob's area. 
    mImg =  Image()# the segmented image of the blob
    mMask = Image()# A mask of the blob area
    mHullMask = Image()#A mask of the hull area ... we may want to use this for the image mask. 
    mHoleContour = []  # list of hole contours
    #mVertEdgeHist = [] #vertical edge histogram
    #mHortEdgeHist = [] #horizontal edge histgram
    
    def __init__(self):
        self.mContour = []
        self.mConvexHull = []
        self.mMinRectangle = [-1,-1,-1,-1,-1] #angle from this
        self.mBoundingBox = [-1,-1,-1,-1] #get W/H and X/Y from this
        self.mHuMoments = [-1,-1,-1,-1,-1,-1,-1]
        self.mPerimeter = 0
        self.mArea = 0
        self.m00 = 0
        self.m01 = 0
        self.m10 = 0
        self.m11 = 0
        self.m20 = 0
        self.m02 = 0
        self.m21 = 0
        self.m12 = 0
        self.mLabel = "UNASSIGNED"
        self.mLabelColor = [] 
        self.mAvgColor = [-1,-1,-1]
        self.mImg = Image()# the segmented image of the blob
        self.mMask = Image()
        self.image = Image()
        self.mHullMask = Image()
        self.mHoleContour = [] 
        self.mVertEdgeHist = [] #vertical edge histogram
        self.mHortEdgeHist = [] #horizontal edge histgram

    def meanColor(self):
        """
        This function returns a tuple representing the average color of the blob
        """
        return (self.mAvgColor[0],self.mAvgColor[1],self.mAvgColor[2])

    def minX(self):
        """
        This method return the minimum x value of the bounding box of the
        the blob. 
        """
        return self.mBoundingBox[0]
        
    def maxX(self):
        """
        This method return the maximum x value of the bounding box of the
        the blob. 
        """        
        return self.mBoundingBox[0]+self.mBoundingBox[2]

    def minY(self):
        """
        This method return the minimum y value of the bounding box of the
        the blob. 
        """
        return self.mBoundingBox[1]
        
    def maxY(self):
        """
        This method return the maximum y value of the bounding box of the
        the blob. 
        """        
        return self.mBoundingBox[1]+self.mBoundingBox[3]
        
    def x(self):
        """
        The x coordinate of the centroid of the blob.
        """
        return(self.mBoundingBox[0])

    def y(self):
        """
        The y coordinate of the centroid of the blob. 
        """
        return(self.mBoundingBox[1])

    def width(self):
        """
        This method returns the width of the bounding box of the blob. 
        """
        return(self.mBoundingBox[2])

    def height(self):
        """
        This method returs the height of the bounding box of the blob. 
        """
        return(self.mBoundingBox[3])
        
    def topLeftCorner(self):
        """
        This method returns the top left corner of the bounding box of
        the blob as an (x,y) tuple.
        """
        return (self.mBoundingBox[0],self.mBoundingBox[1])

    def bottomRightCorner(self):
        """
        This method returns the bottom right corner of the bounding box of
        the blob as an (x,y) tuple.
        """        
        return (self.mBoundingBox[0]+self.mBoundingBox[2],self.mBoundingBox[1]+self.mBoundingBox[3])
        
    def bottomLeftCorner(self):
        """
        This method returns the bottom left corner of the bounding box of
        the blob as an (x,y) tuple.
        """ 
        return (self.mBoundingBox[0],self.mBoundingBox[1]+self.mBoundingBox[3])
        
    def topRightCorner(self):
        """
        This method returns the top right corner of the bounding box of
        the blob as an (x,y) tuple.
        """        
        return (self.mBoundingBox[0]+self.mBoundingBox[2],self.mBoundingBox[1])

    def area(self):
        """
        This method returns the area of the blob in terms of the number of
        pixels inside the contour. 
        """
        return(self.mArea)
    
    def length(self):
        """
        Length returns the longest dimension of the X/Y bounding box 
        """
        return max(self.mBoundingBox[2],self.mBoundingBox[3])

    def angle(self):
        """
        This method returns the angle between the horizontal and the minimum enclosing
        rectangle of the blob. The minimum enclosing rectangle IS NOT not the bounding box.
        Use the bounding box for situations where you need only an approximation of the objects
        dimensions. The minimum enclosing rectangle is slightly harder to maninpulate but
        gives much better information about the blobs dimensions. 
        """
        return(self.mMinRectangle[2])
        
    def minRectX(self):
        """
        This is the x coordinate of the centroid for the minimum bounding rectangle
        """
        return(self.mMinRectangle[0][0])
        
    def minRectY(self):
        """
        This is the y coordinate of the centroid for the minimum bounding rectangle
        """
        return(self.mMinRectangle[0][1])

    def minRectWidth(self):
        """
        This is the y coordinate of the centroid for the minimum bounding rectangle
        """
        return(self.mMinRectangle[1][0])
    
    def minRectHeight(self):
        """
        This is the y coordinate of the centroid for the minimum bounding rectangle
        """
        return(self.mMinRectangle[1][1])

    def aspectRatio(self):
        """
        This method returns the aspect ration (W/H) of the bounding box of the
        blob. 
        """
        return( float(self.mBoundingBox[2])/float(self.mBoundingBox[3]))
    
    def rectifyMajorAxis(self,axis=0):
        """
        Rectify the blob image and the contour such that the major
        axis is aligned to either vertical=0 or horizontal=1 
        """
        return None
    
    def above(self,blob):
        """
        Given a point or another blob determine if this blob is above the other blob
        """
        if(blob.__class__.__name__ == 'blob' ):
            return( self.minY() > blob.maxY() )
        elif(blob.__class__.__name__ == 'tuple'):
            return( self.minY() > blob[1] )
        elif(blob.__class__.__name__ == 'ndarray'):
            return( self.minY() > blob[1] )
        else:
            return None
 

    
    def below(self,blob):
        """
        Given a point or another blob determine if this blob is below the other blob
        """    
        if(blob.__class__.__name__ == 'blob' ):
            return( self.maxY() < blob.minY() )
        elif(blob.__class__.__name__ == 'tuple'):
            return( self.maxY() < blob[1] )
        elif(blob.__class__.__name__ == 'ndarray'):
            return( self.maxY() < blob[1] )
        else:
            return None 
    
    def right(self,blob):
        """
        Given a point or another blob determine if this blob is to the right of the other blob
        """
        if(blob.__class__.__name__ == 'blob' ):
            return( self.maxX() < blob.minX() )
        elif(blob.__class__.__name__ == 'tuple'):
            return( self.maxX() < blob[0] )
        elif(blob.__class__.__name__ == 'ndarray'):
            return( self.maxX() < blob[0] )
        else:
            return None   
     
    
    def left(self,blob):
        """
        Given a point or another blob determine if this blob is to the left of the other blob
        """           
        if(blob.__class__.__name__ == 'blob' ):
            return( self.minX() > blob.maxX() )
        elif(blob.__class__.__name__ == 'tuple'):
            return( self.minX() > blob[0] )
        elif(blob.__class__.__name__ == 'ndarray'):
            return( self.minX() > blob[0] )
        else:
            return None  
    

    def contains(self,other):
        """
        Returns true if this blob contains the point, all of a collection of points, or the entire other blo in other
        """
        if(other.__class__.__name__ == 'blob' ):
            retVal = True
            if( self.above(other) or self.below(other) or self.right(other) or self(below)):   
                retVal = False             
            return retVal;
        elif(other.__class__.__name__ == 'tuple' or other.__class__.__name__ == 'ndarray'):
            return( other[0] <= self.maxX() and
                    other[0] >= self.minX() and
                    other[1] <= self.maxY() and
                    other[1] >= self.minY() )
        else:
            return None  
    
    def overlaps(self, other):
        """
        Returns true if this blob contains at least one point, part of a collection
        of points, or any part of a blob.        
        """
        retVal = False
        if(other.__class__.__name__ == 'blob' ):
            if( self.contains(other.topRightCorner()) or self.contains(other.topLeftCorner()) or
                self.contains(other.bottomLeftCorner()) or self.contains(other.bottomRightCorner())):    
                retVal = True            
            return retVal;

        
                   
    #draw the blob to a layer
    def draw(self, color=Color.WHITE, alpha=-1, w=-1, layer=None):
        """
        Draw the blob contour to either the source image or to the specified layer
        given by layer.
        
        color = The color to render the blob.
        alpha = The alpha value of the rendered blob.
        w     = The width of the drawn blob in pixels, if w=-1 then the polygon is filled.
        layer = if layer is not None, the blob is rendered to the layer versus
                the source image. 
        """
        if( layer is not None ):
            if( w < 0 ):
                #blit the blob in
                layer.polygon(self.mContour,color,filled=True,alpha=alpha)
            else:
                lastp = self.mContour[0] #this may work better.... than the other 
                for nextp in self.mContour[1::]:
                    layer.line(lastp,nextp,color,width=w,alpha=alpha,antialias = False)
                    lastp = nextp
                layer.line(self.mContour[0],self.mContour[-1],color,width=w,alpha=alpha, antialias = False)
        else:
            if( w < 0 ):
                #blit the blob in
                self.image.getDrawingLayer().polygon(self.mContour,color,filled=True,alpha=alpha)
            else:
                lastp = self.mContour[0] #this may work better.... than the other 
                for nextp in self.mContour[1::]:
                    self.image.getDrawingLayer().line((int(lastp[0]),int(lastp[1])),(int(nextp[0]),int(nextp[1])),color,width=w,alpha=alpha,antialias = False)
                    lastp = nextp
                self.image.getDrawingLayer().line(self.mContour[0],self.mContour[-1],color,width=w,alpha=alpha, antialias = False)      
    
    def drawHoles(self, color=Color.WHITE, alpha=-1, w=-1, layer=None):
        """
        This method renders all of the holes (if any) that are present in the blob
        
        color = The color to render the blob's holes.
        alpha = The alpha value of the rendered blob hole.
        w     = The width of the drawn blob hole in pixels, if w=-1 then the polygon is filled.
        layer = if layer is not None, the blob is rendered to the layer versus
                the source image. 
        """
        if(self.mHoleContour is None):
            return
        if( layer is not None ):
            if( w < 0 ):
                #blit the blob in
                for h in self.mHoleContour:
                    layer.polygon(h,color,filled=True,alpha=alpha)
            else:
                for h in self.mHoleContour:
                    lastp = h[0] #this may work better.... than the other 
                    for nextp in h[1::]:
                        layer.line((int(lastp[0]),int(lastp[1])),(int(nextp[0]),int(nextp[1])),color,width=w,alpha=alpha,antialias = False)
                        lastp = nextp
                    layer.line(h[0],h[-1],color,width=w,alpha=alpha, antialias = False)
        else:
            if( w < 0 ):
                #blit the blob in
                for h in self.mHoleContour:
                    self.image.getDrawingLayer().polygon(h,color,filled=True,alpha=alpha)
            else:
                for h in self.mHoleContour:
                    lastp = h[0] #this may work better.... than the other 
                    for nextp in h[1::]:
                        self.image.getDrawingLayer().line((int(lastp[0]),int(lastp[1])),(int(nextp[0]),int(nextp[1])),color,width=w,alpha=alpha,antialias = False)
                        lastp = nextp
                    self.image.getDrawingLayer().line(h[0],h[-1],color,width=w,alpha=alpha, antialias = False)
                    

    def drawHull(self, color=Color.WHITE, alpha=-1, w=-1, layer=None ):
        """
        Draw the blob's convex hull to either the source image or to the
        specified layer given by layer.
        
        color = The color to render the blob's convex hull.
        alpha = The alpha value of the rendered blob.
        w     = The width of the drawn blob in pixels, if w=-1 then the polygon is filled.
        layer = if layer is not None, the blob is rendered to the layer versus
                the source image. 
        """
        if( layer is not None ):
            if( w < 0 ):
                #blit the blob in
                layer.polygon(self.mConvexHull,color,filled=True,alpha=alpha)
            else:
                lastp = self.mConvexHull[0] #this may work better.... than the other 
                for nextp in self.mConvexHull[1::]:
                    layer.line(lastp,nextp,color,width=w,alpha=alpha,antialias = False)
                    lastp = nextp
                layer.line(self.mConvexHull[0],self.mConvexHull[-1],color,width=w,alpha=alpha, antialias = False)        
        else:
            if( w < 0 ):
                #blit the blob in
                self.image.getDrawingLayer().polygon(self.mConvexHull,color,filled=True,alpha=alpha)
            else:
                lastp = self.mConvexHull[0] #this may work better.... than the other 
                for nextp in self.mConvexHull[1::]:
                    self.image.getDrawingLayer().line(lastp,nextp,color,width=w,alpha=alpha,antialias = False)
                    lastp = nextp
                self.image.getDrawingLayer().line(self.mConvexHull[0],self.mConvexHull[-1],color,width=w,alpha=alpha, antialias = False)

    
    #draw the actual pixels inside the contour to the layer
    def drawMaskToLayer(self, layer, offset=(0,0)):
        """
        Draw the actual pixels of the blob to another layer. This is handy if you
        want to examine just the pixels inside the contour. 
            
        offset = The offset from the top left corner where we want to place the mask. 
        """
        mx = self.mBoundingBox[0]+offset[0]
        my = self.mBoundingBox[1]+offset[1]
        layer.blit(self.mImg,coordinates=(mx,my))
        return None

        