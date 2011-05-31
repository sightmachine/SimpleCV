#!/usr/bin/python

#system includes
import os, sys, warnings, time, socket, re, urllib2, types
import SocketServer
import threading
from copy import copy
from math import sqrt, atan2
from pkg_resources import load_entry_point
from SimpleHTTPServer import SimpleHTTPRequestHandler
from types import IntType, LongType, FloatType, InstanceType
from cStringIO import StringIO

#couple quick typecheck helper functions
def is_number(n):
  return n in (IntType, LongType, FloatType)

def is_tuple(n):
  return type(n) == tuple 

def reverse_tuple(n):
  return tuple(reversed(n))


#library includes
import cv
import numpy as np
import scipy.spatial.distance as spsd
from numpy import linspace 
from scipy.interpolate import UnivariateSpline

"""
A color spline class for performing color correction. This class basically wraps 
the scipy.interpolate.UnivariateSpline. We use the spline for external modifications
while the internal repsentation is a linear array with 256 elements from 0 to 256
"""
class ColorCurve:
  mCurve =""
  def __init__(self, curve_vals ):
    inBins = linspace(0,255,256)
    if( type(curve_vals) == np.ndarray ):
      aSpline = UnivariateSpline( curve_vals[:,0],curve_vals[:,1],s=1)   
      self.mCurve = aSpline(inBins)
    elif( type(curve_vals) == UnivariateSpline ):
      self.mCurve = curvVals(inBins)
  
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

FREENECT_ENABLED = True
try:
  import freenect
except ImportError:
  FREENECT_ENABLED = False 


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
   
class Kinect(FrameSource):
  """
    This is an experimental wrapper for the Freenect python libraries
    you can getImage() and getDepth() for separate channel images
  """
  def __init__(self):
    if not FREENECT_ENABLED:
      warnings.warn("You don't seem to have the freenect library installed.  This will make it hard to use a Kinect.")

  #this code was borrowed from
  #https://github.com/amiller/libfreenect-goodies
  def getImage(self):
    video = freenect.sync_get_video()[0]
    video = video[:, :, ::-1]  # RGB -> BGR
    image = cv.CreateImageHeader((video.shape[1], video.shape[0]), cv.IPL_DEPTH_8U, 3)
    cv.SetData(image, video.tostring(),
               video.dtype.itemsize * 3 * video.shape[1])
    return Image(image)

  def getDepth(self):
    depth = freenect.sync_get_depth()[0]
    np.clip(depth, 0, 2**10 - 1, depth)
    depth >>= 2
    depth = depth.astype(np.uint8)

    image = cv.CreateImageHeader((depth.shape[1], depth.shape[0]),
                                 cv.IPL_DEPTH_8U, 1)

    cv.SetData(image, depth.tostring(), depth.dtype.itemsize * depth.shape[1])
    return Image(image) 


class JpegStreamReader(threading.Thread):
  #threaded class for pulling down JPEG streams and breaking up the images
  url = ""
  currentframe = ""

  def run(self):
    f = urllib2.urlopen(self.url)
    headers = f.info()
    if (headers.has_key("content-type")):
      headers['Content-type'] = headers['content-type'] #force ucase first char

    if not headers.has_key("Content-type"):
      warnings.warn("Tried to load a JpegStream from " + self.url + ", but didn't find a content-type header!")
      return

    (multipart, boundary) = headers['Content-type'].split("boundary=")
    if not re.search("multipart", multipart, re.I):
      warnings.warn("Tried to load a JpegStream from " + self.url + ", but the content type header was " + multipart + " not multipart/replace!")
      return 

    buff = ''
    data = f.readline().strip()
    length = 0 
    contenttype = "jpeg"

    #the first frame contains a boundarystring and some header info
    while (1):
      if (data.strip() == boundary and len(buff)):
        #we have a full jpeg in buffer.  Convert to an image  
        self.currentframe = buff 
        buff = ''

      if (re.match("Content-Type", data, re.I)):
        #set the content type, if provided (default to jpeg)
        (header, typestring) = data.split(":")
        (junk, contenttype) = typestring.strip().split("/")

      if (re.match("Content-Length", data, re.I)):
        #once we have the content length, we know how far to go jfif
        (header, length) = data.split(":")
        length = int(length.strip())
         
      if (re.search("JFIF", data, re.I)):
        # we have reached the start of the image  
        buff = '' 
        if length:
          buff += data + f.read(length - len(buff)) #read the remainder of the image
        else:
          while (not re.search(boundary, data)):
            buff += data 
            data = f.readline()

          endimg, junk = data.split(boundary) 
          buff += endimg
          data = boundary
          continue
        
          

      data = f.readline() #load the next (header) line
      time.sleep(0) #let the other threads go

class JpegStreamCamera(FrameSource):
  """
The JpegStreamCamera takes a URL of a JPEG stream and treats it like a camera.  The current frame can always be accessed with getImage() 

Requires the [Python Imaging Library](http://www.pythonware.com/library/pil/handbook/index.htm)
  """
  url = ""
  camthread = ""
  
  def __init__(self, url):
    if not PIL_ENABLED:
      warnings.warn("You need the Python Image Library (PIL) to use the JpegStreamCamera")
      return

    self.url = url
    self.camthread = JpegStreamReader()
    self.camthread.url = self.url
    self.camthread.start()

  def getImage(self):
    """
Return the current frame of the JpegStream being monitored
    """
    return Image(pil.open(StringIO(self.camthread.currentframe)))



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
  filehandle = "" #filehandle if used

  _barcodeReader = "" #property for the ZXing barcode reader

  #these are buffer frames for various operations on the image
  _bitmap = ""  #the bitmap (iplimage)  representation of the image
  _matrix = ""  #the matrix (cvmat) representation
  _grayMatrix = "" #the gray scale (cvmat) representation -KAS
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
    "_grayMatrix": "",
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
      if (source.nChannels == 1):
        self._bitmap = cv.CreateImage(cv.GetSize(source), cv.IPL_DEPTH_8U, 3) 
        cv.Merge(source, source, source, None, self._bitmap)
      else:
        self._bitmap = source
    elif (type(source) == type(str()) and source != ''):
      self.filename = source
      self._bitmap = cv.LoadImage(self.filename, iscolor=cv.CV_LOAD_IMAGE_COLOR) 
    elif (PIL_ENABLED and source.__class__.__name__ == "JpegImageFile"):
      self._pil = source
      #from the opencv cookbook 
      #http://opencv.willowgarage.com/documentation/python/cookbook.html
      self._bitmap = cv.CreateImageHeader(self._pil.size, cv.IPL_DEPTH_8U, 3)
      cv.SetData(self._bitmap, self._pil.tostring())
      #self._bitmap = cv.iplimage(self._bitmap)
    else:
      return None 

    bm = self.getBitmap()
    self.width = bm.width
    self.height = bm.height
    self.depth = bm.depth
 
  def getEmpty(self, channels = 3):
    """
Create a new, empty OpenCV bitmap with the specified number of channels (default 3)h
    """
    return cv.CreateImage(self.size(), cv.IPL_DEPTH_8U, channels)

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
      rgbbitmap = self.getEmpty()
      cv.CvtColor(self.getBitmap(), rgbbitmap, cv.CV_BGR2RGB)
      self._pil = pil.fromstring("RGB", self.size(), rgbbitmap.tostring())
    return self._pil

  def _getGrayscaleBitmap(self):
    if (self._graybitmap):
      return self._graybitmap

    self._graybitmap = self.getEmpty(1) 
    cv.CvtColor(self.getBitmap(), self._graybitmap, cv.CV_BGR2GRAY) 
    return self._graybitmap

  def getGrayscaleMatrix(self):
   """
   Returns the intensity grayscale matrix
   """
   if (self._grayMatrix):
     return self._grayMatrix
   else:
     self._grayMatrix = cv.GetMat(self._getGrayscaleBitmap()) #convert the bitmap to a matrix
     return self._grayMatrix
    
  def _getEqualizedGrayscaleBitmap(self):

    if (self._equalizedgraybitmap):
      return self._equalizedgraybitmap

    self._equalizedgraybitmap = self.getEmpty(1) 
    cv.EqualizeHist(self._getGrayscaleBitmap(), self._equalizedgraybitmap)

    return self._equalizedgraybitmap
    
  def save(self, filehandle_or_filename="", mode=""):
    """
    Save the image to the specified filename.  If no filename is provided then
    then it will use the filename the Image was loaded from or the last
    place it was saved to. 
    """
    if (not filehandle_or_filename):
      if (self.filename):
        filehandle_or_filename = self.filename
      else:
        filehandle_or_filename = self.filehandle


    if (type(filehandle_or_filename) != str):
      fh = filehandle_or_filename

      if (not PIL_ENABLED):
        warnings.warn("You need the python image library to save by filehandle")
        return 0

      if (type(fh) == InstanceType and fh.__class__.__name__ == "JpegStreamer"):
        fh = fh.framebuffer
      
      if (not mode):
        mode = "jpeg"

      try:
        self.getPIL().save(fh, mode)
        self.filehandle = fh #set the filename for future save operations
        self.filename = ""
        
      except:
        return 0

      return 1

    filename = filehandle_or_filename 
    if (filename):
      cv.SaveImage(filename, self.getBitmap())  
      self.filename = filename #set the filename for future save operations
      self.filehandle = ""
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
    newimg = self.getEmpty() 
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

    Returns: greyscale image.
    """
    win_x = 3
    win_y = 3  #set the default aperature window size (3x3)

    if (is_tuple(aperature)):
      win_x, win_y = aperature#get the coordinates from parameter
      #TODO: make sure aperature is valid 
      #   eg Positive, odd and square for bilateral and median

    algorithm = cv.CV_GAUSSIAN #default algorithm is gaussian 

    #gauss and blur can work in-place, others need a buffer frame
    #use a string to ID rather than the openCV constant
    if algorithm_name == "blur":
      algorithm = cv.CV_BLUR
    if algorithm_name == "bilateral":
      algorithm = cv.CV_BILATERAL
      win_y = win_x #aperature must be square
    if algorithm_name == "median":
      algorithm = cv.CV_MEDIAN
      win_y = win_x #aperature must be square

    newimg = self.getEmpty(1) 
    cv.Smooth(self._getGrayscaleBitmap(), newimg, algorithm, win_x, win_y, sigma, spatial_sigma)

    return Image(newimg)

  def invert(self):
    """
    Invert (negative) the image note that this can also be done with the
    unary minus (-) operator. 
    """
    return -self 

  def grayscale(self):
    """
    return a gray scale version of the image
    """
    return Image(self._getGrayscaleBitmap())

  def flipHorizontal(self):
    """
    return a horizontally mirrored image
    """
    newimg = self.getEmpty()
    cv.Flip(self.getBitmap(), newimg, 1)
    return Image(newimg) 

  def flipVertical(self):
    """
    return a vertically mirrored image
    """
    newimg = self.getEmpty()
    cv.Flip(self.getBitmap(), newimg, 0)
    return Image(newimg) 
    
    
    
  def stretch(self, thresh_low = 0, thresh_high = 255):
    """
    Returns greyscale image
    
    The stretch filter works on a greyscale image, if the image
    is color, it returns a greyscale image.  The filter works by
    taking in a lower and upper threshold.  Anything below the lower
    threshold is pushed to black (0) and anything above the upper
    threshold is pushed to white (255)
    """
    try:
      newimg = self.getEmpty() 
      cv.Threshold(self._getGrayscaleBitmap(), newimg, thresh_low, thresh_high, cv.CV_THRESH_TRUNC)
      return Image(newimg)
    except e:
      return None
      
  def binarize(self, thresh = 127):
    """
    Do a binary threshold the image, changing all values above thresh to white
    and all below to black.  If a color tuple is provided, each color channel
    is thresholded separately.
    """
    if (is_tuple(thresh)):
      r = self.getEmpty(1) 
      g = self.getEmpty(1)
      b = self.getEmpty(1)
      cv.Split(self.getBitmap(), b, g, r, None)

      cv.Threshold(r, r, thresh[0], 255, cv.CV_THRESH_BINARY)
      cv.Threshold(g, g, thresh[1], 255, cv.CV_THRESH_BINARY)
      cv.Threshold(b, b, thresh[2], 255, cv.CV_THRESH_BINARY)

      cv.Add(r, g, r)
      cv.Add(r, b, r)
      
      return Image(r)

    else:
      newbitmap = self.getEmpty(1) 
      #desaturate the image, and apply the new threshold          
      cv.Threshold(self._getGrayscaleBitmap(), newbitmap, thresh, 255, cv.CV_THRESH_BINARY)
      return Image(newbitmap)
  

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
    grey = self.getEmpty(1) 
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
    * the scaling factor for subsequent rounds of the haar cascade (default 1.2)7
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
    objects = cv.HaarDetectObjects(self._getEqualizedGrayscaleBitmap(), cascade, storage, scale_factors, use_canny, (0,0))
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
    cv.Circle(self.getBitmap(), (int(ctr[0]), int(ctr[1])), rad, reverse_tuple(color), thickness)
    self._clearBuffers("_bitmap")

  def drawLine(self, pt1, pt2, color = (0,0,0), thickness = 1):
    """
    Draw a line on the Image, parameters include
    * pt1 - the first point for the line (tuple)
    * pt1 - the second point on the line (tuple)
    * a color tuple (default black)
    * thickness of the line 
 
    Note that this modifies the image in-place and clears all buffers.
    """
    pt1 = (int(pt1[0]), int(pt1[1]))
    pt2 = (int(pt2[0]), int(pt2[1]))
    cv.Line(self.getBitmap(), pt1, pt2, reverse_tuple(color), thickness, cv.CV_AA) 

  def size(self):
    """
    Return the width and height as a tuple
    """
    return cv.GetSize(self.getBitmap())

  def splitChannels(self, grayscale = True):
    """
    Split the channels of an image into RGB (not the default BGR)
    single parameter is whether to return the channels as grey images (default)
    or to return them as tinted color image 

    returns: tuple of 3 image objects
    """
    r = self.getEmpty(1) 
    g = self.getEmpty(1) 
    b = self.getEmpty(1) 
    cv.Split(self.getBitmap(), b, g, r, None)

    red = self.getEmpty() 
    green = self.getEmpty() 
    blue = self.getEmpty() 
	
    if (grayscale):
      cv.Merge(r, r, r, None, red)
      cv.Merge(g, g, g, None, green)
      cv.Merge(b, b, b, None, blue)
    else:
      cv.Merge(None, None, r, None, red)
      cv.Merge(None, g, None, None, green)
      cv.Merge(b, None, None, None, blue)

    return (Image(red), Image(green), Image(blue)) 

  def applyHLSCurve(self, hCurve, lCurve, sCurve):
    """
    Apply a curve correction in HSL space
    Do BGR->HLS conversion
    Apply correction, curve values of 1 get no change
    Convert back to RGB space
    Return new image, original is unchanged
    The curve should be a floating point array of length 256
  
    TODO CHECK ROI
    TODO CHECK CURVE SIZE
    TODO CHECK COLORSPACE
    """
    temp  = cv.CreateImage(self.size(), 8, 3)
    #Move to HLS space
    cv.CvtColor(self._bitmap,temp,cv.CV_RGB2HLS)
    tempMat = cv.GetMat(temp) #convert the bitmap to a matrix
    #now apply the color curve correction
    tempMat = np.array(self.getMatrix()).copy()
    tempMat[:,:,0] = np.take(hCurve.mCurve,tempMat[:,:,0])
    tempMat[:,:,1] = np.take(sCurve.mCurve,tempMat[:,:,1])
    tempMat[:,:,2] = np.take(lCurve.mCurve,tempMat[:,:,2])
    #Now we jimmy the np array into a cvMat
    image = cv.CreateImageHeader((tempMat.shape[1], tempMat.shape[0]), cv.IPL_DEPTH_8U, 3)
    cv.SetData(image, tempMat.tostring(), tempMat.dtype.itemsize * 3 * tempMat.shape[1])
    cv.CvtColor(image,image,cv.CV_HLS2RGB)  
    return Image(image)

  def applyRGBCurve(self, rCurve, gCurve, bCurve):
    """
    Apply correction, curve values of 1 get no change
    Return new image, original is unchanged
    The curve should be a floating point array of length 256
    """
    tempMat = np.array(self.getMatrix()).copy()
    tempMat[:,:,0] = np.take(bCurve.mCurve,tempMat[:,:,0])
    tempMat[:,:,1] = np.take(gCurve.mCurve,tempMat[:,:,1])
    tempMat[:,:,2] = np.take(rCurve.mCurve,tempMat[:,:,2])
    #Now we jimmy the np array into a cvMat
    image = cv.CreateImageHeader((tempMat.shape[1], tempMat.shape[0]), cv.IPL_DEPTH_8U, 3)
    cv.SetData(image, tempMat.tostring(), tempMat.dtype.itemsize * 3 * tempMat.shape[1])
    return Image(image)

  def applyIntensityCurve(self, curve):
    """
    Apply correction, curve values of 1 get no change
    Return new grayscale image, original is unchanged
    The curve should be a floating point array of length 256
    """
    tempMat = np.array(self.getGrayscaleMatrix()).copy()
    tempMat[:,:] = np.take(curve.mCurve,tempMat[:,:])
    #Now we jimmy the np array into a cvMat
    image = cv.CreateImageHeader((tempMat.shape[1], tempMat.shape[0]), cv.IPL_DEPTH_8U, 1)
    cv.SetData(image, tempMat.tostring(), tempMat.dtype.itemsize * 1 * tempMat.shape[1])
    return Image(image);
      
  def histogram(self, numbins = 50):
    """
    Return a numpy array of the 1D histogram of intensity for pixels in the image
    Single parameter is how many "bins" to have.
    """
    gray = self._getGrayscaleBitmap()

    (hist, bin_edges) = np.histogram(np.asarray(cv.GetMat(gray)), bins=numbins)
    return hist.tolist()

  def __getitem__(self, coord):
    ret = self.getMatrix()[tuple(reversed(coord))]
    if (type(ret) == cv.cvmat):
      (width, height) = cv.GetSize(ret)
      newmat = cv.CreateMat(height, width, ret.type)
      cv.Copy(ret, newmat) #this seems to be a bug in opencv
      #if you don't copy the matrix slice, when you convert to bmp you get
      #a slice-sized hunk starting at 0,0
      return Image(newmat)
    return tuple(reversed(ret))

  def __setitem__(self, coord, value):
    value = tuple(reversed(value))  #RGB -> BGR
    if (is_tuple(self.getMatrix()[tuple(reversed(coord))])):
      self.getMatrix()[coord] = value 
    else:
      cv.Set(self.getMatrix()[tuple(reversed(coord))], value)
      self._clearBuffers("_matrix") 

  def __sub__(self, other):
    newbitmap = self.getEmpty() 
    if is_number(other):
      cv.SubS(self.getBitmap(), other, newbitmap)
    else:
      cv.Sub(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def __add__(self, other):
    newbitmap = self.getEmpty() 
    if is_number(other):
      cv.AddS(self.getBitmap(), other, newbitmap)
    else:
      cv.Add(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def __and__(self, other):
    newbitmap = self.getEmpty() 
    if is_number(other):
      cv.AndS(self.getBitmap(), other, newbitmap)
    else:
      cv.And(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def __or__(self, other):
    newbitmap = self.getEmpty() 
    if is_number(other):
      cv.OrS(self.getBitmap(), other, newbitmap)
    else:
      cv.Or(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def __div__(self, other):
    newbitmap = self.getEmpty() 
    cv.Div(self.getBitmap(), other.getBitmap(), newbitmap)
    return Image(newbitmap)

  def __pow__(self, other):
    newbitmap = self.getEmpty() 
    cv.Pow(self.getBitmap(), newbitmap, other)
    return Image(newbitmap)

  def __neg__(self):
    newbitmap = self.getEmpty() 
    cv.Not(self.getBitmap(), newbitmap)
    return Image(newbitmap)

  def max(self, other):
    """
    Return the maximum value of my image, and the other image, in each channel
    If other is a number, returns the maximum of that and the number
    """ 
    newbitmap = self.getEmpty() 
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
    newbitmap = self.getEmpty() 
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
  def findLines(self, threshold=80, minlinelength=30, maxlinegap=10, cannyh1=50, cannyth2=100):
    """
    findLines will find line segments in your image and returns Line feature 
    objects in a FeatureSet. The parameters are:
    * threshold, which determies the minimum "strength" of the line
    * min line length -- how many pixels long the line must be to be returned
    * max line gap -- how much gap is allowed between line segments to consider them the same line 
    * cannyth1 and cannyth2 are thresholds used in the edge detection step, refer to _getEdgeMap() for details

    For more information, consult the cv.HoughLines2 documentation
    """
    em = self._getEdgeMap(cannyth1, cannyth2)
    
    lines = cv.HoughLines2(em, cv.CreateMemStorage(), cv.CV_HOUGH_PROBABILISTIC, 1.0, cv.CV_PI/180.0, threshold, minlinelength, maxlinegap)

    linesFS = FeatureSet()
    for l in lines:
      linesFS.append(Line(self, l))  
    
    return linesFS

  def edges(self, t1=50, t2=100):
    return Image(self._getEdgeMap(t1, t2))

  def _getEdgeMap(self, t1=50, t2=100):
    """
    Return the binary bitmap which shows where edges are in the image.  The two
    parameters determine how much change in the image determines an edge, 
    and how edges are linked together.  For more information refer to:

    http://en.wikipedia.org/wiki/Canny_edge_detector
    http://opencv.willowgarage.com/documentation/python/imgproc_feature_detection.html?highlight=canny#Canny
    """ 
  
    if (self._edgeMap and self._cannyparam[0] == t1 and self._cannyparam[1] == t2):
      return self._edgeMap

    self._edgeMap = self.getEmpty(1) 
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

  def __init__(self, i, at_x, at_y):
    self.x = at_x
    self.y = at_y
    self.image = i

  def coordinates(self):
    """
    Return a an array of x,y
    """
    return np.array([self.x, self.y])  

  def draw(self, color = (255.0,0.0,0.0)):
    """
    With no dimension information, color the x,y point for the featuer 
    """
    self.image[self.x,self.y] = color

  def distanceFrom(self, point = (-1,-1)): 
    """
    Given a point (default to center of the image), return the euclidean distance of x,y from this point
    """
    if (point[0] == -1 or point[1] == -1):
      point = np.array(self.image.size())/2
    return spsd.euclidean(point, [self.x, self.y]) 

  def meanColor(self):
    """
      Return the color tuple from x,y
    """
    return self.image[self.x, self.y]

  def colorDistance(self, color = (0,0,0)): 
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
    self.image = i
    self.cvblob = cb
    (self.x, self.y) = cvb.Centroid(cb)

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
    return cvb.Angle(self.cvblob)

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
  points = ()

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
    return atan2(d_y, d_x) #zero is west 

class Barcode(Feature):
  """
  The Barcode Feature wrappers the object returned by findBarcode(), a python-zxing object.

  - The x,y coordinate is the center of the code
  - points represents the four boundary points of the feature.  Note: for QR codes, these points are the reference rectangles, and are quadrangular, rather than rectangular with other datamatrix types. 
  - data is the parsed data of the code
  """
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
  points = ()
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
    if (self.width > self.height):
      return 0
    else:
      return np.pi / 2 


#TODO?
#class Edge(Feature):
#class Ridge(Feature):


_jpegstreamers = {}
class JpegStreamHandler(SimpleHTTPRequestHandler):
  """
  The JpegStreamHandler handles requests to the threaded HTTP server.
  Once initialized, any request to this port will receive a multipart/replace
  jpeg.   
  """

  def do_GET(self):
    global _jpegstreamers

    if (self.path == "/" or not self.path):

      self.send_response(200)
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write("""
<html>
<head>
<style type=text/css>
  body { background-image: url(/stream); background-repeat:no-repeat; background-position:center top; background-attachment:fixed; background-size: 100% , auto; }
</style>
</head>
<body>
&nbsp;
</body>
</html>
      """)
    else:
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
      jpgdata = ""
      while (1):
        interval = _jpegstreamers[port].sleeptime
  
        if (time.time() - timeout > lasttimeserved or jpgdata != _jpegstreamers[port].framebuffer.getvalue()):
  
          jpgdata = _jpegstreamers[port].framebuffer.getvalue()
          _jpegstreamers[port].framebuffer = StringIO()
  
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
  """
  The JpegStreamer class allows the user to stream a jpeg encoded file
  to a HTTP port.  Any updates to the jpg file will automatically be pushed
  to the browser via multipart/replace content type.

  To initialize:
  js = JpegStreamer()

  to update:
  img.save(js)

  Note 3 optional parameters on the constructor:
  - port (default 8080) which sets the TCP port you need to connect to
  - sleep time (default 0.1) how often to update.  Above 1 second seems to cause dropped connections in Google chrome

  Once initialized, the buffer and sleeptime can be modified and will function properly -- port will not.
  """
  server = ""
  host = ""
  port = ""
  sleeptime = ""
  framebuffer = StringIO()

  def __init__(self, hostandport = 8080, st=0.1 ):
    global _jpegstreamers
    if (type(hostandport) == int):
      self.port = hostandport
    elif (type(hostandport) == tuple):
      (self.host, self.port) = hostandport 

    self.sleeptime = st
    
    self.server = JpegTCPServer((self.host, self.port), JpegStreamHandler)
    self.server_thread = threading.Thread(target = self.server.serve_forever)
    _jpegstreamers[self.port] = self
    self.server_thread.start()


"""
If you run SimpleCV directly, it will launch an ipython shell
"""
if __name__ == '__main__':
    sys.exit(
        #load_entry_point('ipython==0.10.2', 'console_scripts', 'ipython')()
    )

