# SimpleCV Cameras & Devices

#load system libraries
from .base import *
from .ImageClass import Image 

#Globals
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
        _camera_polling_thread.daemon = True
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
    self.camthread.daemon = True
    self.camthread.start()

  def getImage(self):
    """
Return the current frame of the JpegStream being monitored
    """
    return Image(pil.open(StringIO(self.camthread.currentframe)))



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
    self.server_thread.daemon = True
    self.server_thread.start()
