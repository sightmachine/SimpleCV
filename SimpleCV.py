#!/usr/bin/python

#system includes
import sys

#necessary for Ubuntu 10.4 cross-compatability
sys.path.append('/usr/share/pyshared/opencv')
sys.path.append('/usr/lib/pyshared/python2.6/opencv')

#library includes
import cv


#camera class, wrappers the cvCapture class and associated methods
class Camera:
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
  def __init__(self, camera_index, prop_set = {}):
    self.capture = cv.CaptureFromCAM(camera_index)

    if (not self.capture):
      return false

    #set any properties in the constructor
    for p in prop_set.keys():
      if p in self.prop_map:
        cv.SetCaptureProperty(self.capture, self.prop_map[p], prop_set[p])

    
  #todo -- make these dynamic attributes of the Camera class
  def getProperty(self, prop):
    if prop in self.prop_map:
      return cv.GetCaptureProperty(self.capture, self.prop_map[prop]);
    return false 

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
  _buffer_frames = [] #frame buffers for memory-intensive transforms

  #initialize the frame
  #parameters: source designation (filename)
  #todo: handle camera/capture from file cases (detect on file extension)
  def __init__(self, source):

    if (type(source) == cv.cvmat):
      self._matrix = source 

    if (type(source) == cv.iplimage):
      self._bitmap = source

    if (type(source) == type(str())):
      self.filename = source
      self._bitmap = cv.LoadImage(self.filename, iscolor=cv.CV_LOAD_IMAGE_UNCHANGED) 

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

  def getGrayscaleBitmap(self):
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

  #scale this image, and return an Image object with the new dimensions 
  def scale(self, width, height):
    scaled_matrix = cv.CreateMat(width, height, self.getMatrix().type)
    cv.Resize(self.getMatrix(), scaled_matrix)
    return Image(scaled_matrix)

  def findCorners(self, max = 50):

    #initialize buffer frames
    eig_image = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_32F, 1)
    temp_image = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_32F, 1)

    corner_coordinates = cv.GoodFeaturesToTrack(self.getGrayscaleBitmap(), eig_image, temp_image, max, 0.04, 1.0, None)

    corner_features = []   
    for (x,y) in corner_coordinates:
      corner_features.append(Corner(self, x, y))

    return FeatureSet(corner_features)
      
  def drawCircle(self, at_x, at_y, rad, color, thickness = 1):
    cv.Circle(self.getMatrix(), (at_x, at_y), rad, color, thickness)
    self._clearbuffers()

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
      self._clearbuffers()


  def _clearbuffers(self):
    self._bitmap = ""
    self._graymatrix = ""
    self._buffer_frames = []


class FeatureSet:
  features = ()

  def __init__(self, f):
    self.features = f

  def draw(self, color = (255.0,0,0)):
    for f in self.features:
      f.draw(color) 

  def __len__(self):
    return len(self.features)

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

  def draw(self, color = (255.0, 0.0, 0.0)):
    self.image.drawCircle(self.x, self.y, 4, color)
 


#stubbing out blon interface
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
