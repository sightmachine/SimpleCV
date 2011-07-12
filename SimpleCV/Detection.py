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
from SimpleCV.Features import Feature, FeatureSet

class Corner(Feature):
  """
  The Corner feature is a point returned by the FindCorners function
  """
  def __init__(self, i, at_x, at_y):
    super(Corner, self).__init__(i, at_x, at_y)
    #can we look at the eigenbuffer and find direction?

  def draw(self, color = (255, 0, 0)):
    """
    Draw a small circle around the corner.  Color tuple is single parameter, default Red 
    """
    self.image.drawCircle((self.x, self.y), 4, color)

class Blob(Feature):
  """
The Blob Feature is a wrapper for the cvblob-python library.  

The findBlobs() function returns contiguous regions of light-colored area, given an intensity threshold.  The Blob class helps you map the position, volume, and shape of these areas.  The coordinates of the Blob are its centroid, and its area is defined by its total pixel count.

Blob implements all of the Feature properties, and its core data structure, cvblob has the following properties (from cvblob.h)::

    CvLabel label; ///< Label assigned to the blob.
    
    union
    {
      unsigned int area; ///< Area (moment 00).
      unsigned int m00; ///< Moment 00 (area).
    };
    
    unsigned int minx; ///< X min.
    unsigned int maxx; ///< X max.
    unsigned int miny; ///< Y min.
    unsigned int maxy; ///< y max.
    
    CvPoint2D64f centroid; ///< Centroid.
    
    double m10; ///< Moment 10.
    double m01; ///< Moment 01.
    double m11; ///< Moment 11.
    double m20; ///< Moment 20.
    double m02; ///< Moment 02.
    
    double u11; ///< Central moment 11.
    double u20; ///< Central moment 20.
    double u02; ///< Central moment 02.

    double n11; ///< Normalized central moment 11.
    double n20; ///< Normalized central moment 20.
    double n02; ///< Normalized central moment 02.

    double p1; ///< Hu moment 1.
    double p2; ///< Hu moment 2.

    CvContourChainCode contour;           ///< Contour.
    CvContoursChainCode internalContours; ///< Internal contours. 


For more information:

* http://github.com/oostendo/cvblob-python
* http://code.google.com/p/cvblob
* http://code.google.com/p/cvblob/source/browse/trunk/cvBlob/cvblob.h 
  """
  cvblob = ""
    
  def __init__(self, i, cb):
    self.points = [0,0,0,0]
    self.image = i
    self.cvblob = cb
    (self.x, self.y) = cvb.Centroid(cb)
    self.points[0] = (self.cvblob.minx, self.cvblob.miny)
    self.points[1] = (self.cvblob.maxx, self.cvblob.miny)
    self.points[2] = (self.cvblob.maxx, self.cvblob.maxy)
    self.points[3] = (self.cvblob.minx, self.cvblob.maxy)
    
  def area(self):
    return self.cvblob.area  

  def meanColor(self):
    """
      Returns the color tuple of the entire area of the blob
    """
    return cvb.BlobMeanColor(self.cvblob, self.image._blobLabel, self.image.getBitmap())

  def length(self):
    """
    Length returns the longest dimension of the X/Y bounding box 
    """
    return max(self.cvblob.maxx-self.cvblob.minx, self.cvblob.maxy-self.cvblob.miny)
   

#  todo?
#  def elongation(self):
#  def perimeter(self):
  #return angle in radians
  def angle(self):
    """
    This Angle function is defined as: 
    .5*atan2(2.* blob.cvblob.u11,(blob.cvblob.u20-blob.cvblob.u02))
    """
    return 360.00*(cvb.Angle(self.cvblob)/(2*np.pi))

  def draw(self, color = (0, 255, 0)):
    """
    Fill in the blob with the given color (default green), and flush buffers
    """
    cvb.RenderBlob(self.image._blobLabel, self.cvblob, self.image.getBitmap(), self.image.getBitmap(), cvb.CV_BLOB_RENDER_COLOR, color)
    self.image._clearBuffers("_bitmap")

class Line(Feature):
  """
  The Line class is returned by the findLines function, but can also be initialized with any two points:

  l = Line(Image, point1, point2) 
  Where point1 and point2 are coordinate tuples

  l.points will be a tuple of the two points
  """

  def __init__(self, i, line):
    self.image = i
    #coordinate of the line object is the midpoint
    self.x = (line[0][0] + line[1][0]) / 2
    self.y = (line[0][1] + line[1][1]) / 2
    self.points = copy(line)

  def draw(self, color = (0,0,255)):
    """
    Draw the line, default color is blue
    """
    self.image.drawLine(self.points[0], self.points[1], color)
     
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
      return self.image[pt1[0]:pt1[0]+1,miny:maxy].meanColor()
    if (d_y == 0.0):
      return self.image[minx:maxx,pt1[1]:pt1[1]+1].meanColor()
    
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
        px.append(self.image[x,y])
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
        px.append(self.image[x,y])
        weights.append(1.0 - abs(error))
        
        #if we have error in either direction, we're going to use the px
        #above or below
        if (error > 0): #
          px.append(self.image[x+1, y])
          weights.append(error)
  
        if (error < 0):
          px.append(self.image[x-1, y])
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
    return (360.00*(atan2(d_y, d_x)/(2*np.pi))) #formerly 0 was west

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
    numpoints = len(self.points)
    self.x = 0
    self.y = 0

    for p in self.points:
      self.x += p[0]
      self.y += p[1]

    if (numpoints):
      self.x /= numpoints
      self.y /= numpoints

  def draw(self, color = (255, 0, 0)): 
    """
    Draws the bounding area of the barcode, given by points.  Note that for
    QR codes, these points are the reference boxes, and so may "stray" into 
    the actual code.
    """
    self.image.drawLine(self.points[0], self.points[1], color)
    self.image.drawLine(self.points[1], self.points[2], color)
    self.image.drawLine(self.points[2], self.points[3], color)
    self.image.drawLine(self.points[3], self.points[0], color)

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


class HaarFeature(Feature):
  """
  The HaarFeature is a rectangle returned by the FindHaarFeature() function.

  - The x,y coordinates are defined by the center of the bounding rectangle
  - the classifier property refers to the cascade file used for detection 
  - points are the clockwise points of the bounding rectangle, starting in upper left
  """
  classifier = "" 
  width = ""
  height = ""
  
  def __init__(self, i, haarobject, haarclassifier=None):
    self.image = i
    ((x,y,self.width,self.height), self.neighbors) = haarobject
    self.x = x + self.width/2
    self.y = y + self.height/2 #set location of feature to middle of rectangle
    self.points = ((x, y), (x + self.width, y), (x + self.width, y + self.height), (x, y + self.height))
    #set bounding points of the rectangle
    self.classifier = haarclassifier
  
  def draw(self, color=(0,255,0)):
    """
    Draw the bounding rectangle, default color green
    """
    self.image.drawLine(self.points[0], self.points[1], color)
    self.image.drawLine(self.points[1], self.points[2], color)
    self.image.drawLine(self.points[2], self.points[3], color)
    self.image.drawLine(self.points[3], self.points[0], color)
    
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
    return max(self.width, self.height)

  def area(self):
    """
    Returns the area contained within the HaarFeature's bounding rectangle 
    """
    return self.width * self.height

  def angle(self):
    """
    Returns the angle of the rectangle -- horizontal if wide, vertical if tall
    """
    #Note this is misleading
    # I am not sure I like this 
    if (self.width > self.height):
      return 0.00
    else:
      return 90.00

  def width(self):
    """
    Get the width of the line.
    """
    return abs(self.points[1][0]- self.points[0][0])
    
  def height(self):
    """
    Get the height of the line
    """    
    return abs(self.points[1][1]- self.points[0][1])

class Chessboard(Feature):
  spCorners = []
  dimensions = ()
  
  def __init__(self, i, dim, subpixelCorners):
    self.dimensions = dim
    self.spCorners = subpixelCorners
    self.image = i
    self.x = np.average(np.array(self.spCorners)[:,0])
    self.y = np.average(np.array(self.spCorners)[:,1])
    
    posdiagsorted = sorted(self.spCorners, key = lambda corner: corner[0] + corner[1])
    #sort corners along the x + y axis
    negdiagsorted = sorted(self.spCorners, key = lambda corner: corner[0] - corner[1])
    #sort corners along the x - y axis
    
    self.points = (posdiagsorted[0], negdiagsorted[-1], posdiagsorted[-1], negdiagsorted[0])
    #return the exterior points in clockwise order
    
  def draw(self, no_needed_color=None):
    """
    Draws the chessboard corners.  We take a color param, but ignore it
    """
    cv.DrawChessboardCorners(self.image.getBitmap(),self.dimensions,self.spCorners,1)
    
  def area(self):
    """
    Returns the mean of the distance between corner points in the chessboard
    This can be used as a proxy for distance from the camera
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

#TODO?
#class Edge(Feature):
#class Ridge(Feature):
