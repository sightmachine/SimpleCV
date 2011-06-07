#!/usr/bin/python

# SimpleCV Image Object

#load required libraries
from __init__ import *
from Detection import *

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
    except:
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
Returns an image with 3 ColorCurve corrections applied in HSL space
Parameters are: 
 * Hue ColorCurve 
 * Lightness (brightness/value) ColorCurve
 * Saturation ColorCurve
    """
  
    #TODO CHECK ROI
    #TODO CHECK CURVE SIZE
    #TODO CHECK COLORSPACE
    #TODO CHECK CURVE SIZE
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
Returns an image with 3 ColorCurve corrections applied in rgb channels 
Parameters are: 
 * Red ColorCurve 
 * Green ColorCurve
 * Blue ColorCurve
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
Return an image with ColorCurve curve applied to all three color channels
    """
    return self.applyRGBCurve(curve, curve, curve)
      
  def erode(self, iterations=1):
    """
    Apply a morphological erosion. An erosion has the effect of removing small bits of noise
    and smothing blobs. 
    This implementation uses the default openCV 3X3 square kernel 
    Erosion is effectively a local minima detector, the kernel moves over the image and
    takes the minimum value inside the kernel. 
    iterations - this parameters is the number of times to apply/reapply the operation
    See: http://en.wikipedia.org/wiki/Erosion_(morphology).
    See: http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-erode 
    Example Use: A threshold/blob image has 'salt and pepper' noise. 
    Example Code: ./examples/MorphologyExample.py
    """
    retVal = self.getEmpty() 
    kern = cv.CreateStructuringElementEx(3,3,1,1,cv.CV_SHAPE_RECT)
    cv.Erode(self.getBitmap(),retVal,kern,iterations)
    return( Image(retVal) )

  def dilate(self, iterations=1):
    """
    Apply a morphological dilation. An dilation has the effect of smoothing blobs while
    intensifying the amount of noise blobs. 
    This implementation uses the default openCV 3X3 square kernel 
    Erosion is effectively a local maxima detector, the kernel moves over the image and
    takes the maxima value inside the kernel. 

    iterations - this parameters is the number of times to apply/reapply the operation

    See: http://en.wikipedia.org/wiki/Dilation_(morphology)
    See: http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-dilate
    Example Use: A part's blob needs to be smoother 
    Example Code: ./examples/MorphologyExample.py
    """
    retVal = self.getEmpty() 
    kern = cv.CreateStructuringElementEx(3,3,1,1,cv.CV_SHAPE_RECT)
    cv.Dilate(self.getBitmap(),retVal,kern,iterations)
    return( Image(retVal) )

  def morphOpen(self):
    """
    morphologyOpen applies a morphological open operation which is effectively
    an erosion operation followed by a morphological dilation. This operation
    helps to 'break apart' or 'open' binary regions which are close together. 

    See: http://en.wikipedia.org/wiki/Opening_(morphology)
    See: http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-morphologyex
    Example Use: two part blobs are 'sticking' together.
    Example Code: ./examples/MorphologyExample.py 
    """
    retVal = self.getEmpty() 
    temp = self.getEmpty()
    kern = cv.CreateStructuringElementEx(3,3,1,1,cv.CV_SHAPE_RECT)
    cv.MorphologyEx(self.getBitmap(),retVal,temp,kern,cv.MORPH_OPEN,1)
    return( Image(retVal) )


  def morphClose(self):
    """
    morphologyClose applies a morphological close operation which is effectively
    a dilation operation followed by a morphological erosion. This operation
    helps to 'bring together' or 'close' binary regions which are close together. 

    See: http://en.wikipedia.org/wiki/Closing_(morphology)
    See: http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-morphologyex
    Example Use: Use when a part, which should be one blob is really two blobs.   
    Example Code: ./examples/MorphologyExample.py
    """
    retVal = self.getEmpty() 
    temp = self.getEmpty()
    kern = cv.CreateStructuringElementEx(3,3,1,1,cv.CV_SHAPE_RECT)
    cv.MorphologyEx(self.getBitmap(),retVal,temp,kern,cv.MORPH_CLOSE,1)
    return( Image(retVal) )

  def morphGradient(self):
    """
    The morphological gradient is the difference betwen the morphological
    dilation and the morphological gradient. This operation extracts the 
    edges of a blobs in the image. 

    See: http://en.wikipedia.org/wiki/Morphological_Gradient
    See: http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-morphologyex
    Example Use: Use when you have blobs but you really just want to know the blob edges.
    Example Code: ./examples/MorphologyExample.py
    """
    retVal = self.getEmpty() 
    retVal = self.getEmpty() 
    temp = self.getEmpty()
    kern = cv.CreateStructuringElementEx(3,3,1,1,cv.CV_SHAPE_RECT)
    cv.MorphologyEx(self.getBitmap(),retVal,temp,kern,cv.MORPH_GRADIENT,1)
    return( Image(retVal) )

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
  def findLines(self, threshold=80, minlinelength=30, maxlinegap=10, cannyth1=50, cannyth2=100):
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
