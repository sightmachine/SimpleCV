# SimpleCV Feature library
#
# Tools return basic features in feature sets
# #    x = 0.00
#     y = 0.00
#     _mMaxX = None
#     _mMaxY = None
#     _mMinX = None
#     _mMinY = None
#     _mWidth = None
#     _mHeight = None
#     _mSrcImgW = None
#     mSrcImgH = None


#load system libraries
from SimpleCV.base import *
from SimpleCV.Color import *
import copy


class FeatureSet(list):
    """
    **SUMMARY**

    FeatureSet is a class extended from Python's list which has special functions so that it is useful for handling feature metadata on an image.

    In general, functions dealing with attributes will return numpy arrays, and functions dealing with sorting or filtering will return new FeatureSets.

    **EXAMPLE**

    >>> image = Image("/path/to/image.png")
    >>> lines = image.findLines()  #lines are the feature set
    >>> lines.draw()
    >>> lines.x()
    >>> lines.crop()
    """
    def __getitem__(self,key):
        """
        **SUMMARY**

        Returns a FeatureSet when sliced. Previously used to
        return list. Now it is possible to use FeatureSet member
        functions on sub-lists

        """
        if type(key) is types.SliceType: #Or can use 'try:' for speed
            return FeatureSet(list.__getitem__(self, key))
        else:
            return list.__getitem__(self,key)

    def __getslice__(self, i, j):
        """
        Deprecated since python 2.0, now using __getitem__
        """
        return self.__getitem__(slice(i,j))

    def count(self):
        '''
        This function returns the length / count of the all the items in the FeatureSet
        '''

        return len(self)

    def draw(self, color = Color.GREEN,width=1, autocolor = False, alpha=-1):
        """
        **SUMMARY**

        Call the draw() method on each feature in the FeatureSet.

        **PARAMETERS**
        
        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *width* - The width to draw the feature in pixels. A value of -1 usually indicates a filled region.
        * *autocolor* - If true a color is randomly selected for each feature.
        

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> feats.draw(color=Color.PUCE, width=3)
        >>> img.show()

        """
        for f in self:
            if(autocolor):
                color = Color().getRandom()
            if alpha != -1:
                f.draw(color=color,width=width,alpha=alpha)
            else:
                f.draw(color=color,width=width)

    def show(self, color = Color.GREEN, autocolor = False,width=1):
        """
        **EXAMPLE**

        This function will automatically draw the features on the image and show it.
        It is a basically a shortcut function for development and is the same as:

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *width* - The width to draw the feature in pixels. A value of -1 usually indicates a filled region.
        * *autocolor* - If true a color is randomly selected for each feature.

        **RETURNS**

        Nada. Nothing. Zilch.


        **EXAMPLE**
        >>> img = Image("logo")
        >>> feat = img.findBlobs()
        >>> if feat: feat.draw()
        >>> img.show()

        """
        self.draw(color, width, autocolor)
        self[-1].image.show()


    def reassignImage(self, newImg):
        """
        **SUMMARY**

        Return a new featureset where the features are assigned to a new image.

        **PARAMETERS**

        * *img* - the new image to which to assign the feature.

        .. Warning::
          THIS DOES NOT PERFORM A SIZE CHECK. IF YOUR NEW IMAGE IS NOT THE EXACT SAME SIZE YOU WILL CERTAINLY CAUSE ERRORS.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> img2 = img.invert()
        >>> l = img.findLines()
        >>> l2 = img.reassignImage(img2)
        >>> l2.show()

        """
        retVal = FeatureSet()
        for i in self:
            retVal.append(i.reassign(newImg))
        return retVal

    def x(self):
        """
        **SUMMARY**

        Returns a numpy array of the x (horizontal) coordinate of each feature.

        **RETURNS**

        A numpy array.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> xs = feats.x()
        >>> print xs

        """
        return np.array([f.x for f in self])

    def y(self):
        """
        **SUMMARY**

        Returns a numpy array of the y (vertical) coordinate of each feature.

        **RETURNS**

        A numpy array.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> xs = feats.y()
        >>> print xs

        """
        return np.array([f.y for f in self])

    def coordinates(self):
        """
        **SUMMARY**

        Returns a 2d numpy array of the x,y coordinates of each feature.  This
        is particularly useful if you want to use Scipy's Spatial Distance module

        **RETURNS**

        A numpy array of all the positions in the featureset.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> xs = feats.coordinates()
        >>> print xs


        """
        return np.array([[f.x, f.y] for f in self])

    def center(self):
        return self.coordinates()

    def area(self):
        """
        **SUMMARY**

        Returns a numpy array of the area of each feature in pixels.

        **RETURNS**

        A numpy array of all the positions in the featureset.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> xs = feats.area()
        >>> print xs

        """
        return np.array([f.area() for f in self])

    def sortArea(self):
        """
        **SUMMARY**

        Returns a new FeatureSet, with the largest area features first.

        **RETURNS**

        A featureset sorted based on area.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> feats = feats.sortArea()
        >>> print feats[-1] # biggest blob
        >>> print feats[0] # smallest blob

        """
        return FeatureSet(sorted(self, key = lambda f: f.area()))

    def sortX(self):
        """
        **SUMMARY**

        Returns a new FeatureSet, with the smallest x coordinates features first.

        **RETURNS**

        A featureset sorted based on area.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> feats = feats.sortX()
        >>> print feats[-1] # biggest blob
        >>> print feats[0] # smallest blob

        """
        return FeatureSet(sorted(self, key = lambda f: f.x))

    def sortY(self):
        """
        **SUMMARY**

        Returns a new FeatureSet, with the smallest y coordinates features first.

        **RETURNS**

        A featureset sorted based on area.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> feats = feats.sortY()
        >>> print feats[-1] # biggest blob
        >>> print feats[0] # smallest blob

        """
        return FeatureSet(sorted(self, key = lambda f: f.y)) 

    def distanceFrom(self, point = (-1, -1)):
        """
        **SUMMARY**

        Returns a numpy array of the distance each Feature is from a given coordinate.
        Default is the center of the image.

        **PARAMETERS**

        * *point* - A point on the image from which we will calculate distance.

        **RETURNS**

        A numpy array of distance values.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> d = feats.distanceFrom()
        >>> d[0]  #show the 0th blobs distance to the center.

        **TO DO**

        Make this accept other features to measure from.

        """
        if (point[0] == -1 or point[1] == -1 and len(self)):
            point = self[0].image.size()

        return spsd.cdist(self.coordinates(), [point])[:,0]

    def sortDistance(self, point = (-1, -1)):
        """
        **SUMMARY**

        Returns a sorted FeatureSet with the features closest to a given coordinate first.
        Default is from the center of the image.

        **PARAMETERS**

        * *point* - A point on the image from which we will calculate distance.

        **RETURNS**

        A numpy array of distance values.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> d = feats.sortDistance()
        >>> d[-1].show()  #show the 0th blobs distance to the center.


        """
        return FeatureSet(sorted(self, key = lambda f: f.distanceFrom(point)))

    def distancePairs(self):
        """
        **SUMMARY**

        Returns the square-form of pairwise distances for the featureset.
        The resulting N x N array can be used to quickly look up distances
        between features.

        **RETURNS**

        A NxN np matrix of distance values.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> feats = img.findBlobs()
        >>> d = feats.distancePairs()
        >>> print d

        """
        return spsd.squareform(spsd.pdist(self.coordinates()))

    def angle(self):
        """
        **SUMMARY**

        Return a numpy array of the angles (theta) of each feature.
        Note that theta is given in degrees, with 0 being horizontal.

        **RETURNS**

        An array of angle values corresponding to the features.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> l = img.findLines()
        >>> angs = l.angle()
        >>> print angs


        """
        return np.array([f.angle() for f in self])

    def sortAngle(self, theta = 0):
        """
        Return a sorted FeatureSet with the features closest to a given angle first.
        Note that theta is given in radians, with 0 being horizontal.

        **RETURNS**

        An array of angle values corresponding to the features.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> l = img.findLines()
        >>> l = l.sortAngle()
        >>> print angs

        """
        return FeatureSet(sorted(self, key = lambda f: abs(f.angle() - theta)))

    def length(self):
        """
        **SUMMARY**

        Return a numpy array of the length (longest dimension) of each feature.

        **RETURNS**

        A numpy array of the length, in pixels, of eatch feature object.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> l = img.findLines()
        >>> lengt = l.length()
        >>> lengt[0] # length of the 0th element.

        """

        return np.array([f.length() for f in self])

    def sortLength(self):
        """
        **SUMMARY**

        Return a sorted FeatureSet with the longest features first.

        **RETURNS**

        A sorted FeatureSet.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> l = img.findLines().sortLength()
        >>> lengt[-1] # length of the 0th element.

        """
        return FeatureSet(sorted(self, key = lambda f: f.length()))

    def meanColor(self):
        """
        **SUMMARY**

        Return a numpy array of the average color of the area covered by each Feature.

        **RETURNS**

        Returns an array of RGB triplets the correspond to the mean color of the feature.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> kp = img.findKeypoints()
        >>> c = kp.meanColor()


        """
        return np.array([f.meanColor() for f in self])

    def colorDistance(self, color = (0, 0, 0)):
        """
        **SUMMARY**

        Return a numpy array of the distance each features average color is from
        a given color tuple (default black, so colorDistance() returns intensity)

        **PARAMETERS**

        * *color* - The color to calculate the distance from.

        **RETURNS**

        The distance of the average color for the feature from given color as a numpy array.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> circs = img.findCircle()
        >>> d = circs.colorDistance(color=Color.BLUE)
        >>> print d

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
        **SUMMARY**

        Return a FeatureSet which is filtered on a numpy boolean array.  This
        will let you use the attribute functions to easily screen Features out
        of return FeatureSets.

        **PARAMETERS**

        * *filterarray* - A numpy array, matching  the size of the feature set,
          made of Boolean values, we return the true values and reject the False value.

        **RETURNS**

        The revised feature set.

        **EXAMPLE**

        Return all lines < 200px

        >>> my_lines.filter(my_lines.length() < 200) # returns all lines < 200px
        >>> my_blobs.filter(my_blobs.area() > 0.9 * my_blobs.length**2) # returns blobs that are nearly square
        >>> my_lines.filter(abs(my_lines.angle()) < numpy.pi / 4) #any lines within 45 degrees of horizontal
        >>> my_corners.filter(my_corners.x() - my_corners.y() > 0) #only return corners in the upper diagonal of the image

        """
        return FeatureSet(list(np.array(self)[np.array(filterarray)]))

    def width(self):
        """
        **SUMMARY**

        Returns a nparray which is the width of all the objects in the FeatureSet.

        **RETURNS**

        A numpy array of width values.


        **EXAMPLE**

        >>> img = Image("NotLenna")
        >>> l = img.findLines()
        >>> l.width()

        """
        return np.array([f.width() for f in self])

    def height(self):
        """
        Returns a nparray which is the height of all the objects in the FeatureSet

        **RETURNS**

        A numpy array of width values.


        **EXAMPLE**

        >>> img = Image("NotLenna")
        >>> l = img.findLines()
        >>> l.height()

        """
        return np.array([f.height() for f in self])

    def crop(self):
        """
        **SUMMARY**

        Returns a nparray with the cropped features as SimpleCV image.

        **RETURNS**

        A SimpleCV image cropped to each image.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs(128)
        >>> for b in blobs:
        >>>   newImg = b.crop()
        >>>   newImg.show()
        >>>   time.sleep(1)

        """
        return np.array([f.crop() for f in self])

    def inside(self,region):
        """
        **SUMMARY**

        Return only the features inside the region. where region can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *region*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a featureset of features that are inside the region.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[-1]
        >>> lines = img.findLines()
        >>> inside = lines.inside(b)

        **NOTE**

        This currently performs a bounding box test, not a full polygon test for speed.


        """
        fs = FeatureSet()
        for f in self:
            if(f.isContainedWithin(region)):
                fs.append(f)
        return fs


    def outside(self,region):
        """
        **SUMMARY**

        Return only the features outside the region. where region can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *region*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a featureset of features that are outside the region.


        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[-1]
        >>> lines = img.findLines()
        >>> outside = lines.outside(b)

        **NOTE**

        This currently performs a bounding box test, not a full polygon test for speed.

        """
        fs = FeatureSet()
        for f in self:
            if(f.isNotContainedWithin(region)):
                fs.append(f)
        return fs

    def overlaps(self,region):
        """
        **SUMMARY**

        Return only the features that overlap or the region. Where region can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *region*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a featureset of features that overlap the region.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[-1]
        >>> lines = img.findLines()
        >>> outside = lines.overlaps(b)

        **NOTE**

        This currently performs a bounding box test, not a full polygon test for speed.

        """
        fs = FeatureSet()
        for f in self:
            if( f.overlaps(region) ):
                fs.append(f)
        return fs

    def above(self,region):
        """
        **SUMMARY**

        Return only the features that are above a  region. Where region can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *region*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a featureset of features that are above the region.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[-1]
        >>> lines = img.findLines()
        >>> outside = lines.above(b)

        **NOTE**

        This currently performs a bounding box test, not a full polygon test for speed.

        """
        fs = FeatureSet()
        for f in self:
            if(f.above(region)):
                fs.append(f)
        return fs

    def below(self,region):
        """
        **SUMMARY**

        Return only the features below the region. where region can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *region*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a featureset of features that are below the region.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[-1]
        >>> lines = img.findLines()
        >>> inside = lines.below(b)

        **NOTE**

        This currently performs a bounding box test, not a full polygon test for speed.

        """
        fs = FeatureSet()
        for f in self:
            if(f.below(region)):
                fs.append(f)
        return fs

    def left(self,region):
        """
        **SUMMARY**

        Return only the features left of the region. where region can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *region*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a featureset of features that are left of the region.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[-1]
        >>> lines = img.findLines()
        >>> left = lines.left(b)

        **NOTE**

        This currently performs a bounding box test, not a full polygon test for speed.

        """
        fs = FeatureSet()
        for f in self:
            if(f.left(region)):
                fs.append(f)
        return fs

    def right(self,region):
        """
        **SUMMARY**

        Return only the features right of the region. where region can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *region*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a featureset of features that are right of the region.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[-1]
        >>> lines = img.findLines()
        >>> right = lines.right(b)

        **NOTE**

        This currently performs a bounding box test, not a full polygon test for speed.

        """
        fs = FeatureSet()
        for f in self:
            if(f.right(region)):
                fs.append(f)
        return fs

    def onImageEdge(self, tolerance=1):
        """
        **SUMMARY**

        The method returns a feature set of features that are on or "near" the edge of
        the image. This is really helpful for removing features that are edge effects.

        **PARAMETERS**

        * *tolerance* - the distance in pixels from the edge at which a feature
          qualifies as being "on" the edge of the image.

        **RETURNS**

        Returns a featureset of features that are on the edge of the image.

        **EXAMPLE**

        >>> img = Image("./sampleimages/EdgeTest1.png")
        >>> blobs = img.findBlobs()
        >>> es = blobs.onImageEdge()
        >>> es.draw(color=Color.RED)
        >>> img.show()

        """
        fs = FeatureSet()
        for f in self:
            if(f.onImageEdge(tolerance)):
                fs.append(f)
        return fs

    def notOnImageEdge(self, tolerance=1):
        """
        **SUMMARY**

        The method returns a feature set of features that are not on or "near" the edge of
        the image. This is really helpful for removing features that are edge effects.

        **PARAMETERS**

        * *tolerance* - the distance in pixels from the edge at which a feature
          qualifies as being "on" the edge of the image.

        **RETURNS**

        Returns a featureset of features that are not on the edge of the image.

        **EXAMPLE**

        >>> img = Image("./sampleimages/EdgeTest1.png")
        >>> blobs = img.findBlobs()
        >>> es = blobs.notOnImageEdge()
        >>> es.draw(color=Color.RED)
        >>> img.show()

        """
        fs = FeatureSet()
        for f in self:
            if(f.notOnImageEdge(tolerance)):
                fs.append(f)
        return fs


    def topLeftCorners(self):
        """
        **SUMMARY**

        This method returns the top left corner of each feature's bounding box.

        **RETURNS**

        A numpy array of x,y position values.

        **EXAMPLE**

        >>> img = Image("./sampleimages/EdgeTest1.png")
        >>> blobs = img.findBlobs()
        >>> tl = img.topLeftCorners()
        >>> print tl[0]
        """
        return np.array([f.topLeftCorner() for f in self])



    def bottomLeftCorners(self):
        """
        **SUMMARY**

        This method returns the bottom left corner of each feature's bounding box.

        **RETURNS**

        A numpy array of x,y position values.

        **EXAMPLE**

        >>> img = Image("./sampleimages/EdgeTest1.png")
        >>> blobs = img.findBlobs()
        >>> bl = img.bottomLeftCorners()
        >>> print bl[0]

        """
        return np.array([f.bottomLeftCorner() for f in self])

    def topLeftCorners(self):
        """
        **SUMMARY**

        This method returns the top left corner of each feature's bounding box.

        **RETURNS**

        A numpy array of x,y position values.

        **EXAMPLE**

        >>> img = Image("./sampleimages/EdgeTest1.png")
        >>> blobs = img.findBlobs()
        >>> tl = img.bottomLeftCorners()
        >>> print tl[0]

        """
        return np.array([f.topLeftCorner() for f in self])


    def topRightCorners(self):
        """
        **SUMMARY**

        This method returns the top right corner of each feature's bounding box.

        **RETURNS**

        A numpy array of x,y position values.

        **EXAMPLE**

        >>> img = Image("./sampleimages/EdgeTest1.png")
        >>> blobs = img.findBlobs()
        >>> tr = img.topRightCorners()
        >>> print tr[0]

        """
        return np.array([f.topRightCorner() for f in self])



    def bottomRightCorners(self):
        """
        **SUMMARY**

        This method returns the bottom right corner of each feature's bounding box.

        **RETURNS**

        A numpy array of x,y position values.

        **EXAMPLE**

        >>> img = Image("./sampleimages/EdgeTest1.png")
        >>> blobs = img.findBlobs()
        >>> br = img.bottomRightCorners()
        >>> print br[0]

        """
        return np.array([f.bottomRightCorner() for f in self])

    def aspectRatios(self):
        """
        **SUMMARY**

        Return the aspect ratio of all the features in the feature set, For our purposes
        aspect ration is max(width,height)/min(width,height).

        **RETURNS**

        A numpy array of the aspect ratio of the features in the featureset.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs.aspectRatio()

        """
        return np.array([f.aspectRatio() for f in self])

    def cluster(self,method="kmeans",properties=None,k=3):
        """
        
        **SUMMARY**

        This function clusters the blobs in the featureSet based on the properties. Properties can be "color", "shape" or "position" of blobs.
        Clustering is done using K-Means or Hierarchical clustering(Ward) algorithm.

        **PARAMETERS**
        
        * *properties* - It should be a list with any combination of "color", "shape", "position". properties = ["color","position"]. properties = ["position","shape"]. properties = ["shape"]
        * *method* - if method is "kmeans", it will cluster using K-Means algorithm, if the method is "hierarchical", no need to spicify the number of clusters
        * *k* - The number of clusters(kmeans).
        

        **RETURNS**

        A list of featureset, each being a cluster itself.

        **EXAMPLE**

          >>> img = Image("lenna")
          >>> blobs = img.findBlobs()
          >>> clusters = blobs.cluster(method="kmeans",properties=["color"],k=5)
          >>> for i in clusters:
          >>>     i.draw(color=Color.getRandom(),width=5)
          >>> img.show()
        
        """
        try :
            from sklearn.cluster import KMeans, Ward
            from sklearn import __version__
        except :
            logger.warning("install scikits-learning package")
            return
        X = [] #List of feature vector of each blob
        if not properties:
            properties = ['color','shape','position']
        if k > len(self):
            logger.warning("Number of clusters cannot be greater then the number of blobs in the featureset")
            return
        for i in self:
            featureVector = []
            if 'color' in properties:
                featureVector.extend(i.mAvgColor)
            if 'shape' in properties:
                featureVector.extend(i.mHu)
            if 'position' in properties:
                featureVector.extend(i.extents())
            if not featureVector :
                logger.warning("properties parameter is not specified properly")
                return
            X.append(featureVector)

        if method == "kmeans":
            
            # Ignore minor version numbers.
            sklearn_version = re.search(r'\d+\.\d+', __version__).group()
            
            if (float(sklearn_version) > 0.11):
                k_means = KMeans(init='random', n_clusters=k, n_init=10).fit(X)
            else:
                k_means = KMeans(init='random', k=k, n_init=10).fit(X)
            KClusters = [ FeatureSet([]) for i in range(k)]
            for i in range(len(self)):
                KClusters[k_means.labels_[i]].append(self[i])
            return KClusters

        if method == "hierarchical":
            ward = Ward(n_clusters=int(sqrt(len(self)))).fit(X) #n_clusters = sqrt(n)
            WClusters = [ FeatureSet([]) for i in range(int(sqrt(len(self))))]
            for i in range(len(self)):
                WClusters[ward.labels_[i]].append(self[i])
            return WClusters

    @property
    def image(self):
        if not len(self):
            return None
        return self[0].image

    @image.setter
    def image(self, i):
        for f in self:
            f.image = i

### ----------------------------------------------------------------------------
### ----------------------------------------------------------------------------
### ----------------------------FEATURE CLASS-----------------------------------
### ----------------------------------------------------------------------------
### ----------------------------------------------------------------------------
class Feature(object):
    """
    **SUMMARY**

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
    _mMaxX = None
    _mMaxY = None
    _mMinX = None
    _mMinY = None
    _mWidth = None
    _mHeight = None
    _mSrcImgW = None
    _mSrcImgH = None

    # This is 2.0 refactoring
    mBoundingBox = None # THIS SHALT BE TOP LEFT (X,Y) THEN W H i.e. [X,Y,W,H]
    mExtents = None # THIS SHALT BE [MAXX,MINX,MAXY,MINY]
    points = None  # THIS SHALT BE (x,y) tuples in the ORDER [(TopLeft),(TopRight),(BottomLeft),(BottomRight)]

    image = "" #parent image
    #points = []
    #boundingBox = []

    def __init__(self, i, at_x, at_y, points):
        #THE COVENANT IS THAT YOU PROVIDE THE POINTS IN THE SPECIFIED FORMAT AND ALL OTHER VALUES SHALT FLOW
        self.x = at_x
        self.y = at_y
        self.image = i
        self.points = points
        self._updateExtents(new_feature=True)

    def reassign(self, img):
        """
        **SUMMARY**

        Reassign the image of this feature and return an updated copy of the feature.

        **PARAMETERS**

        * *img* - the new image to which to assign the feature.

        .. Warning::
          THIS DOES NOT PERFORM A SIZE CHECK. IF YOUR NEW IMAGE IS NOT THE EXACT SAME SIZE YOU WILL CERTAINLY CAUSE ERRORS.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> img2 = img.invert()
        >>> l = img.findLines()
        >>> l2 = img.reassignImage(img2)
        >>> l2.show()
        """
        retVal = copy.deepcopy(self)
        if( self.image.width != img.width or
            self.image.height != img.height ):
            warnings.warn("DON'T REASSIGN IMAGES OF DIFFERENT SIZES")
        retVal.image = img

        return retVal

    def corners(self):
        self._updateExtents()
        return self.points

    def coordinates(self):
        """
        **SUMMARY**

        Returns the x,y position of the feature. This is usually the center coordinate.

        **RETURNS**

        Returns an (x,y) tuple of the position of the feature.

        **EXAMPLE**

        >>> img = Image("aerospace.png")
        >>> blobs = img.findBlobs()
        >>> for b in blobs:
        >>>    print b.coordinates()

        """
        return np.array([self.x, self.y])


    def draw(self, color = Color.GREEN):
        """
        **SUMMARY**

        This method will draw the feature on the source image.

        **PARAMETERS**

        * *color* - The color as an RGB tuple to render the image.

        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> img = Image("RedDog2.jpg")
        >>> blobs = img.findBlobs()
        >>> blobs[-1].draw()
        >>> img.show()

        """
        self.image[self.x, self.y] = color

    def show(self, color = Color.GREEN):
        """
        **SUMMARY**

        This function will automatically draw the features on the image and show it.

        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> img = Image("logo")
        >>> feat = img.findBlobs()
        >>> feat[-1].show() #window pops up.

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
        >>> blobs = img.findBlobs(128)
        >>> blobs[-1].distanceFrom(blobs[-2].coordinates())


        """
        if (point[0] == -1 or point[1] == -1):
            point = np.array(self.image.size()) / 2
        return spsd.euclidean(point, [self.x, self.y])

    def meanColor(self):
        """
        **SUMMARY**

        Return the average color within the feature as a tuple.

        **RETURNS**

        An RGB color tuple.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> for b in blobs:
        >>>    if (b.meanColor() == color.WHITE):
        >>>       print "Found a white thing"

        """
        return self.image[self.x, self.y]

    def colorDistance(self, color = (0, 0, 0)):
        """
        **SUMMARY**

        Return the euclidean color distance of the color tuple at x,y from a given color (default black).

        **PARAMETERS**

        * *color* - An RGB triplet to calculate from which to calculate the color distance.

        **RETURNS**

        A floating point color distance value.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> for b in blobs:
        >>>    print b.colorDistance(color.WHITE):

        """
        return spsd.euclidean(np.array(color), np.array(self.meanColor()))

    def angle(self):
        """
        **SUMMARY**

        Return the angle (theta) in degrees of the feature. The default is 0 (horizontal).

        .. Warning::
          This is not a valid operation for all features.


        **RETURNS**

        An angle value in degrees.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> for b in blobs:
        >>>    if b.angle() == 0:
        >>>       print "I AM HORIZONTAL."

        **TODO**

        Double check that values are being returned consistently.
        """
        return 0

    def length(self):
        """
        **SUMMARY**

        This method returns the longest dimension of the feature (i.e max(width,height)).

        **RETURNS**

        A floating point length value.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> for b in blobs:
        >>>    if b.length() > 200:
        >>>       print "OH MY! - WHAT A BIG FEATURE YOU HAVE!"
        >>>       print "---I bet you say that to all the features."

        **TODO**

        Should this be sqrt(x*x+y*y)?
        """
        return float(np.max([self.width(),self.height()]))

    def distanceToNearestEdge(self):
        """
        **SUMMARY**

        This method returns the distance, in pixels, from the nearest image edge.

        **RETURNS**

        The integer distance to the nearest edge.

        **EXAMPLE**

        >>> img = Image("../sampleimages/EdgeTest1.png")
        >>> b = img.findBlobs()
        >>> b[0].distanceToNearestEdge()

        """
        w = self.image.width
        h = self.image.height
        return np.min([self._mMinX,self._mMinY, w-self._mMaxX,h-self._mMaxY])

    def onImageEdge(self,tolerance=1):
        """
        **SUMMARY**

        This method returns True if the feature is less than `tolerance`
        pixels away from the nearest edge.

        **PARAMETERS**

        * *tolerance* - the distance in pixels at which a feature qualifies
          as being on the image edge.

        **RETURNS**

        True if the feature is on the edge, False otherwise.

        **EXAMPLE**

        >>> img = Image("../sampleimages/EdgeTest1.png")
        >>> b = img.findBlobs()
        >>> if(b[0].onImageEdge()):
        >>>     print "HELP! I AM ABOUT TO FALL OFF THE IMAGE"

        """
        # this has to be one to deal with blob library weirdness that goes deep down to opencv
        return ( self.distanceToNearestEdge() <= tolerance )

    def notOnImageEdge(self,tolerance=1):
        """
        **SUMMARY**

        This method returns True if the feature is greate than `tolerance`
        pixels away from the nearest edge.

        **PARAMETERS**

        * *tolerance* - the distance in pixels at which a feature qualifies
          as not being on the image edge.

        **RETURNS**

        True if the feature is not on the edge of the image, False otherwise.

        **EXAMPLE**

        >>> img = Image("../sampleimages/EdgeTest1.png")
        >>> b = img.findBlobs()
        >>> if(b[0].notOnImageEdge()):
        >>>     print "I am safe and sound."

        """

        # this has to be one to deal with blob library weirdness that goes deep down to opencv
        return ( self.distanceToNearestEdge() > tolerance )


    def aspectRatio(self):
        """
        **SUMMARY**

        Return the aspect ratio of the feature, which for our purposes
        is max(width,height)/min(width,height).

        **RETURNS**

        A single floating point value of the aspect ration.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> b[0].aspectRatio()

        """
        self._updateExtents()
        return self.mAspectRatio

    def area(self):
        """
        **SUMMARY**

        Returns the area (number of pixels)  covered by the feature.

        **RETURNS**

        An integer area of the feature.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> for b in blobs:
        >>>    if b.area() > 200:
        >>>       print b.area()

        """
        return self.width() * self.height()

    def width(self):
        """
        **SUMMARY**

        Returns the height of the feature.

        **RETURNS**

        An integer value for the feature's width.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> for b in blobs:
        >>>    if b.width() > b.height():
        >>>       print "wider than tall"
        >>>       b.draw()
        >>> img.show()

        """
        self._updateExtents()
        return self._mWidth


    def height(self):
        """
        **SUMMARY**

        Returns the height of the feature.

        **RETURNS**

        An integer value of the feature's height.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> for b in blobs:
        >>>    if b.width() > b.height():
        >>>       print "wider than tall"
        >>>       b.draw()
        >>> img.show()
        """
        self._updateExtents()
        return self._mHeight

    def crop(self):
        """
        **SUMMARY**

        This function crops the source image to the location of the feature and returns
        a new SimpleCV image.

        **RETURNS**

        A SimpleCV image that is cropped to the feature position and size.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> big = blobs[-1].crop()
        >>> big.show()

        """

        return self.image.crop(self.x, self.y, self.width(), self.height(), centered = True)

    def __repr__(self):
        return "%s.%s at (%d,%d)" % (self.__class__.__module__, self.__class__.__name__, self.x, self.y)


    def _updateExtents(self, new_feature=False):
#    mBoundingBox = None # THIS SHALT BE TOP LEFT (X,Y) THEN W H i.e. [X,Y,W,H]
#    mExtents = None # THIS SHALT BE [MAXX,MINX,MAXY,MINY]
#    points = None  # THIS SHALT BE (x,y) tuples in the ORDER [(TopLeft),(TopRight),(BottomLeft),(BottomRight)]

        max_x = self._mMaxX
        min_x = self._mMinX
        max_y = self._mMaxY
        min_y = self._mMinY
        width = self._mWidth
        height = self._mHeight
        extents = self.mExtents
        bounding_box = self.mBoundingBox

        #if new_feature or None in [self._mMaxX, self._mMinX, self._mMaxY, self._mMinY,
        #            self._mWidth, self._mHeight, self.mExtents, self.mBoundingBox]:

        if new_feature or None in [max_x, min_x, max_y, min_y, width, height, extents, bounding_box]:

            max_x = max_y = float("-infinity")
            min_x = min_y = float("infinity")

            for p in self.points:
                if (p[0] > max_x):
                    max_x = p[0]
                if (p[0] < min_x):
                    min_x = p[0]
                if (p[1] > max_y):
                    max_y = p[1]
                if (p[1] < min_y):
                    min_y = p[1]

            width = max_x - min_x
            height = max_y - min_y

            if (width <= 0):
                width = 1

            if (height <= 0):
                height = 1

            self.mBoundingBox = [min_x, min_y, width, height]
            self.mExtents = [max_x, min_x, max_y, min_y]

            if width > height:
                self.mAspectRatio = float(width/height)
            else:
                self.mAspectRatio = float(height/width)

            self._mMaxX = max_x
            self._mMinX = min_x
            self._mMaxY = max_y
            self._mMinY = min_y
            self._mWidth = width
            self._mHeight = height

    def boundingBox(self):
        """
        **SUMMARY**

        This function returns a rectangle which bounds the blob.

        **RETURNS**

        A list of [x, y, w, h] where (x, y) are the top left point of the rectangle
        and w, h are its width and height respectively.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs[-1].boundingBox()

        """
        self._updateExtents()
        return self.mBoundingBox

    def extents(self):
        """
        **SUMMARY**

        This function returns the maximum and minimum x and y values for the feature and
        returns them as a tuple.

        **RETURNS**

        A tuple of the extents of the feature. The order is (MaxX,MaxY,MinX,MinY).

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs[-1].extents()

        """
        self._updateExtents()
        return self.mExtents

    def minY(self):
        """
        **SUMMARY**

        This method return the minimum y value of the bounding box of the
        the feature.

        **RETURNS**

        An integer value of the minimum y value of the feature.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs[-1].minY()

        """
        self._updateExtents()
        return self._mMinY

    def maxY(self):
        """
        **SUMMARY**

        This method return the maximum y value of the bounding box of the
        the feature.

        **RETURNS**

        An integer value of the maximum y value of the feature.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs[-1].maxY()

        """
        self._updateExtents()
        return self._mMaxY


    def minX(self):
        """
        **SUMMARY**

        This method return the minimum x value of the bounding box of the
        the feature.

        **RETURNS**

        An integer value of the minimum x value of the feature.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs[-1].minX()

        """
        self._updateExtents()
        return self._mMinX

    def maxX(self):
        """
        **SUMMARY**

        This method return the minimum x value of the bounding box of the
        the feature.

        **RETURNS**

        An integer value of the maxium x value of the feature.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs[-1].maxX()

        """
        self._updateExtents()
        return self._mMaxX

    def topLeftCorner(self):
        """
        **SUMMARY**

        This method returns the top left corner of the bounding box of
        the blob as an (x,y) tuple.

        **RESULT**

        Returns a tupple of the top left corner.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs[-1].topLeftCorner()

        """
        self._updateExtents()
        return (self._mMinX,self._mMinY)

    def bottomRightCorner(self):
        """
        **SUMMARY**

        This method returns the bottom right corner of the bounding box of
        the blob as an (x,y) tuple.

        **RESULT**

        Returns a tupple of the bottom right corner.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs[-1].bottomRightCorner()

        """
        self._updateExtents()
        return (self._mMaxX,self._mMaxY)

    def bottomLeftCorner(self):
        """
        **SUMMARY**

        This method returns the bottom left corner of the bounding box of
        the blob as an (x,y) tuple.

        **RESULT**

        Returns a tupple of the bottom left corner.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs[-1].bottomLeftCorner()

        """
        self._updateExtents()
        return (self._mMinX,self._mMaxY)

    def topRightCorner(self):
        """
        **SUMMARY**

        This method returns the top right corner of the bounding box of
        the blob as an (x,y) tuple.

        **RESULT**

        Returns a tupple of the top right  corner.

        **EXAMPLE**

        >>> img = Image("OWS.jpg")
        >>> blobs = img.findBlobs(128)
        >>> print blobs[-1].topRightCorner()

        """
        self._updateExtents()
        return (self._mMaxX,self._mMinY)


    def above(self,object):
        """
        **SUMMARY**

        Return true if the feature is above the object, where object can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *object*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a Boolean, True if the feature is above the object, False otherwise.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[0]
        >>> if( blobs[-1].above(b) ):
        >>>    print "above the biggest blob"

        """
        if( isinstance(object,Feature) ):
            return( self.maxY() < object.minY() )
        elif( isinstance(object,tuple) or isinstance(object,np.ndarray) ):
            return( self.maxY() < object[1]  )
        elif( isinstance(object,float) or isinstance(object,int) ):
            return( self.maxY() < object )
        else:
            logger.warning("SimpleCV did not recognize the input type to feature.above(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None

    def below(self,object):
        """
        **SUMMARY**

        Return true if the feature is below the object, where object can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *object*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a Boolean, True if the feature is below the object, False otherwise.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[0]
        >>> if( blobs[-1].below(b) ):
        >>>    print "above the biggest blob"

        """
        if( isinstance(object,Feature) ):
            return( self.minY() > object.maxY() )
        elif( isinstance(object,tuple) or isinstance(object,np.ndarray) ):
            return( self.minY() > object[1]  )
        elif( isinstance(object,float) or isinstance(object,int) ):
            return( self.minY() > object )
        else:
            logger.warning("SimpleCV did not recognize the input type to feature.below(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None


    def right(self,object):
        """
        **SUMMARY**

        Return true if the feature is to the right object, where object can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *object*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a Boolean, True if the feature is to the right object, False otherwise.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[0]
        >>> if( blobs[-1].right(b) ):
        >>>    print "right of the the blob"

        """
        if( isinstance(object,Feature) ):
            return( self.minX() > object.maxX() )
        elif( isinstance(object,tuple) or isinstance(object,np.ndarray) ):
            return( self.minX() > object[0]  )
        elif( isinstance(object,float) or isinstance(object,int) ):
            return( self.minX() > object )
        else:
            logger.warning("SimpleCV did not recognize the input type to feature.right(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None

    def left(self,object):
        """
        **SUMMARY**

        Return true if the feature is to the left of  the object, where object can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *object*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a Boolean, True if the feature is to the left of  the object, False otherwise.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[0]
        >>> if( blobs[-1].left(b) ):
        >>>    print "left of  the biggest blob"


        """
        if( isinstance(object,Feature) ):
            return( self.maxX() < object.minX() )
        elif( isinstance(object,tuple) or isinstance(object,np.ndarray) ):
            return( self.maxX() < object[0]  )
        elif( isinstance(object,float) or isinstance(object,int) ):
            return( self.maxX() < object )
        else:
            logger.warning("SimpleCV did not recognize the input type to feature.left(). This method only takes another feature, an (x,y) tuple, or a ndarray type.")
            return None

    def contains(self,other):
        """
        **SUMMARY**

        Return true if the feature contains  the object, where object can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *object*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a Boolean, True if the feature contains the object, False otherwise.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[0]
        >>> if( blobs[-1].contains(b) ):
        >>>    print "this blob is contained in the biggest blob"

        **NOTE**

        This currently performs a bounding box test, not a full polygon test for speed.

        """
        retVal = False

        bounds = self.points
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
            logger.warning("SimpleCV did not recognize the input type to features.contains. This method only takes another blob, an (x,y) tuple, or a ndarray type.")
            return False

        return retVal

    def overlaps(self, other):
        """
        **SUMMARY**

        Return true if the feature overlaps the object, where object can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *object*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a Boolean, True if the feature overlaps  object, False otherwise.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[0]
        >>> if( blobs[-1].overlaps(b) ):
        >>>    print "This blob overlaps the biggest blob"

        Returns true if this blob contains at least one point, part of a collection
        of points, or any part of a blob.

        **NOTE**

        This currently performs a bounding box test, not a full polygon test for speed.

       """
        retVal = False
        bounds = self.points

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
            logger.warning("SimpleCV did not recognize the input type to features.overlaps. This method only takes another blob, an (x,y) tuple, or a ndarray type.")
            return False

        return retVal

    def doesNotContain(self, other):
        """
        **SUMMARY**

        Return true if the feature does not contain  the other object, where other can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *other*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a Boolean, True if the feature does not contain the object, False otherwise.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[0]
        >>> if( blobs[-1].doesNotContain(b) ):
        >>>    print "above the biggest blob"

        Returns true if all of features points are inside this point.
        """
        return not self.contains(other)

    def doesNotOverlap( self, other):
        """
        **SUMMARY**

        Return true if the feature does not overlap the object other, where other can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *other*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a Boolean, True if the feature does not Overlap  the object, False otherwise.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[0]
        >>> if( blobs[-1].doesNotOverlap(b) ):
        >>>    print "does not over overlap biggest blob"


        """
        return not self.overlaps( other)


    def isContainedWithin(self,other):
        """
        **SUMMARY**

        Return true if the feature is contained withing  the object other, where other can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *other*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a Boolean, True if the feature is above the object, False otherwise.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[0]
        >>> if( blobs[-1].isContainedWithin(b) ):
        >>>    print "inside the blob"

        """
        retVal = True
        bounds = self.points

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
        elif(isinstance(other,list) and len(other) > 2 ): # an arbitrary polygon
            #everything else ....
            retVal = True
            for p in bounds:
                test = self._pointInsidePolygon(p,other)
                if(not test):
                    retVal = False
                    break

        else:
            logger.warning("SimpleCV did not recognize the input type to features.contains. This method only takes another blob, an (x,y) tuple, or a ndarray type.")
            retVal = False
        return retVal


    def isNotContainedWithin(self,shape):
        """
        **SUMMARY**

        Return true if the feature is not contained within the shape, where shape can be a bounding box,
        bounding circle, a list of tuples in a closed polygon, or any other featutres.

        **PARAMETERS**

        * *shape*

          * A bounding box - of the form (x,y,w,h) where x,y is the upper left corner
          * A bounding circle of the form (x,y,r)
          * A list of x,y tuples defining a closed polygon e.g. ((x,y),(x,y),....)
          * Any two dimensional feature (e.g. blobs, circle ...)

        **RETURNS**

        Returns a Boolean, True if the feature is not contained within the shape, False otherwise.

        **EXAMPLE**

        >>> img = Image("Lenna")
        >>> blobs = img.findBlobs()
        >>> b = blobs[0]
        >>> if( blobs[-1].isNotContainedWithin(b) ):
        >>>    print "Not inside the biggest blob"

        """
        return not self.isContainedWithin(shape)

    def _pointInsidePolygon(self,point,polygon):
        """
        returns true if tuple point (x,y) is inside polygon of the form ((a,b),(c,d),...,(a,b)) the polygon should be closed

        """
        # try:
        #     import cv2
        # except:
        #     logger.warning("Unable to import cv2")
        #     return False

        if( len(polygon) < 3 ):
            logger.warning("feature._pointInsidePolygon - this is not a valid polygon")
            return False

        if( not isinstance(polygon,list)):
            logger.warning("feature._pointInsidePolygon - this is not a valid polygon")
            return False

        #if( not isinstance(point,tuple) ):
            #if( len(point) == 2 ):
            #    point = tuple(point)
            #else:
            #    logger.warning("feature._pointInsidePolygon - this is not a valid point")
            #    return False
        #if( cv2.__version__ == '$Rev:4557'):
        counter = 0
        retVal = True
        p1 = None
        #print "point: " + str(point)
        poly = copy.deepcopy(polygon)
        poly.append(polygon[0])
        #for p2 in poly:
        N = len(poly)
        p1 = poly[0]
        for i in range(1,N+1):
            p2 = poly[i%N]
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
        return retVal
        #else:
        #    result = cv2.pointPolygonTest(np.array(polygon,dtype='float32'),point,0)
        #    return result > 0 

    def boundingCircle(self):
        """
        **SUMMARY**

        This function calculates the minimum bounding circle of the blob in the image
        as an (x,y,r) tuple

        **RETURNS**

        An (x,y,r) tuple where (x,y) is the center of the circle and r is the radius

        **EXAMPLE**

        >>> img = Image("RatMask.png")
        >>> blobs = img.findBlobs()
        >>> print blobs[-1].boundingCircle()

        """

        try:
            import cv2
        except:
            logger.warning("Unable to import cv2")
            return None

        # contour of the blob in image
        contour = self.contour()

        points = []
        # list of contour points converted to suitable format to pass into cv2.minEnclosingCircle()
        for pair in contour:
            points.append([[pair[0], pair[1]]])

        points = np.array(points)

        (cen, rad) = cv2.minEnclosingCircle(points);

        return (cen[0], cen[1], rad)


#---------------------------------------------
