#!/usr/bin/python

#system includes
import os, sys
from copy import copy
from math import sqrt, atan2
from pkg_resources import load_entry_point

#library includes
import cv
import numpy as np
import scipy.spatial.distance as spsd

#optional libraries
PIL_ENABLED = True
try:
  import Image as pil
except ImportError:
  PIL_ENABLED = False 




BLOBS_ENABLED = True
try:
  import cvblob as cvb
except ImportError:
  BLOBS_ENABLED = False 

ZXING_ENABLED = True
try:
  import zxing
except ImportError:
  ZXING_ENABLED = False 

#an abstract Camera class, for handling multiple types of video input
class FrameSource:
  def __init__(self):
    return

  def getPropery(self, p):
    return None

  def getAllProperties(self):
    return {}

  def getImage(self):
    return None

#camera class, wrappers the cvCapture class and associated methods
class Camera(FrameSource):
  capture = ""   #cvCapture object

  prop_map = {"width": cv.CV_CAP_PROP_FRAME_WIDTH,
    "height": cv.CV_CAP_PROP_FRAME_HEIGHT,
    "brightness": cv.CV_CAP_PROP_BRIGHTNESS,
    "contrast": cv.CV_CAP_PROP_CONTRAST,
    "saturation": cv.CV_CAP_PROP_SATURATION,
    "hue": cv.CV_CAP_PROP_HUE,
    "gain": cv.CV_CAP_PROP_GAIN,
    "exposure": cv.CV_CAP_PROP_EXPOSURE}
  #human readable to CV constant property mapping

  #constructor, camera_index indicates which camera to connect to
  #props is a dictionary which can be used to set any camera attributes
  def __init__(self, camera_index = 0, prop_set = {}):
    self.capture = cv.CaptureFromCAM(camera_index)

    if (not self.capture):
      return None 

    #set any properties in the constructor
    for p in prop_set.keys():
      if p in self.prop_map:
        cv.SetCaptureProperty(self.capture, self.prop_map[p], prop_set[p])

    
  #todo -- make these dynamic attributes of the Camera class
  def getProperty(self, prop):
    if prop in self.prop_map:
      return cv.GetCaptureProperty(self.capture, self.prop_map[prop]);
    return False 

  #dump all the available characteristics of this camera
  def getAllProperties(self):
    props = {} 
    for p in self.prop_map:
      props[p] = self.getProperty(p)

    return props

  #grab and retrieve an image, note that this should be retooled
  #when we want to do multiple camera support
  def getImage(self):
    return Image(cv.QueryFrame(self.capture))
  

#this is a virtual camera, initialized with some source which is not
#a camera directly connected to this computer
class VirtualCamera(FrameSource):
  source = ""
  sourcetype = ""
  capture = "" 
  
  def __init__(self, s, st):
    self.source = s
    self.sourcetype = st 
    
    if (self.sourcetype == 'video'):
      self.capture = cv.CaptureFromFile(self.source) 
    
  def getImage(self):
    if (self.sourcetype == 'image'):
      return Image(self.source)
    
    if (self.sourcetype == 'video'):
      return Image(cv.QueryFrame(self.capture))
   
#the Image class is the bulk of SimpleCV and wrappers the iplImage, cvMat,
#and most of the associated image processing functions
class Image:
  width = 0    #width and height in px
  height = 0
  depth = 0
  filename = "" #source filename

  _barcodeReader = "" #property for the ZXing barcode reader

  #these are buffer frames for various operations on the image
  _bitmap = ""  #the bitmap (iplimage)  representation of the image
  _matrix = ""  #the matrix (cvmat) representation
  _graybitmap = ""  #a reusable 8-bit grayscale bitmap
  _blobLabel = ""  #the label image for blobbing
  _edgeMap = "" #holding reference for edge map
  _cannyparam = (0,0) #parameters that created _edgeMap
  _pil = "" #holds a PIL object in buffer

  #when we empty the buffers, populate with this:
  _initialized_buffers = { 
    "_bitmap": "", 
    "_matrix": "", 
    "_graybitmap": "", 
    "_blobLabel": "",
    "_edgeMap": "",
    "_cannyparam": (0,0), 
    "_pil": ""}  
    
  #initialize the frame
  #parameters: source designation (filename)
  #todo: handle camera/capture from file cases (detect on file extension)
  def __init__(self, source):
    

    if (type(source) == cv.cvmat):
      self._matrix = source 
    elif (type(source) == cv.iplimage):
      self._bitmap = source
    elif (type(source) == type(str()) and source != ''):
      self.filename = source
      self._bitmap = cv.LoadImage(self.filename, iscolor=cv.CV_LOAD_IMAGE_COLOR) 
    elif (type(source) == instance): #it's a class instance, check class name
      if (PIL_ENABLED and source.__class__.__name__ == "JpegImageFile"):
        self._pil = source
        #from the opencv cookbook 
        #http://opencv.willowgarage.com/documentation/python/cookbook.html
        self._bitmap = cv.CreateImageHeader(self._pil.size, cv.IPL_DEPTH_8U, 3)
        cvSetData(self._bitmap, self._pil.tostring())
    else:
      return None 

    bm = self.getBitmap()
    self.width = bm.width
    self.height = bm.height
    self.depth = bm.depth

  #get the bitmap version (iplimage) of the image
  def getBitmap(self):
    if (self._bitmap):
      return self._bitmap
    elif (self._matrix):
      self._bitmap = cv.GetImage(self._matrix)

    return self._bitmap

  #get the matrix version of the image, if the matrix version doesn't exist
  #convert the bitmap
  def getMatrix(self):
    if (self._matrix):
      return self._matrix
    else:
      self._matrix = cv.GetMat(self.getBitmap()) #convert the bitmap to a matrix
      return self._matrix

  def getPIL(self):
    if (not PIL_ENABLED):
      return None
    if (not self._pil):
      self._pil = PIL.fromstring("RGB", self.size(), self.getBitmap().tostring())

    return self._pil


  def _getGrayscaleBitmap(self):
    if (self._graybitmap):
      return self._graybitmap

    self._graybitmap = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_8U, 1)
    cv.CvtColor(self.getBitmap(), self._graybitmap, cv.CV_BGR2GRAY) 
    return self._graybitmap

  #save the image, if no filename then use the load filename and overwrite
  def save(self, filename=""):
    if (filename):
      cv.SaveImage(filename, self.getBitmap())  
      self.filename = filename #set the filename for future save operations
    elif (self.filename):
      cv.SaveImage(self.filename, self.getBitmap())
    else:
      return 0

    return 1


  #scale this image, and return a new Image object with the new dimensions 
  def scale(self, width, height):
    scaled_matrix = cv.CreateMat(width, height, self.getMatrix().type)
    cv.Resize(self.getMatrix(), scaled_matrix)
    return Image(scaled_matrix)


  #interface to cv.Smooth -- note that we're going to "fake" in-place
  #smoothing for each image
  def smooth(self, algorithm_name = 'bilateral', aperature = '', sigma = 0, spatial_sigma = 0):
    win_x = 3
    win_y = 3  #set the default aperature window size (3x3)

    if (type(aperature) == tuple):
      win_x, win_y = aperature#get the coordinates from parameter
      #TODO: make sure aperature is valid 
      #   eg Positive, odd and square for bilateral and median

    algorithm = cv.CV_GAUSSIAN #default algorithm is gaussian 
    inplace = 1  

    #gauss and blur can work in-place, others need a buffer frame
    #use a string to ID rather than the openCV constant
    if algorithm_name == "blur":
      algorithm = cv.CV_BLUR
      inplace = 1
    if algorithm_name == "bilateral":
      algorithm = cv.CV_BILATERAL
      inplace = 0 
      win_y = win_x #aperature must be square
    if algorithm_name == "median":
      algorithm = cv.CV_MEDIAN
      inplace = 0 
      win_y = win_x #aperature must be square

    newmatrix = self.getMatrix()
    if (not inplace): 
      #create a new matrix, this will hold the altered image
      newmatrix = cv.CreateMat(self.getMatrix().rows, self.getMatrix().cols, self.getMatrix().type)

    cv.Smooth(self.getMatrix(), newmatrix, algorithm, win_x, win_y, sigma, spatial_sigma)

    if (not inplace):
      #replace the unaltered image with the changed image
      self._matrix = newmatrix 

    #reclaim any buffers
    self._clearBuffers("_matrix")

    return 1

  #get the mean color of an image
  def meanColor(self):
    return cv.Avg(self.getMatrix())[0:3]  
  

  def findCorners(self, maxnum = 50, minquality = 0.04, mindistance = 1.0):
    #initialize buffer frames
    eig_image = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_32F, 1)
    temp_image = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_32F, 1)

    corner_coordinates = cv.GoodFeaturesToTrack(self._getGrayscaleBitmap(), eig_image, temp_image, maxnum, minquality, mindistance, None)

    corner_features = []   
    for (x,y) in corner_coordinates:
      corner_features.append(Corner(self, x, y))

    return FeatureSet(corner_features)


  def findBlobs(self, threshval = 127, minsize=10, maxsize=0):
    if not BLOBS_ENABLED:
      return None

    if (maxsize == 0):  
      maxsize = self.width * self.height / 2
    
    #create a single channel image, thresholded to parameters
    grey = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_8U, 1)
    cv.Threshold(self._getGrayscaleBitmap(), grey, threshval, 255, cv.CV_THRESH_BINARY)

    #create the label image
    self._blobLabel = cv.CreateImage(cv.GetSize(self.getBitmap()), cvb.IPL_DEPTH_LABEL, 1)

    #initialize the cvblobs blobs data structure (dict with label -> blob)
    blobs = cvb.Blobs()

    result = cvb.Label(grey, self._blobLabel, blobs)
    cvb.FilterByArea(blobs, minsize, maxsize) 

    blobs_sizesorted = sorted(blobs.values(), key=lambda x: x.area, reverse=True) 

    blobsFS = [] #create a new featureset for the blobs
    for b in blobs_sizesorted:
      blobsFS.append(Blob(self,b)) #wrapper the cvblob type in SimpleCV's blob type 

    return FeatureSet(blobsFS) 

  def drawCircle(self, ctr, rad, color = (0,0,0), thickness = 1):
    cv.Circle(self.getMatrix(), (int(ctr[0]), int(ctr[1])), rad, color, thickness)
    self._clearBuffers("_matrix")

  def drawLine(self, pt1, pt2, color = (0,0,0), thickness = 1):
    pt1 = (int(pt1[0]), int(pt1[1]))
    pt2 = (int(pt2[0]), int(pt2[1]))
    cv.Line(self.getBitmap(), pt1, pt2, color, thickness, cv.CV_AA) 

  #return the width, height as a tuple
  def size(self):
    return cv.GetSize(self.getBitmap())

  #split the channels of an image into RGB (not the default BGR)
  #single parameter is whether to return the channels as grey images
  #or to return them as tinted color image (default)
  def channels(self, grayscale = False):
    r = cv.CreateImage(self.size(), 8, 1)
    g = cv.CreateImage(self.size(), 8, 1)
    b = cv.CreateImage(self.size(), 8, 1)
    cv.Split(self.getBitmap(), b, g, r, None)

    if (grayscale):
      return (Image(r), Image(g), Image(b)) 
    else:
      red = cv.CreateImage(self.size(), 8, 3)
      green = cv.CreateImage(self.size(), 8, 3)
      blue = cv.CreateImage(self.size(), 8, 3)
      cv.Merge(None, None, r, None, red)
      cv.Merge(None, g, None, None, green)
      cv.Merge(b, None, None, None, blue)
      return (Image(red), Image(green), Image(blue)) 

  #return a histogram of intensity for the image, note that this desaturates
  #the image to a grayscale image
  def histogram(self, numbins = 50):
    gray = self._getGrayscaleBitmap()

    (hist, bin_edges) = np.histogram(np.asarray(cv.GetMat(gray)), bins=numbins)
    return hist.tolist()

  def __getitem__(self, coord):
    ret = self.getMatrix()[coord]
    if (type(ret) == cv.cvmat):
      return Image(ret)
    return ret

  def __setitem__(self, coord, value):
    if (type(self.getMatrix()[coord]) == tuple):
      self.getMatrix()[coord] = value
    else:
      cv.Set(self.getMatrix()[coord], value)
      self._clearBuffers("_matrix") 

  def _clearBuffers(self, clearexcept = "_bitmap"):
    for k, v in self._initialized_buffers.items():
      if k == clearexcept:
        continue
      self.__dict__[k] = v

  def findBarcode(self, zxing_path = ""):
    if not ZXING_ENABLED:
      return None

    if (not self._barcodeReader):
      if not zxing_path:
        self._barcodeReader = zxing.BarCodeReader()
      else:
        self._barcodeReader = zxing.BarCodeReader(zxing_path)

    tmp_filename = os.tmpnam() + ".png"
    self.save(tmp_filename)
    barcode = self._barcodeReader.decode(tmp_filename)
    os.unlink(tmp_filename)

    if barcode:
      return Barcode(self, barcode)
    else:
      return None

  #this function contains two functions -- the basic edge detection algorithm
  #and then a function to break the lines down given a threshold parameter
  def findLines(self, threshold=80, minlinelength=30, maxlinegap=10, cannyth1=50, cannyth2=100):

    em = self.getEdgeMap(cannyth1, cannyth2)
    
    lines = cv.HoughLines2(em, cv.CreateMemStorage(), cv.CV_HOUGH_PROBABILISTIC, 1.0, cv.CV_PI/180.0, threshold, minlinelength, maxlinegap)

    linesFS = FeatureSet()
    for l in lines:
      linesFS.append(Line(self, l))  
    
    return linesFS

  def getEdgeMap(self, t1=50, t2=100):
    if (self._edgeMap and self._cannyparam[0] == t1 and self._cannyparam[1] == t2):
      return self._edgeMap

    self._edgeMap = cv.CreateImage(self.size(), 8, 1)
    cv.Canny(self._getGrayscaleBitmap(), self._edgeMap, t1, t2)
    self._cannyparam = (t1, t2)

    return self._edgeMap

class FeatureSet(list):

  def draw(self, color = (255,0,0)):
    for f in self:
      f.draw(color) 

  def coordinates(self):
    return np.array([[f.x, f.y] for f in self]) 

  def area(self):
    return np.array([f.area() for f in self]) 

  def sortArea(self):
    return FeatureSet(sorted(self, key=lambda f: f.area()))

  def distanceFrom(self, point = (-1, -1)):
    return np.array([f.distanceFrom(point) for f in self ])

  def sortDistance(self, point = (-1, -1)):
    return FeatureSet(sorted(self, key=lambda f: f.distanceFrom(point)))

  def angle(self):
    return np.array([f.angle() for f in self])

  def sortAngle(self, theta = 0):
    return FeatureSet(sorted(self, key=lambda f: abs(f.angle() - theta)))
  
  def length(self):
    return np.array([f.length() for f in self])

  def sortLength(self):
    return FeatureSet(sorted(self, key=lambda f: f.length()))

  def meanColor(self):
    return np.array([f.meanColor() for f in self])

  def colorDistance(self, color = (0,0,0)):
    return np.array([f.colorDistance(color) for f in self])
  
  def sortColorDistance(self, color = (0,0,0)):
    return FeatureSet(sorted(self, key=lambda f: f.colorDistance(color)))


class Feature(object):
  x = 0.0
  y = 0.0 
  image = "" #parent image

  def __init__(self, i, at_x, at_y):
    self.x = at_x
    self.y = at_y
    self.image = i

  def coordinates(self):
    return [self.x, self.y]  

  #in this abstract case, we're just going to color the exact point 
  #the desired color
  def draw(self, color = (255.0,0.0,0.0)):
    self.image[self.x,self.y] = color

  #return euclidian distance from coordinates
  def distanceFrom(self, point = (-1,-1)): 
    if (point[0] == -1 or point[1] == -1):
      point = np.array(self.image.size())/2
    return spsd.euclidean(point, [self.x, self.y]) 

  def meanColor(self):
    return self.image[self.x, self.y]

  #return distance from a given color, default black (brightness)
  def colorDistance(self, color = (0,0,0)): 
    return spsd.euclidean(color, self.meanColor()) 

  #angle (theta) of the feature -- default 0
  def angle(self):
    return 0

  #longest dimension of the feature -- default 1
  def length(self):
    return 1

  #area of the feature -- default 1 
  def area(self):
    return 1 

class Corner(Feature):

  def __init__(self, i, at_x, at_y):
    super(Corner, self).__init__(i, at_x, at_y)
    #can we look at the eigenbuffer and find direction?

  def draw(self, color = (255, 0, 0)):
    self.image.drawCircle((self.x, self.y), 4, color)

#stubbing out blob interface
class Blob(Feature):
  cvblob = ""
  
  def __init__(self, i, cb): 
    self.image = i
    self.cvblob = cb
    (self.x, self.y) = cvb.Centroid(cb)

  def area(self):
    return self.cvblob.area  

  def meanColor(self):
    return cvb.BlobMeanColor(self.cvblob, self.image._blobLabel, self.image.getBitmap())

  #this takes the longest dimension of the X/Y orientation -- seems like
  #the optimal solution should be taking the longest dimension of a rotated
  #bounding box.  Oh well
  def length(self):
    return max(self.cvblob.maxx-self.cvblob.minx, self.cvblob.maxy-self.cvblob.miny)

#  todo?
#  def elongation(self):
#  def perimeter(self):
  #return angle in radians
  def angle(self):
    return cvb.Angle(self.cvblob)

  def draw(self, color = (0, 255, 0)):
    cvb.RenderBlob(self.image._blobLabel, self.cvblob, self.image.getBitmap(), self.image.getBitmap(), cvb.CV_BLOB_RENDER_COLOR, color)


class Line(Feature):
  points = ()

  def __init__(self, i, line):
    self.image = i
    #coordinate of the line object is the midpoint
    self.x = (line[0][0] + line[1][0]) / 2
    self.y = (line[0][1] + line[1][1]) / 2
    self.points = copy(line)

  def draw(self, color = (0,0,255)):
    self.image.drawLine(self.points[0], self.points[1], color)
     
  def length(self):
    return spsd.euclidean(self.points[0], self.points[1])  

  def meanColor(self):
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
      return self.image[pt1[0],miny:maxy].meanColor()
    if (d_y == 0.0):
      return self.image[minx:maxx,pt1[1]].meanColor()
    
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
    #first find the rightmost point 
    a = 0
    b = 1
    if (self.points[a][0] > self.points[b][0]):
      b = 0 
      a = 1
    
    d_x = self.points[b][0] - self.points[a][0]
    d_y = self.points[b][1] - self.points[a][1]
    return atan2(d_y, d_x) #zero is west 

class Barcode(Feature):
  data = ""
  points = []

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
    self.image.drawLine(self.points[0], self.points[1], color)
    self.image.drawLine(self.points[1], self.points[2], color)
    self.image.drawLine(self.points[2], self.points[3], color)
    self.image.drawLine(self.points[3], self.points[0], color)

  def length(self):
    sqform = spsd.squareform(spsd.pdist(self.points, "euclidean"))
    #get pairwise distances for all points
    #note that the code is a quadrilateral
    return max(sqform[0][1], sqform[1][2], sqform[2,3], sqform[3,0])

  def area(self):
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

#TODO?
#class Edge(Feature):
#class Ridge(Feature):


if __name__ == '__main__':
    sys.exit(
        load_entry_point('ipython==0.10.2', 'console_scripts', 'ipython')()
    )

