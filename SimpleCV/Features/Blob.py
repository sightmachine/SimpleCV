from SimpleCV.base import *
from SimpleCV.Features.Features import Feature, FeatureSet
from SimpleCV.Color import Color
from SimpleCV.ImageClass import Image


class Blob(Feature):
    """
    A blob is a typicall a cluster of pixels that form a feature or unique
    shape that allows it to be distinguished from the rest of the image
    Blobs typically are computed very quickly so they are used often to
    find various items in a picture based on properties.  Typically these
    things like color, shape, size, etc.   Since blobs are computed quickly
    they are typically used to narrow down search regions in an image, where
    you quickly find a blob and then that blobs region is used for more
    computational intensive type image processing
    """
    seq = '' #the cvseq object that defines this blob
    mContour = [] # the blob's outer perimeter as a set of (x,y) tuples 
    mConvexHull = [] # the convex hull contour as a set of (x,y) tuples
    mMinRectangle = [] #the smallest box rotated to fit the blob
    # mMinRectangle[0] = centroid (x,y)
    # mMinRectangle[1] = (w,h)
    # mMinRectangle[2] = angle
    
    mBoundingBox = [] #get W/H and X/Y from this
    mHu = [] # The seven Hu Moments
    mPerimeter = 0 # the length of the perimeter in pixels 
    mArea = 0 # the area in pixels
    mAspectRatio = 0
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
    mImg =  '' #Image()# the segmented image of the blob
    mMask = '' #Image()# A mask of the blob area
    mHullMask = '' #Image()#A mask of the hull area ... we may want to use this for the image mask. 
    mHoleContour = []  # list of hole contours
    #mVertEdgeHist = [] #vertical edge histogram
    #mHortEdgeHist = [] #horizontal edge histgram
    
    def __init__(self):
        self.mContour = []
        self.mConvexHull = []
        self.mMinRectangle = [-1,-1,-1,-1,-1] #angle from this
        self.mBoundingBox = [-1,-1,-1,-1] #get W/H and X/Y from this
        self.mHu = [-1,-1,-1,-1,-1,-1,-1]
        self.mPerimeter = 0
        self.mArea = 0
        self.mAspectRatio = 0
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
        self.mImg = None
        self.mMask = None
        self.image = None
        self.mHullMask = None
        self.mHoleContour = [] 
        self.mVertEdgeHist = [] #vertical edge histogram
        self.mHortEdgeHist = [] #horizontal edge histgram
        self.points = []

    def meanColor(self):
        """
        This function returns a tuple representing the average color of the blob

        Returns:
            Tuple
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

    def center(self):
        """
        This mehtod returns the center of the blob's bounding box

        Returns:
            Tuple
        """
        x = self.mBoundingBox[0]+(self.mBoundingBox[2]/2)
        y = self.mBoundingBox[1]+(self.mBoundingBox[3]/2)
        return ([x,y])

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
        finalRotation = self.angle()
        w = self.minRectWidth()
        h = self.minRectHeight()
        
        if( w > h ):
            finalRotation = finalRotation - 90
            
        if(axis > 0 ):
            finalRotation = finalRotation - 90

        self.rotate(finalRotation)  
        return None
    
    def rotate(self,angle):
        """
        Rotate the blob given the angle in degrees most of the blob elements will
        be rotated, not however this will "break" drawing back to the original image.
        To draw the blob create a new layer and draw to that layer.

        Parameters:
            angle - Int or Float
            
        """
        #FIXME: This function should return a blob
        theta = 2*np.pi*(angle/360.0)
        mode = ""
        point =(self.x,self.y)
        self.mImg = self.mImg.rotate(angle,mode,point)
        #this is a bit of a hack, but it saves a lot of code
        #I left masks as bitmaps grrrr
        tempMask = Image(self.mMask)
        self.mMask = tempMask.rotate(angle,mode,point).getBitmap()
        
        tempMask = Image(self.mHullMask)
        self.mHullMask = tempMask.rotate(angle,mode,point).getBitmap()
        
        #self.mMask.rotate(theta,"",(self.x,self.y))
        #self.mHullMask.rotate(theta,"",(self.x,self.y))
        self.mContour = map(lambda x:
                            (x[0]*np.cos(theta)-x[1]*np.sin(theta),
                             x[0]*np.sin(theta)+x[1]*np.cos(theta)),
                             self.mContour)
        self.mConvexHull = map(lambda x:
                               (x[0]*np.cos(theta)-x[1]*np.sin(theta),
                                x[0]*np.sin(theta)+x[1]*np.cos(theta)),
                               self.mConvexHull)

        if( self.mHoleContour is not None):
            for h in self.mHoleContour:
                h = map(lambda x:
                    (x[0]*np.cos(theta)-x[1]*np.sin(theta),
                     x[0]*np.sin(theta)+x[1]*np.cos(theta)),
                     h)
            

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

    def draw(self, color = Color.GREEN, alpha=-1, width=-1, layer=None):
        """
        Draw the blob, in the given color, to the appropriate layer
        
        By default, this draws the entire blob filled in, with holes.  If you
        provide a width, an outline of the exterior and interior contours is drawn.
        
        color = The color to render the blob.
        alpha = The alpha value of the rendered blob.
        width = The width of the drawn blob in pixels, if -1 then filled then the polygon is filled.
        layer = if layer is not None, the blob is rendered to the layer versus the source image.

        Parameters:
            color - Color object or Color tuple
            alpha - Int
            width - Int
            layer - DrawingLayer
        """
        if not layer:
            layer = self.image.dl()
            
        if width == -1:
            #copy the mask into 3 channels and multiply by the appropriate color
            maskred = cv.CreateImage(cv.GetSize(self.mMask), cv.IPL_DEPTH_8U, 1)
            maskgrn = cv.CreateImage(cv.GetSize(self.mMask), cv.IPL_DEPTH_8U, 1)
            maskblu = cv.CreateImage(cv.GetSize(self.mMask), cv.IPL_DEPTH_8U, 1)
            
            maskbit = cv.CreateImage(cv.GetSize(self.mMask), cv.IPL_DEPTH_8U, 3) 

            cv.ConvertScale(self.mMask, maskred, color[0] / 255.0)
            cv.ConvertScale(self.mMask, maskgrn, color[1] / 255.0)
            cv.ConvertScale(self.mMask, maskblu, color[2] / 255.0)
            
            cv.Merge(maskblu, maskgrn, maskred, None, maskbit)    
            
            masksurface = Image(maskbit).getPGSurface()
            masksurface.set_colorkey(Color.BLACK)
            if alpha != -1:
                masksurface.set_alpha(alpha)
            layer._mSurface.blit(masksurface, self.points[0])
        else:
            self.drawOutline(color, alpha, width, layer)
            self.drawHoles(color, alpha, width, layer)
            
                   
    def drawOutline(self, color=Color.GREEN, alpha=-1, width=-1, layer=None):
        """
        Draw the blob contour the given layer -- if no layer is provided, draw
        to the source image
        
        color = The color to render the blob.
        alpha = The alpha value of the rendered blob.
        width = The width of the drawn blob in pixels, -1 then the polygon is filled.
        layer = if layer is not None, the blob is rendered to the layer versus the source image.

        Parameters:
            color - Color object or Color tuple
            alpha - Int
            width - Int
            layer - DrawingLayer
        """
        
        if( layer is None ):
            layer = self.image.dl()
        
        if( width < 0 ):
            #blit the blob in
            layer.polygon(self.mContour,color,filled=True,alpha=alpha)
        else:
            lastp = self.mContour[0] #this may work better.... than the other 
            for nextp in self.mContour[1::]:
                layer.line(lastp,nextp,color,width=width,alpha=alpha,antialias = False)
                lastp = nextp
            layer.line(self.mContour[0],self.mContour[-1],color,width=width,alpha=alpha, antialias = False)
        
    
    def drawHoles(self, color=Color.GREEN, alpha=-1, width=-1, layer=None):
        """
        This method renders all of the holes (if any) that are present in the blob
        
        color = The color to render the blob's holes.
        alpha = The alpha value of the rendered blob hole.
        width = The width of the drawn blob hole in pixels, if w=-1 then the polygon is filled.
        layer = if layer is not None, the blob is rendered to the layer versus the source image.

        Parameters:
            color - Color object or Color tuple
            alpha - Int
            width - Int
            layer - DrawingLayer
        """
        if(self.mHoleContour is None):
            return
        if( layer is None ):
            layer = self.image.dl()
            
        if( width < 0 ):
            #blit the blob in
            for h in self.mHoleContour:
                layer.polygon(h,color,filled=True,alpha=alpha)
        else:
            for h in self.mHoleContour:
                lastp = h[0] #this may work better.... than the other 
                for nextp in h[1::]:
                    layer.line((int(lastp[0]),int(lastp[1])),(int(nextp[0]),int(nextp[1])),color,width=width,alpha=alpha,antialias = False)
                    lastp = nextp
                layer.line(h[0],h[-1],color,width=width,alpha=alpha, antialias = False)

    def drawHull(self, color=Color.GREEN, alpha=-1, width=-1, layer=None ):
        """
        Draw the blob's convex hull to either the source image or to the
        specified layer given by layer.
        
        color = The color to render the blob's convex hull.
        alpha = The alpha value of the rendered blob.
        width = The width of the drawn blob in pixels, if w=-1 then the polygon is filled.
        layer = if layer is not None, the blob is rendered to the layer versus the source image.

        Parameters:
            color - Color object or Color tuple
            alpha - Int
            width - Int
            layer - DrawingLayer
        """
        if( layer is None ):
            layer = self.image.dl()
            
        if( width < 0 ):
            #blit the blob in
            layer.polygon(self.mConvexHull,color,filled=True,alpha=alpha)
        else:
            lastp = self.mConvexHull[0] #this may work better.... than the other 
            for nextp in self.mConvexHull[1::]:
                layer.line(lastp,nextp,color,width=width,alpha=alpha,antialias = False)
                lastp = nextp
            layer.line(self.mConvexHull[0],self.mConvexHull[-1],color,width=width,alpha=alpha, antialias = False)        
        
    
    #draw the actual pixels inside the contour to the layer
    def drawMaskToLayer(self, layer = None, offset=(0,0)):
        """
        Draw the actual pixels of the blob to another layer. This is handy if you
        want to examine just the pixels inside the contour. 
            
        offset = The offset from the top left corner where we want to place the mask.

        Parameters:
            layer - DrawingLayer
            offset - Tuple
        """
        if( layer is not None ):
            layer = self.image.dl()
            
        mx = self.mBoundingBox[0]+offset[0]
        my = self.mBoundingBox[1]+offset[1]
        layer.blit(self.mImg,coordinates=(mx,my))
        return None
    
    def isSquare(self, tolerance = 0.05, ratiotolerance = 0.05):
        """
        Given a tolerance, test if the blob is a rectangle, and how close its
        bounding rectangle's aspect ratio is to 1.0

        Parameters:
            tolerance - Float
            ratiotolerance - Float
        """
        if self.isRectangle(tolerance) and abs(1 - self.aspectRatio()) < ratiotolerance:
            return True
        return False
            
    
    def isRectangle(self, tolerance = 0.05):
        """
        Given a tolerance, test the blob against the rectangle distance to see if
        it is rectangular

        Parameters:
            tolerance - Float
        """
        if self.rectangleDistance() < tolerance:
            return True
        return False
    
    def rectangleDistance(self):
        """
        This compares the hull mask to the bounding rectangle.  Returns the area
        of the blob's hull as a fraction of the bounding rectangle
        """
        blackcount, whitecount = Image(self.mHullMask).histogram(2)
        return abs(1.0 - float(whitecount) / (self.minRectWidth() * self.minRectHeight()))
        
    
    def isCircle(self, tolerance = 0.05):
        """
        Test circlde distance against a tolerance to see if the blob is circlular
        """
        if self.circleDistance() < tolerance:
            return True
        return False
    
    def circleDistance(self):
        """
        Compare the hull mask to an ideal circle and count the number of pixels
        that deviate as a fraction of total area of the ideal circle
        """
        idealcircle = Image((self.width(), self.height()))
        radius = min(self.width(), self.height()) / 2
        idealcircle.dl().circle((self.width()/2, self.height()/2), radius, filled= True, color=Color.WHITE)
        idealcircle = idealcircle.applyLayers()
        
        hullmask = Image(self.mHullMask)
        
        netdiff = (idealcircle - hullmask) + (hullmask - idealcircle)
        numblack, numwhite = netdiff.histogram(2)
        return float(numwhite) / (radius * radius * np.pi)

    def centroid(self):
        """
        Return the centroid (mass-determined center) of the blob
        """
        return (self.m10 / self.m00, self.m01 / self.m00)
        
    def radius(self):
        """
        Return the radius, the avg distance of each contour point from the centroid
        """
        return np.mean(spsd.cdist(self.mContour, [self.centroid()]))
        
    def hullRadius(self):
        """
        Return the radius of the convex hull contour from the centroid
        """
        return np.mean(spsd.cdist(self.mConvexHull, [self.centroid()]))
        
    def match(self, otherblob):
        """
        Compare the Hu moments between two blobs to see if they match.  Returns
        a comparison factor -- lower numbers are a closer match
        """
        #note: this should use cv.MatchShapes -- but that seems to be
        #broken in OpenCV 2.2  Instead, I reimplemented in numpy
        #according to the description in the docs for method I1 (reciprocal log transformed abs diff)
        #return cv.MatchShapes(self.seq, otherblob.seq, cv.CV_CONTOURS_MATCH_I1)

        mySigns = np.sign(self.mHu)
        myLogs = np.log(np.abs(self.mHu))
        myM = mySigns * myLogs
        
        otherSigns = np.sign(otherblob.mHu) 
        otherLogs = np.log(np.abs(otherblob.mHu))
        otherM = otherSigns * otherLogs
        
        return np.sum(abs((1/ myM - 1/ otherM)))
