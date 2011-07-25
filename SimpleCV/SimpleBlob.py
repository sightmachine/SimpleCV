from SimpleCV.base import *
from SimpleCV.ImageClass import *
#blob class
class SimpleBlob:
    # In general the factory will get most of this stuff, or allow the user
    # to get the data if they really need it. My preference is for this is
    # that this lass holds as a little of the open CV data structures as possible
    # just because having a bunch of memory pointers around seems really unpythonic
    # the other difficulty is interior contours. Do we nest them or not?
    mContour = []
    mConvexHull = [] # the convex hull
    mMinRectangle = [] #the smallest box rotated to fit the blob
    mBoundingBox = [] #get W/H and X/Y from this
    mHuMoments = []
    mPerimeter = 0
    mArea = 0
    m00 = 0
    m01 = 0
    m10 = 0
    m11 = 0
    m20 = 0
    m02 = 0
    m21 = 0
    m12 = 0
    mLabel = ""
    mLabelColor = [] # what color to draw the label
    mAvgColor = []
    mImg =  Image()#    the segmented image of the blob
    mMask = Image()
    mHullMask = Image()
    mSourceImgPtr = Image()
    mHoleContour = [] 
    mVertEdgeHist = [] #vertical edge histogram
    mHortEdgeHist = [] #horizontal edge histgram
    
    def __init__(self):
        self.mContour = []
        self.mConvexHull = []
        self.mMinRectangle = [-1,-1,-1,-1] #angle from this
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
        self.mSourceImgPtr = Image()
        self.mHullMask = Image()
        self.mHoleContour = [] 
        self.mVertEdgeHist = [] #vertical edge histogram
        self.mHortEdgeHist = [] #horizontal edge histgram
        
    def x(self):
        return(mBoundingBox[0])

    def y(self):
        return(mBoundingBox[1])

    def w(self):
        return(mBoundingBox[2])

    def h(self):
        return(mBoundingBox[3])

    def mx(self):
        """
        This is the x coordinate of the centroid for the minimum bounding rectangle
        """
        return(mMinRectangle[0])
        
    def my(self):
        """
        This is the y coordinate of the centroid for the minimum bounding rectangle
        """
        return(mMinRectangle[1])
    def mw(self):
        """
        This is the y coordinate of the centroid for the minimum bounding rectangle
        """
        return(mMinRectangle[2])
    
    def mh(self):
        """
        This is the y coordinate of the centroid for the minimum bounding rectangle
        """
        return(mMinRectangle[3])
    
    def rectifyMajorAxis(self,axis=0):
        """
        Rectify the blob image and the contour such that the major
        axis is aligned to either vertical=0 or horizontal=1 
        """
    
    def above(self,blob):
        """
        Given a point or another blob determine if it is above
        the blob. 
        """
        return None
    
    def below(self,blob):
        return None
    
    def right(self,blob):
        return None
    
    def left(self,blob):
        return None
    
    def distanceTo(self,point,metric='centroid'):
        """
        The distance to another blob
        metric = 'centroid' - Get the distance between the blob and this blob's centroid
        metric = 'edge' - Get the distance to the nearest point on the blob
        metric = 'edge appx' - Get the distance to the bounding box edge. 
        """
        #if(metric=='centroid'):
        #    if(point)
        #else:
            
        return None
    
    def contains(self,other,mode='FAST'):
        """
        Returns true if this blob contains the point, all of a collection of points, or the entire other blo in other
        mode = 'FAST' - does an approximation of contains by using the bouding box
        mode = 'PRECISE' - uses the blob's polygon approximation
        """
        return None
    
    def overlaps(self, other, mode='FAST'):
        """
        Returns true if this blob contains at least one point, part of a collection
        of points, or any part of a blob. 
        mode = 'FAST' - does an approximation of contains by using the bouding box
        mode = 'PRECISE' - uses the blob's polygon approximation        
        """
        return None
    # draw just the blob contours
    def draw(self, color=Color.WHITE, w=-1,alpha=255):
        """
        Draw the blob to
        return None
        """
        if( w < 0 ):
            #blit the blob in
            self.mSourceImgPtr.getDrawingLayer().polygon(self.mContour,color,filled=True,alpha=alpha)
        else:
            lastp = self.mContour[0] #this may work better.... than the other 
            for nextp in self.mContour[1::]:
                self.mSourceImgPtr.getDrawingLayer().line((int(lastp[0]),int(lastp[1])),(int(nextp[0]),int(nextp[1])),color,width=w,alpha=alpha,antialias = False)
                lastp = nextp
            self.mSourceImgPtr.getDrawingLayer().line(self.mContour[0],self.mContour[-1],color,width=w,alpha=alpha, antialias = False)
                   
    #draw the blob to a layer
    def drawToLayer(self, layer, color=Color.WHITE, alpha=-1, w=-1):
        """
        Draw the blob to
        return None
        """
        if( w < 0 ):
            #blit the blob in
            layer.polygon(self.mContour,color,filled=True,alpha=alpha)
        else:
            lastp = self.mContour[0] #this may work better.... than the other 
            for nextp in self.mContour[1::]:
                layer.line(lastp,nextp,color,width=w,alpha=alpha,antialias = False)
                lastp = nextp
            layer.line(self.mContour[0],self.mContour[-1],color,width=w,alpha=alpha, antialias = False)
        return None
    
    def drawHoles(self,color=Color.WHITE, alpha=-1, w=-1):
        if(self.mHoleContour is None):
            return 
        if( w < 0 ):
            #blit the blob in
            for h in self.mHoleContour:
                self.mSourceImgPtr.getDrawingLayer().polygon(h,color,filled=True,alpha=alpha)
        else:
            for h in self.mHoleContour:
                lastp = h[0] #this may work better.... than the other 
                for nextp in h[1::]:
                    self.mSourceImgPtr.getDrawingLayer().line((int(lastp[0]),int(lastp[1])),(int(nextp[0]),int(nextp[1])),color,width=w,alpha=alpha,antialias = False)
                    lastp = nextp
                self.mSourceImgPtr.getDrawingLayer().line(h[0],h[-1],color,width=w,alpha=alpha, antialias = False)
    
    def drawHolesToLayer(self, layer, color=Color.WHITE, alpha=-1, width=-1):
        if(self.mHoleContour is None):
            return 
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
    
    #draw the hull
    def drawHull(self, color=Color.WHITE, w=-1):
        """
        Draw the blob to
        return None
        """
        if( w < 0 ):
            #blit the blob in
            self.mSourceImgPtr.getDrawingLayer().polygon(self.mConvexHull,color,filled=True,alpha=alpha)
        else:
            lastp = self.mConvexHull[0] #this may work better.... than the other 
            for nextp in self.mConvexHull[1::]:
                self.mSourceImgPtr.getDrawingLayer().line(lastp,nextp,color,width=w,alpha=alpha,antialias = False)
                lastp = nextp
            self.mSourceImgPtr.getDrawingLayer().line(self.mConvexHull[0],self.mConvexHull[-1],color,width=w,alpha=alpha, antialias = False)
        return None
    
    #draw the hull to a layer
    def drawHullToLayer(self, layer, color=Color.WHITE, alpha=-1, w=-1 ):
        """
        Draw the blob to
        return None
        """
        if( w < 0 ):
            #blit the blob in
            layer.polygon(self.mConvexHull,color,filled=True,alpha=alpha)
        else:
            lastp = self.mConvexHull[0] #this may work better.... than the other 
            for nextp in self.mConvexHull[1::]:
                layer.line(lastp,nextp,color,width=w,alpha=alpha,antialias = False)
                lastp = nextp
            layer.line(self.mConvexHull[0],self.mConvexHull[-1],color,width=w,alpha=alpha, antialias = False)        
        return None
    
    #draw the actual pixels inside the contour to the layer
    def drawMaskedToLayer(self, layer, offset=(0,0)):
        mx = self.mBoundingBox[0]+offset[0]
        my = self.mBoundingBox[1]+offset[1]
        layer.blit(self.mImg,coordinates=(mx,my))
        return None
    