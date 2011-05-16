#!/usr/bin/python

#system includes
import os, sys, warnings, time, socket
import SocketServer
import threading
from copy import copy
from math import sqrt, atan2
from pkg_resources import load_entry_point
from SimpleHTTPServer import SimpleHTTPRequestHandler
from types import IntType, LongType, FloatType

#couple quick typecheck helper functions
def is_number(n):
  return n in (IntType, LongType, FloatType)

def is_tuple(n):
  return type(n) == tuple 

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

class FrameSource:
  """
  An abstract Camera-type class, for handling multiple types of video input.
  Any sources of images inheirit from it
  """
  def __init__(self):
    return

  def getPropery(self, p):
    return None

  def getAllProperties(self):
    return {}

  def getImage(self):
    return None

_cameras = [] 
_camera_polling_thread = "" 

class FrameBufferThread(threading.Thread):
  """
  This is a helper thread which continually debuffers the camera frames.  If
  you don't do this, cameras may constantly give you a frame behind, which
  causes problems at low sample rates.  This makes sure the frames returned
  by your camera are fresh.
  """
  def run(self):
    while (1):
      for cam in _cameras:
        cv.GrabFrame(cam.capture)
      time.sleep(0.04)    #max 25 fps, if you're lucky

class Camera(FrameSource):
  """
The Camera class is the class for managing input from a basic camera.  Note
that once the camera is initialized, it will be locked from being used 
by other processes.  You can check manually if you have compatable devices
on linux by looking for /dev/video* devices.

This class wrappers OpenCV's cvCapture class and associated methods.  
Read up on OpenCV's CaptureFromCAM method for more details if you need finer
control than just basic frame retrieval
  """
  capture = ""   #cvCapture object
  thread = ""


  prop_map = {"width": cv.CV_CAP_PROP_FRAME_WIDTH,
    "height": cv.CV_CAP_PROP_FRAME_HEIGHT,
    "brightness": cv.CV_CAP_PROP_BRIGHTNESS,
    "contrast": cv.CV_CAP_PROP_CONTRAST,
    "saturation": cv.CV_CAP_PROP_SATURATION,
    "hue": cv.CV_CAP_PROP_HUE,
    "gain": cv.CV_CAP_PROP_GAIN,
    "exposure": cv.CV_CAP_PROP_EXPOSURE}
  #human readable to CV constant property mapping

  def __init__(self, camera_index = 0, prop_set = {}, threaded = True):
    global _cameras
    global _camera_polling_thread
    """
    In the camera onstructor, camera_index indicates which camera to connect to
    and props is a dictionary which can be used to set any camera attributes
    Supported props are currently: height, width, brightness, contrast,
    saturation, hue, gain, and exposure.

    You can also specify whether you want the FrameBufferThread to continuously
    debuffer the camera.  If you specify True, the camera is essentially 'on' at
    all times.  If you specify off, you will have to manage camera buffers.
    """
    self.capture = cv.CaptureFromCAM(camera_index)
    self.threaded = False

    if (not self.capture):
      return None 

    #set any properties in the constructor
    for p in prop_set.keys():
      if p in self.prop_map:
        cv.SetCaptureProperty(self.capture, self.prop_map[p], prop_set[p])

    if (threaded):
      self.threaded = True
      _cameras.append(self)
      if (not _camera_polling_thread):
        _camera_polling_thread = FrameBufferThread()
        _camera_polling_thread.start()
      
    
  #todo -- make these dynamic attributes of the Camera class
  def getProperty(self, prop):
    """
    Retrieve the value of a given property, wrapper for cv.GetCaptureProperty
    """
    if prop in self.prop_map:
      return cv.GetCaptureProperty(self.capture, self.prop_map[prop]);
    return False 

  def getAllProperties(self):
    """
    Return all properties from the camera 
    """
    props = {} 
    for p in self.prop_map:
      props[p] = self.getProperty(p)

    return props

  def getImage(self):
    """
    Retrieve an Image-object from the camera.  If you experience problems
    with stale frames from the camera's hardware buffer, increase the flushcache
    number to dequeue multiple frames before retrieval

    We're working on how to solve this problem.
    """
    if (not self.threaded):
      cv.GrabFrame(self.capture)

    frame = cv.RetrieveFrame(self.capture)
    newimg = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
    cv.Copy(frame, newimg)
    return Image(newimg)
  

class VirtualCamera(FrameSource):
  """
  The virtual camera lets you test algorithms or functions by providing 
  a Camera object which is not a physically connected device.
  
  Currently, VirtualCamera supports "image" and "video" source types.
  """
  source = ""
  sourcetype = ""
  capture = "" 
  
  def __init__(self, s, st):
    """
    The constructor takes a source, and source type.  ie:
    VirtualCamera("img.jpg", "image") or VirtualCamera("video.mpg", "video")
    """
    self.source = s
    self.sourcetype = st 
    
    if (self.sourcetype == 'video'):
      self.capture = cv.CaptureFromFile(self.source) 
    
  def getImage(self):
    """
    Retrieve the next frame of the video, or just a copy of the image
    """
    if (self.sourcetype == 'image'):
      return Image(self.source)
    
    if (self.sourcetype == 'video'):
      return Image(cv.QueryFrame(self.capture))
   
class Image:
  """
  The Image class is the heart of SimpleCV and allows you to convert to and 
  from a number of source types with ease.  It also has intelligent buffer
  management, so that modified copies of the Image required for algorithms
  such as edge detection, etc can be cached and reused when appropriate.

  Images are converted into 8-bit, 3-channel images in RGB colorspace.  It will
  automatically handle conversion from other representations into this
  standard format. 
  """
  width = 0    #width and height in px
  height = 0
  depth = 0
  filename = "" #source filename

  _barcodeReader = "" #property for the ZXing barcode reader

  #these are buffer frames for various operations on the image
  _bitmap = ""  #the bitmap (iplimage)  representation of the image
  _matrix = ""  #the matrix (cvmat) representation
  _graybitmap = ""  #a reusable 8-bit grayscale bitmap
  _equalizedgraybitmap = "" #the above bitmap, normalized
  _blobLabel = ""  #the label image for blobbing
  _edgeMap = "" #holding reference for edge map
  _cannyparam = (0,0) #parameters that created _edgeMap
  _pil = "" #holds a PIL object in buffer

  #when we empty the buffers, populate with this:
  _initialized_buffers = { 
    "_bitmap": "", 
    "_matrix": "", 
    "_graybitmap": "", 
    "_equalizedgraybitmap": "",
    "_blobLabel": "",
    "_edgeMap": "",
    "_cannyparam": (0,0), 
    "_pil": ""}  
    
  #initialize the frame
  #parameters: source designation (filename)
  #todo: handle camera/capture from file cases (detect on file extension)
  def __init__(self, source):
    """ 
    The constructor takes a single polymorphic parameter, which it tests
    to see how it should convert into an RGB image.  Supported types include:
    
    OpenCV: iplImage and cvMat types
    Python Image Library: Image type
    Filename: All opencv supported types (jpg, png, bmp, gif, etc)
    """
    if (type(source) == cv.cvmat):
      self._matrix = source 
    elif (type(source) == cv.iplimage):
      self._bitmap = source
    elif (type(source) == type(str()) and source != ''):
      self.filename = source
      self._bitmap = cv.LoadImage(self.filename, iscolor=cv.CV_LOAD_IMAGE_COLOR) 
    elif (PIL_ENABLED and source.__class__.__name__ == "JpegImageFile"):
      self._pil = source
      #from the opencv cookbook 
      #http://opencv.willowgarage.com/documentation/python/cookbook.html
      self._bitmap = cv.CreateImage(self._pil.size, cv.IPL_DEPTH_8U, 3)
      cv.SetData(self._bitmap, self._pil.tostring())
      self._bitmap = cv.iplimage(self._bitmap)
    else:
      return None 

    bm = self.getBitmap()
    self.width = bm.width
    self.height = bm.height
    self.depth = bm.depth

  def getBitmap(self):
    """
    Retrieve the bitmap (iplImage) of the Image.  This is useful if you want
    to use functions from OpenCV with SimpleCV's image class
    """
    if (self._bitmap):
      return self._bitmap
    elif (self._matrix):
      self._bitmap = cv.GetImage(self._matrix)

    return self._bitmap

  def getMatrix(self):
    """
    Get the matrix (cvMat) version of the image, required for some OpenCV algorithms 
    """
    if (self._matrix):
      return self._matrix
    else:
      self._matrix = cv.GetMat(self.getBitmap()) #convert the bitmap to a matrix
      return self._matrix

  def getPIL(self):
    """ 
    Get a PIL Image object for use with the Python Image Library
    """ 
    if (not PIL_ENABLED):
      return None
    if (not self._pil):
      self._pil = pil.fromstring("RGB", self.size(), self.getBitmap().tostring())
    return self._pil

  def _getGrayscaleBitmap(self):
    if (self._graybitmap):
      return self._graybitmap

    self._graybitmap = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_8U, 1)
    cv.CvtColor(self.getBitmap(), self._graybitmap, cv.CV_BGR2GRAY) 
    return self._graybitmap

  def _getEqualizedGrayscaleBitmap(self):

    if (self._equalizedgraybitmap):
      return self._equalizedgraybitmap

    self._equalizedgraybitmap = cv.CreateImage(self.size(), 8, 1)
    cv.EqualizeHist(self._getGrayscaleBitmap(), self._equalizedgraybitmap)

    return self._equalizedgraybitmap
    
  def save(self, filename=""):
    """
    Save the image to the specified filename.  If no filename is provided then
    then it will use the filename the Image was loaded from or the last
    place it was saved to. 
    """
    if (filename):
      cv.SaveImage(filename, self.getBitmap())  
      self.filename = filename #set the filename for future save operations
    elif (self.filename):
      cv.SaveImage(self.filename, self.getBitmap())
    else:
      return 0

    return 1

  def copy(self):
    """
    Return a full copy of the Image's bitmap.  Note that this is different
    from using python's implicit copy function in that only the bitmap itself
    is copied.
    """
    newimg = cv.CreateImage(self.size(), cv.IPL_DEPTH_8U, 3)
    cv.Copy(self.getBitmap(), newimg)
    return Image(newimg) 
    
  #scale this image, and return a new Image object with the new dimensions 
  def scale(self, width, height):
    """
    Scale the image to a new width and height.
    """
    scaled_matrix = cv.CreateMat(width, height, self.getMatrix().type)
    cv.Resize(self.getMatrix(), scaled_matrix)
    return Image(scaled_matrix)

  def smooth(self, algorithm_name = 'gaussian', aperature = '', sigma = 0, spatial_sigma = 0):
    """
    Smooth the image, by default with the Gaussian blur.  If desired,
    additional algorithms and aperatures can be specified.  Optional parameters
    are passed directly to OpenCV's cv.Smooth() function. 
    """
    win_x = 3
    win_y = 3  #set the default aperature window size (3x3)

    if (is_tuple(aperature)):
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

  def invert(self):
    """
    Invert (negative) the image note that this can also be done with the
    unary minus (-) operator. 
    """
    return -self 

  def threshold(self, thresh = 127):
    """
    Do a binary threshold the image, changing all values above thresh to white
    and all below to black.  If a color tuple is provided, each color channel
    is thresholded separately.
    """
    if (is_tuple(thresh)):
      r = cv.CreateImage(self.size(), 8, 1)
      g = cv.CreateImage(self.size(), 8, 1)
      b = cv.CreateImage(self.size(), 8, 1)
      cv.Split(self.getBitmap(), b, g, r, None)

      cv.Threshold(r, r, thresh[0], 255, cv.CV_THRESH_BINARY)
      cv.Threshold(g, g, thresh[1], 255, cv.CV_THRESH_BINARY)
      cv.Threshold(b, b, thresh[2], 255, cv.CV_THRESH_BINARY)

      cv.Add(r, g, r)
      cv.Add(r, b, r)
      
      newbitmap = cv.CreateImage(self.size(), 8, 3)
      cv.Merge(r, r, r, None, newbitmap)
      self._bitmap = newbitmap

    else:
      #desaturate the image, and apply the new threshold          
      cv.Threshold(self._getGrayscaleBitmap(), self._getGrayscaleBitmap(), thresh)


    self._clearBuffers("_bitmap")
      
  

  #get the mean color of an image
  def meanColor(self):
    """
    Return the average color of all the pixels in the image.
    """
    return cv.Avg(self.getMatrix())[0:3]  
  

  def findCorners(self, maxnum = 50, minquality = 0.04, mindistance = 1.0):
    """
    This will find corner Feature objects and return them as a FeatureSet
    strongest corners first.  The parameters give the number of corners to look
    for, the minimum quality of the corner feature, and the minimum distance
    between corners. 
    """
    #initialize buffer frames
    eig_image = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_32F, 1)
    temp_image = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_32F, 1)

    corner_coordinates = cv.GoodFeaturesToTrack(self._getGrayscaleBitmap(), eig_image, temp_image, maxnum, minquality, mindistance, None)

    corner_features = []   
    for (x,y) in corner_coordinates:
      corner_features.append(Corner(self, x, y))

    return FeatureSet(corner_features)

  def findBlobs(self, threshval = 127, minsize=10, maxsize=0):
    """
    If you have the cvblob library installed, this will look for continuous
    light regions and return them as Blob features in a FeatureSet.  Parameters
    specify the threshold value, and minimum and maximum size for blobs.

    You can find the cv-blob python library at http://github.com/oostendo/cvblob-python
    """
    if not BLOBS_ENABLED:
      warnings.warn("You tried to use findBlobs, but cvblob is not installed.  Go to http://github.com/oostendo/cvblob-python and git clone it.")
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

  #this code is based on code that's based on code from
  #http://blog.jozilla.net/2008/06/27/fun-with-python-opencv-and-face-detection/
  def findHaarFeatures(self, cascadefile, scale_factor=1.2, min_neighbors=2, use_canny=cv.CV_HAAR_DO_CANNY_PRUNING):
    """
    If you want to find Haar Features (useful for face detection among other
    purposes) this will return Haar feature objects in a FeatureSet.  The
    parameters are:
    * the scaling factor for subsequent rounds of the haar cascade (default 1.2)
    * the minimum number of rectangles that makes up an object (default 2)
    * whether or not to use Canny pruning to reject areas with too many edges (default yes, set to 0 to disable) 

    For more information, consult the cv.HaarDetectObjects documentation
   
    You will need to provide your own cascade file - these are usually found in
    /usr/local/share/opencv/haarcascades and specify a number of body parts.
    """
    storage = cv.CreateMemStorage(0)

    #lovely.  This segfaults if not present
    if (not os.path.exists(cascadefile)):
      warnings.warn("Could not find Haar Cascade file " + cascadefile)
      return None
    cascade = cv.Load(cascadefile) 
    objects = cv.HaarDetectObjects(self._getEqualizedGrayscaleBitmap(), cascade, storage, scale_factor, min_neighbors, use_canny, (0,0))
    if objects: 
      return FeatureSet([HaarFeature(self, o, cascadefile) for o in objects])
    
    return None

  def drawCircle(self, ctr, rad, color = (0,0,0), thickness = 1):
    """
    Draw a circle on the Image, parameters include:
    * the center of the circle
    * the radius in pixels
    * a color tuple (default black)
    * the thickness of the circle

    Note that this modifies the image in-place and clears all buffers.
    """
    cv.Circle(self.getBitmap(), (int(ctr[0]), int(ctr[1])), rad, color, thickness)
    self._clearBuffers("_bitmap")

  def drawLine(self, pt1, pt2, color = (0,0,0), thickness = 1):
    """
    Draw a line on the Image, parameters include
    *the first point for the line (tuple)
    *the second point on the line (tuple)
    *a color tuple (default black)
    *thickness of the line 
 
    Note that this modifies the image in-place and clears all buffers.
    """
    pt1 = (int(pt1[0]), int(pt1[1]))
    pt2 = (int(pt2[0]), int(pt2[1]))
    cv.Line(self.getBitmap(), pt1, pt2, color, thickness, cv.CV_AA) 

  def size(self):
    """
    Return the width and height as a tuple
    """
    return cv.GetSize(self.getBitmap())

  def channels(self, grayscale = True):
    """
    Split the channels of an image into RGB (not the default BGR)
    single parameter is whether to return the channels as grey images (default)
    or to return them as tinted color image 

    returns: tuple of 3 image objects
    """
    r = cv.CreateImage(self.size(), 8, 1)
    g = cv.CreateImage(self.size(), 8, 1)
    b = cv.CreateImage(self.size(), 8, 1)
    cv.Split(self.getBitmap(), b, g, r, None)

    red = cv.CreateImage(self.size(), 8, 3)
    green = cv.CreateImage(self.size(), 8, 3)
    blue = cv.CreateImage(self.size(), 8, 3)
	
    if (grayscale):
      cv.Merge(r, r, r, None, red)
      cv.Merge(g, g, g, None, green)
      cv.Merge(b, b, b, None, blue)
    else:
      cv.Merge(None, None, r, None, red)
      cv.Merge(None, g, None, None, green)
      cv.Merge(b, None, None, None, blue)

    return (Image(red), Image(green), Image(blue)) 

  def histogram(self, numbins = 50):
    """
    Return a numpy array of the 1D histogram of intensity for pixels in the image
    Single parameter is how many "bins" to have.
    """
    gray = self._getGrayscaleBitmap()

    (hist, bin_edges) = np.histogram(np.asarray(cv.GetMat(gray)), bins=numbins)
    return hist.tolist()

  def __getitem__(self, coord):
    ret = self.getMatrix()[coord]
    if (type(ret) == cv.cvmat):
      return Image(ret)
    return tuple(reversed(ret))

  def __setitem__(self, coord, value):
    if (is_tuple(self.getMatrix()[coord])):
      self.getMatrix()[coord] = tuple(reversed(value))
    else:
      cv.Set(self.getMatrix()[coord], value)
      self._clearBuffers("_matrix") 

  def __sub__(self, other):
    newbitmap = cv.CreateImage(self.size(), 8, 3)
    if is_number(other):
      cv.SubS(self.getBitmap(), other, newbitmap)
    else:
      cv.Sub(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def __add__(self, other):
    newbitmap = cv.CreateImage(self.size(), 8, 3)
    if is_number(other):
      cv.AddS(self.getBitmap(), other, newbitmap)
    else:
      cv.Add(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def __and__(self, other):
    newbitmap = cv.CreateImage(self.size(), 8, 3)
    if is_number(other):
      cv.AndS(self.getBitmap(), other, newbitmap)
    else:
      cv.And(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def __or__(self, other):
    newbitmap = cv.CreateImage(self.size(), 8, 3)
    if is_number(other):
      cv.OrS(self.getBitmap(), other, newbitmap)
    else:
      cv.Or(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def __div__(self, other):
    newbitmap = cv.CreateImage(self.size(), 8, 3)
    cv.Div(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def __pow__(self, other):
    newbitmap = cv.CreateImage(self.size(), 8, 3)
    cv.Pow(self.getBitmap(), newbitmap, other)
    return Image(newbitmap)

  def __neg__(self):
    newbitmap = cv.CreateImage(self.size(), 8, 3)
    cv.Not(self.getBitmap(), newbitmap)
    return Image(newbitmap)

  def max(self, other):
    """
    Return the maximum value of my image, and the other image, in each channel
    If other is a number, returns the maximum of that and the number
    """ 
    newbitmap = cv.CreateImage(self.size(), 8, 3)
    if is_number(other):
      cv.MaxS(self.getBitmap(), other.getBitmap(), newbitmap)
    else:
      cv.Max(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def min(self, other):
    """
    Return the minimum value of my image, and the other image, in each channel
    If other is a number, returns the minimum of that and the number
    """ 
    newbitmap = cv.CreateImage(self.size(), 8, 3)
    if is_number(other):
      cv.MaxS(self.getBitmap(), other.getBitmap(), newbitmap)
    else:
      cv.Max(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def _clearBuffers(self, clearexcept = "_bitmap"):
    for k, v in self._initialized_buffers.items():
      if k == clearexcept:
        continue
      self.__dict__[k] = v

  def findBarcode(self, zxing_path = ""):
    """
    If you have the python-zxing library installed, you can find 2d and 1d
    barcodes in your image.  These are returned as Barcode feature objects
    in a FeatureSet.  The single parameter is the ZXing_path, if you 
    don't have the ZXING_LIBRARY env parameter set.

    You can clone python-zxing at http://github.com/oostendo/python-zxing
    """
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
    """
    findLines will find line segments in your image and returns Line feature 
    objects in a FeatureSet. The parameters are:
    * threshold, which determies the minimum "strength" of the line
    * min line length -- how many pixels long the line must be to be returned
    * max line gap -- how much gap is allowed between line segments to consider them the same line 
    * cannyth1 and cannyth2 are thresholds used in the edge detection step, refer to getEdgeMap() for details

    For more information, consult the cv.HoughLines2 documentation
    """
    em = self.getEdgeMap(cannyth1, cannyth2)
    
    lines = cv.HoughLines2(em, cv.CreateMemStorage(), cv.CV_HOUGH_PROBABILISTIC, 1.0, cv.CV_PI/180.0, threshold, minlinelength, maxlinegap)

    linesFS = FeatureSet()
    for l in lines:
      linesFS.append(Line(self, l))  
    
    return linesFS

  def getEdgeMap(self, t1=50, t2=100):
    """
    Return the binary bitmap which shows where edges are in the image.  The two
    parameters determine how much change in the image determines an edge, 
    and how edges are linked together.  For more information refer to:

    http://en.wikipedia.org/wiki/Canny_edge_detector
    http://opencv.willowgarage.com/documentation/python/imgproc_feature_detection.html?highlight=canny#Canny
    """ 
  
    if (self._edgeMap and self._cannyparam[0] == t1 and self._cannyparam[1] == t2):
      return self._edgeMap

    self._edgeMap = cv.CreateImage(self.size(), 8, 1)
    cv.Canny(self._getGrayscaleBitmap(), self._edgeMap, t1, t2)
    self._cannyparam = (t1, t2)

    return self._edgeMap

class FeatureSet(list):
  """
  FeatureSet is a class extended from Python's list which has special
  functions so that it is useful for handling feature metadata on an image.
  
  In general, functions dealing with attributes will return numpy arrays, and
  functions dealing with sorting or filtering will return new FeatureSets.
  """

  def draw(self, color = (255,0,0)):
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
    return FeatureSet(sorted(self, key=lambda f: f.area()))

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
    return FeatureSet(sorted(self, key=lambda f: f.distanceFrom(point)))

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
    return FeatureSet(sorted(self, key=lambda f: abs(f.angle() - theta)))

  def length(self):
    """
    Return a numpy array of the length (longest dimension) of each feature.
    """
   
    return np.array([f.length() for f in self])

  def sortLength(self):
    """
    Return a sorted FeatureSet with the longest features first. 
    """
    return FeatureSet(sorted(self, key=lambda f: f.length()))

  def meanColor(self):
    """
    Return a numpy array of the average color of the area covered by each Feature.
    """
    return np.array([f.meanColor() for f in self])

  def colorDistance(self, color = (0,0,0)):
    """
    Return a numpy array of the distance each features average color is from
    a given color tuple (default black, so colorDistance() returns intensity)
    """
    return np.array([f.colorDistance(color) for f in self])
  
  def sortColorDistance(self, color = (0,0,0)):
    """
    Return a sorted FeatureSet with features closest to a given color first.
    Default is black, so sortColorDistance() will return darkest to brightest
    """
    return FeatureSet(sorted(self, key=lambda f: f.colorDistance(color)))

  def filter(self, filterarray):
    """
    Return a FeatureSet which is filtered on a numpy boolean array.  This
    will let you use the attribute functions to easily screen Features out
    of return FeatureSets.  

    Some examples:
    * my_lines.filter(my_lines.length() < 200) # returns all lines < 200px
    * my_blobs.filter(my_blobs.area() > 0.9 * my_blobs.length**2) # returns blobs that are nearly square    
    * my_lines.filter(abs(my_lines.angle()) < numpy.pi / 4) #any lines within 45 degrees of horizontal
    * my_corners.filter(my_corners.x() - my_corners.y() > 0) #only return corners in the upper diagonal of the image
    """
    return FeatureSet(list(np.array(self)[filterarray]))
    

class Feature(object):
  """
  The Feature object is an abstract class which real features descend from.j
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

  def __init__(self, i, at_x, at_y):
    self.x = at_x
    self.y = at_y
    self.image = i

  def coordinates(self):
    return np.array([self.x, self.y])  

  def draw(self, color = (255.0,0.0,0.0)):
    """
    In this abstract case, we're just going to color the exact point 
    """
    self.image[self.x,self.y] = color

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
  """
  The Corner feature is basically a point returned by the FindCorners function
  """
  def __init__(self, i, at_x, at_y):
    super(Corner, self).__init__(i, at_x, at_y)
    #can we look at the eigenbuffer and find direction?

  def draw(self, color = (255, 0, 0)):
    """
    Draw a small circle around the corner.  Color tuple is single parameter 
    """
    self.image.drawCircle((self.x, self.y), 4, color)

class Blob(Feature):
  """
  The Blob Feature  
  """
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


class HaarFeature(Feature):
  points = ()
  neighbors = 0
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
    #draw the bounding rectangle
    self.image.drawLine(self.points[0], self.points[1], color)
    self.image.drawLine(self.points[1], self.points[2], color)
    self.image.drawLine(self.points[2], self.points[3], color)
    self.image.drawLine(self.points[3], self.points[0], color)
    
  #crop out the face and detect the color on that image
  def meanColor(self):
    crop = self.image[self.points[0][0]:self.points[1][0], self.points[0][1]:self.points[2][1]]
    return crop.meanColor()

  def length(self):
    return max(self.width, self.height)

  def area(self):
    return self.width * self.height

  def angle(self):
    if (self.width > self.height):
      return 0
    else:
      return np.pi / 2 


#TODO?
#class Edge(Feature):
#class Ridge(Feature):

#global class to pass data from the jpegstreamer to the jpegstreamhandler
_jpegstreamers = {}

class JpegStreamHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
      self.send_response(200)
      self.send_header("Connection", "close")
      self.send_header("Max-Age", "0")
      self.send_header("Expires", "0")
      self.send_header("Cache-Control", "no-cache, private")
      self.send_header("Pragma", "no-cache")
      self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=--BOUNDARYSTRING")
      self.end_headers()
      (host, port) = self.server.socket.getsockname()[:2]
     
      count = 0
      timeout = 1 
      lastmodtime = 0
      lasttimeserved = 0
      jpgfile = ""
      while (1):
        interval = _jpegstreamers[port].sleeptime
        fn = _jpegstreamers[port].filename

        if (not os.path.exists(fn)):
          sleep(interval)
          continue

        if (time.time() - timeout > lasttimeserved or lastmodtime != os.stat(fn).st_mtime):

          if (lastmodtime != os.stat(fn).st_mtime):
            jpgfile = open(fn)
            jpgdata = jpgfile.read() 
            jpgfile.close()
            lastmodtime = os.stat(fn).st_mtime

          try:
            self.wfile.write("--BOUNDARYSTRING\r\n")
            self.send_header("Content-type","image/jpeg")
            self.send_header("Content-Length", str(len(jpgdata)))
            self.end_headers()
            self.wfile.write(jpgdata + "\r\n")
          except socket.error, e:
            return
          except IOError, e:
            return
          lasttimeserved = time.time()
          count = count + 1 
        time.sleep(interval)


class JpegTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
  allow_reuse_address = True

#factory class for jpegtcpservers
class JpegStreamer():
  server = ""
  host = ""
  port = ""
  filename = ""
  sleeptime = ""

  def __init__(self, hostandport = 8080, fn = "", st=0.1 ):
    if (type(hostandport) == int):
      self.port = hostandport
    elif (type(hostandport) == tuple):
      (self.host, self.port) = hostandport 

    if not fn:
      fn = os.tmpnam() + ".jpg"
    self.filename = fn
    self.sleeptime = st
    
    self.server = JpegTCPServer((self.host, self.port), JpegStreamHandler)
    self.server_thread = threading.Thread(target = self.server.serve_forever)
    self.server_thread.setDaemon(True)
    self.server_thread.start()
    _jpegstreamers[self.port] = self 

if __name__ == '__main__':
    sys.exit(
        load_entry_point('ipython==0.10.2', 'console_scripts', 'ipython')()
    )

