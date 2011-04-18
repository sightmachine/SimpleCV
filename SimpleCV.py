#!/usr/bin/python

#system includes
import sys

#library includes
import cv
import numpy as np


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

  _bitmap = ""  #the bitmap (iplimage)  representation of the image
  _matrix = ""  #the matrix (cvmat) representation
  _graybitmap = ""  #the matrix (cvmat) representation

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
  def smooth(self, algorithm_name = '', aperature = '', sigma = 0, spatial_sigma = 0):
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
    self._clearBuffers()

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

      
  def drawCircle(self, at_x, at_y, rad, color, thickness = 1):
    cv.Circle(self.getMatrix(), (int(at_x), int(at_y)), rad, color, thickness)
    self._clearBuffers()

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
      self._clearBuffers() 

  def _clearBuffers(self):
    self._bitmap = ""
    self._graybitmap = ""


class FeatureSet:
  features = ()

  def __init__(self, f):
    self.features = f

  def draw(self, color = (255,0,0)):
    for f in self.features:
      f.draw(color) 

  def coordinates(self):
    ar = [] 
    for f in self.features:
      ar.append([f.x, f.y]) 

    return np.array(ar)

  def __len__(self):
    return len(self.features)

  def __getitem__(self, index):
    return self.features[index]

class Feature(object):
  x = 0.0
  y = 0.0 
  image = "" #parent image

  def __init__(self, i, at_x, at_y):
    self.x = at_x
    self.y = at_y
    self.image = i

  def draw(self, color = (255.0,0.0,0.0)):
    self.image[x,y] = color

class Corner(Feature):
  direction = 0.0   #direction of the  

  def __init__(self, i, at_x, at_y):
    super(Corner, self).__init__(i, at_x, at_y)
    #can we look at the eigenbuffer and find direction?

  def draw(self, color = (255, 0, 0)):
    self.image.drawCircle(self.x, self.y, 4, color)
 


#stubbing out blob interface
class Blob(Feature):
  cblob = ""
  
  def __init__(i, cb): 
    cblob = cb

  def radius():
    return 

  def boundingBox():
    return

  def area():
    return cblob.Area()  

  def meanColor():
    return cblob.getMeanColor()

#class Edge(Feature):


#class Ridge(Feature):





def main(argv):
  print "hello world"   

if (__name__ == "__main__"):
  main(sys.argv)
