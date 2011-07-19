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
    mImg =  Image()#the segmented image of the blob
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
    def overlaps(self,blob):
        """
        given two blobs determine if the overlap at all
        """
        return None
    
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
    
    def distanceTo(self,point, mode='Fast'):
        """
        The distance to another blob 
        """
        return None
    
    def contains(self,other,mode='FAST'):
        return None
    