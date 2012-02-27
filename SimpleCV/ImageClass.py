#load required libraries
from SimpleCV.base import *
from SimpleCV.Color import *
from numpy import int32
from numpy import uint8
import pygame as pg
import scipy.ndimage as ndimage
import scipy.stats.stats as sss  #for auto white balance
import scipy.cluster.vq as scv    
#import cv2 
import math # math... who does that 

class ColorSpace:
    """
    This class is used to encapsulates the color space of a given image.
    This class acts like C/C++ style enumerated type.
    See: http://stackoverflow.com/questions/2122706/detect-color-space-with-opencv
    """
    UNKNOWN = 0
    BGR = 1 
    GRAY = 2
    RGB = 3
    HLS = 4
    HSV = 5
    XYZ  = 6

  
class ImageSet(list):
    """
    This is an abstract class for keeping a list of images.  It has a few
    advantages in that you can use it to auto load data sets from a directory
    or the net.

    Keep in mind it inherits from a list too, so all the functionality a
    normal python list has this will too.

    Example:
    
    >>> imgs = ImageSet()
    >>> imgs.download("ninjas")
    >>> imgs.show(ninjas)

    or you can load a directory path:

    >>> imgs = ImageSet('/path/to/imgs/')
    >>> imgs.show()
    
    This will download and show a bunch of random ninjas.  If you want to
    save all those images locally then just use:

    >>> imgs.save()

    
    """

    def __init__(self, directory = None):
      if directory:
        self.load(directory)

      return

    def download(self, tag=None, number=10):
      """
      This function downloads images from Google Image search based
      on the tag you provide.  The number is the number of images you
      want to have in the list.

      note: This requires the python library Beautiful Soup to be installed
      http://www.crummy.com/software/BeautifulSoup/
      """

      try:
        from BeautifulSoup import BeautifulSoup

      except:
        print "You need to install Beatutiul Soup to use this function"
        print "to install you can use:"
        print "easy_install beautifulsoup"

        return

      opener = urllib2.build_opener()
      opener.addheaders = [('User-agent', 'Mozilla/5.0')]
      url = "http://www.google.com/search?tbm=isch&q=" + str(tag)
      page = opener.open(url)
      soup = BeautifulSoup(page)
      imgs = soup.findAll('img')

      for img in imgs:
        dl_url = str(dict(img.attrs)['src'])

        try:
          add_img = Image(dl_url)
          self.append(add_img)

        except:
          #do nothing
          None
        


    def show(self, showtime = 0.25):
      """
      This is a quick way to show all the items in a ImageSet.
      The time is in seconds. You can also provide a decimal value, so
      showtime can be 1.5, 0.02, etc.
      to show each image.
      """

      for i in self:
        i.show()
        time.sleep(showtime)

    def save(self, verbose = False):
      """
      This is a quick way to save all the images in a data set.

      If you didn't specify a path one will randomly be generated.
      To see the location the files are being saved to then pass
      verbose = True
      """

      for i in self:
        i.save(verbose=verbose)
      
    def showPaths(self):
      """
      This shows the file paths of all the images in the set

      if they haven't been saved to disk then they will not have a filepath
      
      """

      for i in self:
        print i.filename

    def load(self, directory = None, extension = None):
      """
      This function loads up files automatically from the directory you pass
      it.  If you give it an extension it will only load that extension
      otherwise it will try to load all know file types in that directory.

      extension should be in the format:
      extension = 'png'

      Example:

      >>> imgs = ImageSet()
      >>> imgs.load("images/faces")
      >>> imgs.load("images/eyes", "png")

      """

      if not directory:
        print "You need to give a directory to load from"
        return

      if not os.path.exists(directory):
        print "Invalied image path given"
        return
      
      
      if extension:
        extension = "*." + extension
        formats = [os.path.join(directory, extension)]
        
      else:
        formats = [os.path.join(directory, x) for x in IMAGE_FORMATS]
        
      file_set = [glob.glob(p) for p in formats]

      for f in file_set:
        for i in f:
          self.append(Image(i))


      
  
class Image:
    """
    The Image class is the heart of SimpleCV and allows you to convert to and 
    from a number of source types with ease.  It also has intelligent buffer
    management, so that modified copies of the Image required for algorithms
    such as edge detection, etc can be cached and reused when appropriate.


    Image are converted into 8-bit, 3-channel images in RGB colorspace.  It will
    automatically handle conversion from other representations into this
    standard format.  If dimensions are passed, an empty image is created.

    Examples:
    >>> i = Image("/path/to/image.png")
    >>> i = Camera().getImage()


    You can also just load the SimpleCV logo using:
    >>> img = Image("simplecv")
    >>> img = Image("logo")
    >>> img = Image("logo_inverted")
    >>> img = Image("logo_transparent")
    >>> img = Image("barcode")

    Or you can load an image from a URL:
    >>> img = Image("http://www.simplecv.org/image.png")
    """
    width = 0    #width and height in px
    height = 0
    depth = 0
    filename = "" #source filename
    filehandle = "" #filehandle if used
    camera = ""
    _mLayers = []  

    _mDoHuePalette = False
    _mPaletteBins = None
    _mPalette = None
    _mPaletteMembers = None
    _mPalettePercentages = None

    _barcodeReader = "" #property for the ZXing barcode reader


    #these are buffer frames for various operations on the image
    _bitmap = ""  #the bitmap (iplimage)  representation of the image
    _matrix = ""  #the matrix (cvmat) representation
    _grayMatrix = "" #the gray scale (cvmat) representation -KAS
    _graybitmap = ""  #a reusable 8-bit grayscale bitmap
    _equalizedgraybitmap = "" #the above bitmap, normalized
    _blobLabel = ""  #the label image for blobbing
    _edgeMap = "" #holding reference for edge map
    _cannyparam = (0, 0) #parameters that created _edgeMap
    _pil = "" #holds a PIL object in buffer
    _numpy = "" #numpy form buffer
    _grayNumpy = "" # grayscale numpy for keypoint stuff
    _colorSpace = ColorSpace.UNKNOWN #Colorspace Object
    _pgsurface = ""
  

    #Keypoint caching values
    _mKeyPoints = None
    _mKPDescriptors = None
    _mKPFlavor = "NONE"

    #when we empty the buffers, populate with this:
    _initialized_buffers = { 
        "_bitmap": "", 
        "_matrix": "", 
        "_grayMatrix": "",
        "_graybitmap": "", 
        "_equalizedgraybitmap": "",
        "_blobLabel": "",
        "_edgeMap": "",
        "_cannyparam": (0, 0), 
        "_pil": "",
        "_numpy": "",
        "_grayNumpy":"",
        "_pgsurface": ""}  
    
    
    #initialize the frame
    #parameters: source designation (filename)
    #todo: handle camera/capture from file cases (detect on file extension)
    def __init__(self, source = None, camera = None, colorSpace = ColorSpace.UNKNOWN):
        """ 
        The constructor takes a single polymorphic parameter, which it tests
        to see how it should convert into an RGB image.  Supported types include:
    
    
        OpenCV: iplImage and cvMat types
        Python Image Library: Image type
        Filename: All opencv supported types (jpg, png, bmp, gif, etc)
        URL: The source can be a url, but must include the http://
        """
        self._mLayers = []
        self.camera = camera
        self._colorSpace = colorSpace
        #Keypoint Descriptors 
        self._mKeyPoints = []
        self._mKPDescriptors = []
        self._mKPFlavor = "NONE"
        #Pallete Stuff
        self._mDoHuePalette = False
        self._mPaletteBins = None
        self._mPalette = None
        self._mPaletteMembers = None
        self._mPalettePercentages = None

        



        #Check if need to load from URL
        if type(source) == str and (source[:7].lower() == "http://" or source[:8].lower() == "https://"):
            try:
                img_file = urllib2.urlopen(source)
            except:
                print "Couldn't open Image from URL:" + source
                return None

            im = StringIO(img_file.read())
            source = pil.open(im).convert("RGB")

        #This section loads custom built-in images    
        if type(source) == str:
            if source.lower() == "simplecv":
                try:
                    scvImg = pil.fromstring("RGB", (118,118), SIMPLECV)

                except:
                    warnings.warn("Couldn't load Image")
                    return None

                im = StringIO(SIMPLECV)
                source = scvImg

            elif source.lower() == "logo":
                try:
                    scvImg = pil.fromstring("RGB", (64,64), LOGO)

                except:
                    warnings.warn("Couldn't load Image")
                    return None

                im = StringIO(LOGO)
                source = scvImg

            elif source.lower() == "logo_inverted":
                try:
                    scvImg = pil.fromstring("RGB", (64,64), LOGO_INVERTED)

                except:
                    warnings.warn("Couldn't load Image")
                    return None

                im = StringIO(LOGO_INVERTED)
                source = scvImg

            elif source.lower() == "logo_transparent":
                try:
                    scvImg = pil.fromstring("RGB", (64,64), LOGO_TRANSPARENT)

                except:
                    warnings.warn("Couldn't load Image")
                    return None

                im = StringIO(LOGO_TRANSPARENT)
                source = scvImg
            
            elif source.lower() == "lenna":
                try:
                    scvImg = pil.fromstring("RGB", (512, 512), LENNA)
                except:
                    warnings.warn("Couldn't Load Image")
                    return None
                    
                im = StringIO(LENNA)
                source = scvImg
        
        if (type(source) == tuple):
            w = int(source[0])
            h = int(source[1])
            source = cv.CreateImage((w,h), cv.IPL_DEPTH_8U, 3)
            cv.Zero(source)
        if (type(source) == cv.cvmat):
            self._matrix = source
            if((source.step/source.cols)==3): #this is just a guess
                self._colorSpace = ColorSpace.BGR
            elif((source.step/source.cols)==1):
                self._colorSpace = ColorSpace.BGR
            else:
                self._colorSpace = ColorSpace.UNKNOWN


        elif (type(source) == np.ndarray):  #handle a numpy array conversion
            if (type(source[0, 0]) == np.ndarray): #we have a 3 channel array
                #convert to an iplimage bitmap
                source = source.astype(np.uint8)
                self._numpy = source

                invertedsource = source[:, :, ::-1].transpose([1, 0, 2])
                self._bitmap = cv.CreateImageHeader((invertedsource.shape[1], invertedsource.shape[0]), cv.IPL_DEPTH_8U, 3)
                cv.SetData(self._bitmap, invertedsource.tostring(), 
                    invertedsource.dtype.itemsize * 3 * invertedsource.shape[1])
                self._colorSpace = ColorSpace.BGR #this is an educated guess
            else:
                #we have a single channel array, convert to an RGB iplimage

                source = source.astype(np.uint8)
                source = source.transpose([1,0]) #we expect width/height but use col/row
                self._bitmap = cv.CreateImage((source.shape[1], source.shape[0]), cv.IPL_DEPTH_8U, 3) 
                channel = cv.CreateImageHeader((source.shape[1], source.shape[0]), cv.IPL_DEPTH_8U, 1)
                #initialize an empty channel bitmap
                cv.SetData(channel, source.tostring(), 
                    source.dtype.itemsize * source.shape[1])
                cv.Merge(channel, channel, channel, None, self._bitmap)
                self._colorSpace = ColorSpace.BGR


        elif (type(source) == cv.iplimage):
            if (source.nChannels == 1):
                self._bitmap = cv.CreateImage(cv.GetSize(source), cv.IPL_DEPTH_8U, 3) 
                cv.Merge(source, source, source, None, self._bitmap)
                self._colorSpace = ColorSpace.BGR
            else:
                self._bitmap = source
                self._colorSpace = ColorSpace.BGR
        elif (type(source) == type(str())):
            if source == '':
                raise IOError("No filename provided to Image constructor")

            else:
                self.filename = source
                self._bitmap = cv.LoadImage(self.filename, iscolor=cv.CV_LOAD_IMAGE_COLOR)
                #TODO, on IOError fail back to PIL
                self._colorSpace = ColorSpace.BGR
    
    
        elif (type(source) == pg.Surface):
            self._pgsurface = source
            self._bitmap = cv.CreateImageHeader(self._pgsurface.get_size(), cv.IPL_DEPTH_8U, 3)
            cv.SetData(self._bitmap, pg.image.tostring(self._pgsurface, "RGB"))
            cv.CvtColor(self._bitmap, self._bitmap, cv.CV_RGB2BGR)
            self._colorSpace = ColorSpace.BGR


        elif (PIL_ENABLED and (source.__class__.__name__ == "JpegImageFile" or source.__class__.__name__ == "Image")):
            self._pil = source
            #from the opencv cookbook 
            #http://opencv.willowgarage.com/documentation/python/cookbook.html
            self._bitmap = cv.CreateImageHeader(self._pil.size, cv.IPL_DEPTH_8U, 3)
            cv.SetData(self._bitmap, self._pil.tostring())
            self._colorSpace = ColorSpace.BGR
            cv.CvtColor(self._bitmap, self._bitmap, cv.CV_RGB2BGR)
            #self._bitmap = cv.iplimage(self._bitmap)


        else:
            return None

        #if the caller passes in a colorspace we overide it 
        if(colorSpace != ColorSpace.UNKNOWN):
            self._colorSpace = colorSpace
      
      
        bm = self.getBitmap()
        self.width = bm.width
        self.height = bm.height
        self.depth = bm.depth
    
    def live(self):
        """
        This shows a live view of the camera.
        To use it's as simple as:

        >>> cam = Camera()
        >>> cam.live()

        Left click will show mouse coordinates and color
        Right click will kill the live image
        """

        start_time = time.time()
        
        from SimpleCV.Display import Display
        i = self
        d = Display(i.size())
        i.save(d)
        col = Color.RED

        while d.isNotDone():
          i = self
          elapsed_time = time.time() - start_time
          

          if d.mouseLeft:
            i.clearLayers()
            txt = "coord: (" + str(d.mouseX) + "," + str(d.mouseY) + ")"
            i.dl().text(txt, (10,i.height / 2), color=col)
            txt = "color: " + str(i.getPixel(d.mouseX,d.mouseY))
            i.dl().text(txt, (10,(i.height / 2) + 10), color=col)


          if elapsed_time > 0 and elapsed_time < 5:
            
            i.dl().text("In live mode", (10,10), color=col)
            i.dl().text("Left click will show mouse coordinates and color", (10,20), color=col)
            i.dl().text("Right click will kill the live image", (10,30), color=col)
            
          
          i.save(d)
          if d.mouseRight:
            d.done = True

        
        pg.quit()

    def getColorSpace(self):
        """
        Returns the value matched in the color space class
        so for instance you would use
        if(image.getColorSpace() == ColorSpace.RGB)

        RETURNS: Integer
        """
        return self._colorSpace
  
  
    def isRGB(self):
        """
        Returns Boolean
        """
        return(self._colorSpace==ColorSpace.RGB)


    def isBGR(self):
        """
        Returns Boolean
        """
        return(self._colorSpace==ColorSpace.BGR)
    
    
    def isHSV(self):
        """
        Returns Boolean
        """
        return(self._colorSpace==ColorSpace.HSV)
    
    
    def isHLS(self):
        """
        Returns Boolean
        """    
        return(self._colorSpace==ColorSpace.HLS)  
  
  
    def isXYZ(self):
        """
        Returns Boolean
        """
        return(self._colorSpace==ColorSpace.XYZ)
    
    
    def isGray(self):
        """
        Returns Boolean
        """
        return(self._colorSpace==ColorSpace.GRAY)    

    def toRGB(self):
        """
        Converts Image colorspace to RGB

        RETURNS: Image
        """
        retVal = self.getEmpty()
        if( self._colorSpace == ColorSpace.BGR or
                self._colorSpace == ColorSpace.UNKNOWN ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_BGR2RGB)
        elif( self._colorSpace == ColorSpace.HSV ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HSV2RGB)
        elif( self._colorSpace == ColorSpace.HLS ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HLS2RGB)    
        elif( self._colorSpace == ColorSpace.XYZ ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_XYZ2RGB)
        elif( self._colorSpace == ColorSpace.RGB ):
            retVal = self.getBitmap()
        else:
            warnings.warn("Image.toRGB: There is no supported conversion to RGB colorspace")
            return None
        return Image(retVal, colorSpace=ColorSpace.RGB )


    def toBGR(self):
        """
        Converts image colorspace to BGR

        RETURNS: Image
        """
        retVal = self.getEmpty()
        if( self._colorSpace == ColorSpace.RGB or
                self._colorSpace == ColorSpace.UNKNOWN ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_RGB2BGR)
        elif( self._colorSpace == ColorSpace.HSV ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HSV2BGR)
        elif( self._colorSpace == ColorSpace.HLS ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HLS2BGR)    
        elif( self._colorSpace == ColorSpace.XYZ ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_XYZ2BGR)
        elif( self._colorSpace == ColorSpace.BGR ):
            retVal = self.getBitmap()    
        else:
            warnings.warn("Image.toBGR: There is no supported conversion to BGR colorspace")
            return None
        return Image(retVal, colorSpace = ColorSpace.BGR )
  
  
    def toHLS(self):
        """
        Converts image to HLS colorspace

        RETURNS: Image
        """
        retVal = self.getEmpty()
        if( self._colorSpace == ColorSpace.BGR or
                self._colorSpace == ColorSpace.UNKNOWN ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_BGR2HLS)
        elif( self._colorSpace == ColorSpace.RGB):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_RGB2HLS)
        elif( self._colorSpace == ColorSpace.HSV ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HSV2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2HLS)
        elif( self._colorSpace == ColorSpace.XYZ ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_XYZ2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2HLS)
        elif( self._colorSpace == ColorSpace.HLS ):
            retVal = self.getBitmap()      
        else:
            warnings.warn("Image.toHSL: There is no supported conversion to HSL colorspace")
            return None
        return Image(retVal, colorSpace = ColorSpace.HLS )
    
    
    def toHSV(self):
        """
        Converts image to HSV colorspace

        RETURNS: Image
        """
        retVal = self.getEmpty()
        if( self._colorSpace == ColorSpace.BGR or
                self._colorSpace == ColorSpace.UNKNOWN ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_BGR2HSV)
        elif( self._colorSpace == ColorSpace.RGB):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_RGB2HSV)
        elif( self._colorSpace == ColorSpace.HLS ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HLS2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2HSV)
        elif( self._colorSpace == ColorSpace.XYZ ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_XYZ2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2HSV)
        elif( self._colorSpace == ColorSpace.HSV ):
            retVal = self.getBitmap()      
        else:
            warnings.warn("Image.toHSV: There is no supported conversion to HSV colorspace")
            return None
        return Image(retVal, colorSpace = ColorSpace.HSV )
    
    
    def toXYZ(self):
        """
        Converts image to XYZ colorspace

        RETURNS: Image
        """
        retVal = self.getEmpty()
        if( self._colorSpace == ColorSpace.BGR or
                self._colorSpace == ColorSpace.UNKNOWN ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_BGR2XYZ)
        elif( self._colorSpace == ColorSpace.RGB):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_RGB2XYZ)
        elif( self._colorSpace == ColorSpace.HLS ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HLS2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2XYZ)
        elif( self._colorSpace == ColorSpace.HSV ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HSV2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2XYZ)
        elif( self._colorSpace == ColorSpace.XYZ ):
            retVal = self.getBitmap()      
        else:
            warnings.warn("Image.toXYZ: There is no supported conversion to XYZ colorspace")
            return None
        return Image(retVal, colorSpace=ColorSpace.XYZ )
    
    
    def toGray(self):
        """
        Converts image to Grayscale colorspace

        RETURNS: Image
        """
        retVal = self.getEmpty(1)
        if( self._colorSpace == ColorSpace.BGR or
                self._colorSpace == ColorSpace.UNKNOWN ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_BGR2GRAY)
        elif( self._colorSpace == ColorSpace.RGB):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_RGB2GRAY)
        elif( self._colorSpace == ColorSpace.HLS ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HLS2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2GRAY)
        elif( self._colorSpace == ColorSpace.HSV ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HSV2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2GRAY)
        elif( self._colorSpace == ColorSpace.XYZ ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_XYZ2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2GRAY)  
        else:
            warnings.warn("Image.toGray: There is no supported conversion to gray colorspace")
            return None
        return Image(retVal, colorSpace = ColorSpace.GRAY )    
    
    
    def getEmpty(self, channels = 3):
        """
        Create a new, empty OpenCV bitmap with the specified number of channels (default 3)h
        """
        bitmap = cv.CreateImage(self.size(), cv.IPL_DEPTH_8U, channels)
        cv.SetZero(bitmap)
        return bitmap


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


    def getFPMatrix(self):
        """
        Converts the standard int bitmap to a floating point bitmap.
        """
        retVal =  cv.CreateImage((self.width,self.height), cv.IPL_DEPTH_32F, 3)
        cv.Convert(self.getBitmap(),retVal)
        return retVal
    
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
  
  
    def getGrayNumpy(self):
        """
        Return a grayscale Numpy array. This is handy for keypoint detection. 
        """
        if( self._grayNumpy != "" ):
            return self._grayNumpy
        else:
            self._grayNumpy = uint8(np.array(cv.GetMat(self._getGrayscaleBitmap())).transpose())

        return self._grayNumpy

    def getNumpy(self):
        """
        Get a Numpy array of the image in width x height x RGB dimensions
        """
        if self._numpy != "":
            return self._numpy
    
    
        self._numpy = np.array(self.getMatrix())[:, :, ::-1].transpose([1, 0, 2])
        return self._numpy


    def _getGrayscaleBitmap(self):
        if (self._graybitmap):
            return self._graybitmap


        self._graybitmap = self.getEmpty(1)
        temp = self.getEmpty(3)
        if( self._colorSpace == ColorSpace.BGR or
                self._colorSpace == ColorSpace.UNKNOWN ):
            cv.CvtColor(self.getBitmap(), self._graybitmap, cv.CV_BGR2GRAY)
        elif( self._colorSpace == ColorSpace.RGB):
            cv.CvtColor(self.getBitmap(), self._graybitmap, cv.CV_RGB2GRAY)
        elif( self._colorSpace == ColorSpace.HLS ):
            cv.CvtColor(self.getBitmap(), temp, cv.CV_HLS2RGB)
            cv.CvtColor(temp, self._graybitmap, cv.CV_RGB2GRAY)
        elif( self._colorSpace == ColorSpace.HSV ):
            cv.CvtColor(self.getBitmap(), temp, cv.CV_HSV2RGB)
            cv.CvtColor(temp, self._graybitmap, cv.CV_RGB2GRAY)
        elif( self._colorSpace == ColorSpace.XYZ ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_XYZ2RGB)
            cv.CvtColor(temp, self._graybitmap, cv.CV_RGB2GRAY)
        elif( self._colorSpace == ColorSpace.GRAY):
            cv.Split(self.getBitmap(), self._graybitmap, self._graybitmap, self._graybitmap, None)
        else:
            warnings.warn("Image._getGrayscaleBitmap: There is no supported conversion to gray colorspace")
            return None    
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
    

    def equalize(self):
        """
        Perform a histogram equalization on the image, return a grayscale image.
        """
        return Image(self._getEqualizedGrayscaleBitmap())
    
    def getPGSurface(self):
        """
        Gets the pygame surface.  This is used for rendering the display

        RETURNS: pgsurface
        """
        if (self._pgsurface):
            return self._pgsurface
        else:
            self._pgsurface = pg.image.fromstring(self.toRGB().getBitmap().tostring(), self.size(), "RGB")
            return self._pgsurface
    
    
    def save(self, filehandle_or_filename="", mode="", verbose = False):
        """
        Save the image to the specified filename.  If no filename is provided then
        then it will use the filename the Image was loaded from or the last
        place it was saved to. 
    
    
        Save will implicitly render the image's layers before saving, but the layers are 
        not applied to the Image itself.
        """
       
        if (not filehandle_or_filename):
            if (self.filename):
                filehandle_or_filename = self.filename
            else:
                filehandle_or_filename = self.filehandle


        if (len(self._mLayers)):
            saveimg = self.applyLayers()
        else:
            saveimg = self


        if (type(filehandle_or_filename) != str):
            fh = filehandle_or_filename

            if (not PIL_ENABLED):
                warnings.warn("You need the python image library to save by filehandle")
                return 0


            if (type(fh) == InstanceType and fh.__class__.__name__ == "JpegStreamer"):
                fh.jpgdata = StringIO() 
                saveimg.getPIL().save(fh.jpgdata, "jpeg") #save via PIL to a StringIO handle 
                fh.refreshtime = time.time()
                self.filename = "" 
                self.filehandle = fh


            elif (type(fh) == InstanceType and fh.__class__.__name__ == "VideoStream"):
                self.filename = "" 
                self.filehandle = fh
                fh.writeFrame(saveimg)


            elif (type(fh) == InstanceType and fh.__class__.__name__ == "Display"):
                self.filename = "" 
                self.filehandle = fh
                fh.writeFrame(saveimg)


            else:
                print "other"
                if (not mode):
                    mode = "jpeg"
      
                saveung.getPIL().save(fh, mode)
                self.filehandle = fh #set the filename for future save operations
                self.filename = ""
                
            if verbose:
              print self.filename
              
            return 1

        #make a temporary file location is there isn't one
        if not filehandle_or_filename:
          filename = tempfile.mkstemp(suffix=".png")[-1]
        else:  
          filename = filehandle_or_filename
          
        if (filename):
            cv.SaveImage(filename, saveimg.getBitmap())  
            self.filename = filename #set the filename for future save operations
            self.filehandle = ""
        elif (self.filename):
            cv.SaveImage(self.filename, saveimg.getBitmap())
        else:
            return 0

        if verbose:
          print self.filename
          
        return 1


    def copy(self):
        """
        Return a full copy of the Image's bitmap.  Note that this is different
        from using python's implicit copy function in that only the bitmap itself
        is copied.


        Returns: IMAGE
        """
        newimg = self.getEmpty() 
        cv.Copy(self.getBitmap(), newimg)
        return Image(newimg, colorSpace=self._colorSpace) 
    
    
    #scale this image, and return a new Image object with the new dimensions 
    def scale(self, width, height = -1):
        """
        WARNING: the two value scale command is deprecated. To set width and height
        use the resize function. 

        Scale the image to a new width and height.

        If no height is provided, the width is considered a scaling value ie::
            
            img.scale(200, 100) #scales the image to 200px x 100px
            img.scale(2.0) #enlarges the image to 2x its current size

        Returns: IMAGE
        """
        w, h = width, height
        if height == -1:
          w = int(self.width * width)
          h = int(self.height * width)
          if( w > MAX_DIMENSION or h > MAX_DIMENSION or h < 1 or w < 1 ):
              warnings.warn("Holy Heck! You tried to make an image really big or impossibly small. I can't scale that")
              return self
           

        scaled_bitmap = cv.CreateImage((w, h), 8, 3)
        cv.Resize(self.getBitmap(), scaled_bitmap)
        return Image(scaled_bitmap, colorSpace=self._colorSpace)

    
    def resize(self, w=None,h=None):
        """
        Resize image based on a width, a height, or both. 
        If width or height is not provided the value is inferred by keeping the aspect ratio. 
        If both values are provided then the image is resized accordingly.

        Returns: IMAGE
        """
        retVal = None
        if( w is None and h is None ):
            warnings.warn("Image.resize has no parameters. No operation is performed")
            return None
        elif( w is not None and h is None):
            sfactor = float(w)/float(self.width)
            h = int( sfactor*float(self.height) )
        elif( w is None and h is not None):
            sfactor = float(h)/float(self.height)
            w = int( sfactor*float(self.width) )
        if( w > MAX_DIMENSION or h > MAX_DIMENSION ):
            warnings.warn("Image.resize Holy Heck! You tried to make an image really big or impossibly small. I can't scale that")
            return retVal           
        scaled_bitmap = cv.CreateImage((w, h), 8, 3)
        cv.Resize(self.getBitmap(), scaled_bitmap)
        return Image(scaled_bitmap, colorSpace=self._colorSpace)
        

    def smooth(self, algorithm_name = 'gaussian', aperature = '', sigma = 0, spatial_sigma = 0, grayscale=False):
        """
        Smooth the image, by default with the Gaussian blur.  If desired,
        additional algorithms and aperatures can be specified.  Optional parameters
        are passed directly to OpenCV's cv.Smooth() function.

        If grayscale is true the smoothing operation is only performed on a single channel
        otherwise the operation is performed on each channel of the image. 

        Returns: IMAGE
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


        
        if( grayscale ):
            newimg = self.getEmpty(1)
            cv.Smooth(self._getGrayscaleBitmap(), newimg, algorithm, win_x, win_y, sigma, spatial_sigma)
        else:
            newimg = self.getEmpty(3)
            r = self.getEmpty(1) 
            g = self.getEmpty(1)
            b = self.getEmpty(1)
            ro = self.getEmpty(1) 
            go = self.getEmpty(1)
            bo = self.getEmpty(1)
            cv.Split(self.getBitmap(), b, g, r, None)
            cv.Smooth(r, ro, algorithm, win_x, win_y, sigma, spatial_sigma)            
            cv.Smooth(g, go, algorithm, win_x, win_y, sigma, spatial_sigma)
            cv.Smooth(b, bo, algorithm, win_x, win_y, sigma, spatial_sigma)
            cv.Merge(ro,go,bo, None, newimg)

        return Image(newimg, colorSpace=self._colorSpace)


    def medianFilter(self, window=''):
        """
        Perform a median filtering operation to denoise/despeckle the image.
        The optional parameter is the window size.
        """
        return self.smooth(algorithm_name='median', aperature=window)
    
    
    def bilateralFilter(self, window = ''):
        """
        Perform a bilateral filtering operation to denoise/despeckle the image.
        The optional parameter is the window size.
        """
        return self.smooth(algorithm_name='bilateral', aperature=window)
    
    
    def invert(self):
        """
        Invert (negative) the image note that this can also be done with the
        unary minus (-) operator.


        Returns: IMAGE
        """
        return -self 


    def grayscale(self):
        """
        return a gray scale version of the image


        Returns: IMAGE
        """
        return Image(self._getGrayscaleBitmap())


    def flipHorizontal(self):
        """
        Horizontally mirror an image
        Note that flip does not mean rotate 180 degrees! The two are different.

        Returns: IMAGE
        """
        newimg = self.getEmpty()
        cv.Flip(self.getBitmap(), newimg, 1)
        return Image(newimg, colorSpace=self._colorSpace) 


    def flipVertical(self):
        """
        Vertically mirror an image
        Note that flip does not mean rotate 180 degrees! The two are different.

        Returns: IMAGE
        """
        newimg = self.getEmpty()
        cv.Flip(self.getBitmap(), newimg, 0)
        return Image(newimg, colorSpace=self._colorSpace) 
    
    
    
    
    
    
    def stretch(self, thresh_low = 0, thresh_high = 255):
        """
        The stretch filter works on a greyscale image, if the image
        is color, it returns a greyscale image.  The filter works by
        taking in a lower and upper threshold.  Anything below the lower
        threshold is pushed to black (0) and anything above the upper
        threshold is pushed to white (255)


        Returns: IMAGE
        """
        try:
            newimg = self.getEmpty(1) 
            cv.Threshold(self._getGrayscaleBitmap(), newimg, thresh_low, 255, cv.CV_THRESH_TOZERO)
            cv.Not(newimg, newimg)
            cv.Threshold(newimg, newimg, 255 - thresh_high, 255, cv.CV_THRESH_TOZERO)
            cv.Not(newimg, newimg)
            return Image(newimg)
        except:
            return None
      
      
    def binarize(self, thresh = -1, maxv = 255, blocksize = 0, p = 5):
        """
        Do a binary threshold the image, changing all values below thresh to maxv
        and all above to black.  If a color tuple is provided, each color channel
        is thresholded separately.
    

        If threshold is -1 (default), an adaptive method (OTSU's method) is used. 
        If then a blocksize is specified, a moving average over each region of block*block 
        pixels a threshold is applied where threshold = local_mean - p.
        """
        if (is_tuple(thresh)):
            r = self.getEmpty(1) 
            g = self.getEmpty(1)
            b = self.getEmpty(1)
            cv.Split(self.getBitmap(), b, g, r, None)
    
    
            cv.Threshold(r, r, thresh[0], maxv, cv.CV_THRESH_BINARY_INV)
            cv.Threshold(g, g, thresh[1], maxv, cv.CV_THRESH_BINARY_INV)
            cv.Threshold(b, b, thresh[2], maxv, cv.CV_THRESH_BINARY_INV)
    
    
            cv.Add(r, g, r)
            cv.Add(r, b, r)
      
      
            return Image(r, colorSpace=self._colorSpace)
    
    
        elif thresh == -1:
            newbitmap = self.getEmpty(1)
            if blocksize:
                cv.AdaptiveThreshold(self._getGrayscaleBitmap(), newbitmap, maxv,
                    cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C, cv.CV_THRESH_BINARY_INV, blocksize, p)
            else:
                cv.Threshold(self._getGrayscaleBitmap(), newbitmap, thresh, float(maxv), cv.CV_THRESH_BINARY_INV + cv.CV_THRESH_OTSU)
            return Image(newbitmap, colorSpace=self._colorSpace)
        else:
            newbitmap = self.getEmpty(1) 
            #desaturate the image, and apply the new threshold          
            cv.Threshold(self._getGrayscaleBitmap(), newbitmap, thresh, float(maxv), cv.CV_THRESH_BINARY_INV)
            return Image(newbitmap, colorSpace=self._colorSpace)
  
  
  
  
    def meanColor(self):
        """
        Finds average color of all the pixels in the image.


        Returns: IMAGE
        """
        return tuple(reversed(cv.Avg(self.getBitmap())[0:3]))  
  
  


    def findCorners(self, maxnum = 50, minquality = 0.04, mindistance = 1.0):
        """
        This will find corner Feature objects and return them as a FeatureSet
        strongest corners first.  The parameters give the number of corners to look
        for, the minimum quality of the corner feature, and the minimum distance
        between corners.


        Returns: FEATURESET


        
        Standard Test:
        >>> img = Image("sampleimages/simplecv.png")
        >>> corners = img.findCorners()
        >>> if corners: True
        True

        Validation Test:
        >>> img = Image("sampleimages/black.png")
        >>> corners = img.findCorners()
        >>> if not corners: True
        True
        """
        #initialize buffer frames
        eig_image = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_32F, 1)
        temp_image = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_32F, 1)


        corner_coordinates = cv.GoodFeaturesToTrack(self._getGrayscaleBitmap(), eig_image, temp_image, maxnum, minquality, mindistance, None)


        corner_features = []   
        for (x, y) in corner_coordinates:
            corner_features.append(Corner(self, x, y))


        return FeatureSet(corner_features)


    def findBlobs(self, threshval = -1, minsize=10, maxsize=0, threshblocksize=0, threshconstant=5):
        """
        This will look for continuous
        light regions and return them as Blob features in a FeatureSet.  Parameters
        specify the binarize filter threshold value, and minimum and maximum size for blobs.  
        If a threshold value is -1, it will use an adaptive threshold.  See binarize() for
        more information about thresholding.  The threshblocksize and threshconstant
        parameters are only used for adaptive threshold.
 
    
        Returns: FEATURESET
        """
        if (maxsize == 0):  
            maxsize = self.width * self.height / 2
        #create a single channel image, thresholded to parameters
    
        blobmaker = BlobMaker()
        blobs = blobmaker.extractFromBinary(self.binarize(threshval, 255, threshblocksize, threshconstant).invert(),
            self, minsize = minsize, maxsize = maxsize)
    
        if not len(blobs):
            return None
            
        return FeatureSet(blobs).sortArea()

    #this code is based on code that's based on code from
    #http://blog.jozilla.net/2008/06/27/fun-with-python-opencv-and-face-detection/
    def findHaarFeatures(self, cascade, scale_factor=1.2, min_neighbors=2, use_canny=cv.CV_HAAR_DO_CANNY_PRUNING):
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
        
        Note that the cascade parameter can be either a filename, or a HaarCascade
        loaded with cv.Load().


        Returns: FEATURESET
        """
        storage = cv.CreateMemStorage(0)


        #lovely.  This segfaults if not present
        if type(cascade) == str:
            
          if (not os.path.exists(cascade)):
              warnings.warn("Could not find Haar Cascade file " + cascade)
              return None
          cascade = cv.Load(cascade)

  
        objects = cv.HaarDetectObjects(self._getEqualizedGrayscaleBitmap(), cascade, storage, scale_factor, use_canny)
        if objects: 
            return FeatureSet([HaarFeature(self, o, cascade) for o in objects])
    
    
        return None


    def drawCircle(self, ctr, rad, color = (0, 0, 0), thickness = 1):
        """
        Draw a circle on the Image, parameters include:
        * the center of the circle
        * the radius in pixels
        * a color tuple (default black)
        * the thickness of the circle


        Note that this function is depricated, try to use DrawingLayer.circle() instead


        Returns: NONE - Inline Operation
        """
        self.getDrawingLayer().circle((int(ctr[0]), int(ctr[1])), int(rad), color, int(thickness))
    
    
    def drawLine(self, pt1, pt2, color = (0, 0, 0), thickness = 1):
        """
        Draw a line on the Image, parameters include
        * pt1 - the first point for the line (tuple)
        * pt1 - the second point on the line (tuple)
        * a color tuple (default black)
        * thickness of the line 
 
 
        Note that this modifies the image in-place and clears all buffers.


        Returns: NONE - Inline Operation
        """
        pt1 = (int(pt1[0]), int(pt1[1]))
        pt2 = (int(pt2[0]), int(pt2[1]))
        self.getDrawingLayer().line(pt1, pt2, color, thickness)
    
    


    def size(self):
        """
        Gets width and height


        Returns: TUPLE
        """
        return cv.GetSize(self.getBitmap())


    def split(self, cols, rows):
        """
        Given number of cols and rows, splits the image into a cols x rows 2d array 
        of cropped images
        
        quadrants = Image("foo.jpg").split(2,2) <-- returns a 2d array of 4 images
        """
        crops = []
        
        wratio = self.width / cols
        hratio = self.height / rows
        
        for i in range(rows):
            row = []
            for j in range(cols):
                row.append(self.crop(j * wratio, i * hratio, wratio, hratio))
            crops.append(row)
        
        return crops

    def splitChannels(self, grayscale = True):
        """
        Split the channels of an image into RGB (not the default BGR)
        single parameter is whether to return the channels as grey images (default)
        or to return them as tinted color image 


        Returns: TUPLE - of 3 image objects
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

    def mergeChannels(self,r=None,b=None,g=None):
        """
        Merge channels is the oposite of splitChannels. The image takes one image for each
        of the R,G,B channels and then recombines them into a single image. 
        """
        if( r is None and g is None and b is None ):
            warnings.warn("ImageClass.mergeChannels - we need at least one valid channel")
            return None
        if( r is None ):
            r = self.getEmpty(1)
            cv.Zero(r);
        else:
            rt = r.getEmpty(1)
            cv.Split(r.getBitmap(),rt,rt,rt,None)
            r = rt
        if( g is None ):
            g = self.getEmpty(1)
            cv.Zero(g);
        else:
            gt = g.getEmpty(1)
            cv.Split(g.getBitmap(),gt,gt,gt,None)
            g = gt
        if( b is None ):
            b = self.getEmpty(1)
            cv.Zero(b);
        else:
            bt = b.getEmpty(1)
            cv.Split(b.getBitmap(),bt,bt,bt,None)
            b = bt

        retVal = self.getEmpty()
        cv.Merge(b,g,r,None,retVal)
        return Image(retVal);



        

    def applyHLSCurve(self, hCurve, lCurve, sCurve):
        """
        Apply 3 ColorCurve corrections applied in HSL space
        Parameters are: 
        * Hue ColorCurve 
        * Lightness (brightness/value) ColorCurve
        * Saturation ColorCurve


        Returns: IMAGE
        """
  
  
        #TODO CHECK ROI
        #TODO CHECK CURVE SIZE
        #TODO CHECK COLORSPACE
        #TODO CHECK CURVE SIZE
        temp  = cv.CreateImage(self.size(), 8, 3)
        #Move to HLS space
        cv.CvtColor(self._bitmap, temp, cv.CV_RGB2HLS)
        tempMat = cv.GetMat(temp) #convert the bitmap to a matrix
        #now apply the color curve correction
        tempMat = np.array(self.getMatrix()).copy()
        tempMat[:, :, 0] = np.take(hCurve.mCurve, tempMat[:, :, 0])
        tempMat[:, :, 1] = np.take(sCurve.mCurve, tempMat[:, :, 1])
        tempMat[:, :, 2] = np.take(lCurve.mCurve, tempMat[:, :, 2])
        #Now we jimmy the np array into a cvMat
        image = cv.CreateImageHeader((tempMat.shape[1], tempMat.shape[0]), cv.IPL_DEPTH_8U, 3)
        cv.SetData(image, tempMat.tostring(), tempMat.dtype.itemsize * 3 * tempMat.shape[1])
        cv.CvtColor(image, image, cv.CV_HLS2RGB)  
        return Image(image, colorSpace=self._colorSpace)


    def applyRGBCurve(self, rCurve, gCurve, bCurve):
        """
        Apply 3 ColorCurve corrections applied in rgb channels 
        Parameters are: 
        * Red ColorCurve 
        * Green ColorCurve
        * Blue ColorCurve


        Returns: IMAGE
        """
        tempMat = np.array(self.getMatrix()).copy()
        tempMat[:, :, 0] = np.take(bCurve.mCurve, tempMat[:, :, 0])
        tempMat[:, :, 1] = np.take(gCurve.mCurve, tempMat[:, :, 1])
        tempMat[:, :, 2] = np.take(rCurve.mCurve, tempMat[:, :, 2])
        #Now we jimmy the np array into a cvMat
        image = cv.CreateImageHeader((tempMat.shape[1], tempMat.shape[0]), cv.IPL_DEPTH_8U, 3)
        cv.SetData(image, tempMat.tostring(), tempMat.dtype.itemsize * 3 * tempMat.shape[1])
        return Image(image, colorSpace=self._colorSpace)


    def applyIntensityCurve(self, curve):
        """
        Intensity applied to all three color channels

        Parameters:
            curve - ColorCurve object
        Returns:
            Image
        """
        return self.applyRGBCurve(curve, curve, curve)
      
      
    def colorDistance(self, color = Color.BLACK):
        """
        Returns an image representing the distance of each pixel from a given color
        tuple, scaled between 0 (the given color) and 255.  Pixels distant from the 
        given tuple will appear as brighter and pixels closest to the target color 
        will be darker.
    
    
        By default this will give image intensity (distance from pure black)

        Parameters:
            color - Color object or Color Tuple
        Returns:
            Image
        """ 
        pixels = np.array(self.getNumpy()).reshape(-1, 3)   #reshape our matrix to 1xN
        distances = spsd.cdist(pixels, [color]) #calculate the distance each pixel is
        distances *= (255.0/distances.max()) #normalize to 0 - 255
        return Image(distances.reshape(self.width, self.height)) #return an Image
    
    def hueDistance(self, color = Color.BLACK, minsaturation = 20, minvalue = 20):
        """
        Returns an image representing the distance of each pixel from the given hue
        of a specific color.  The hue is "wrapped" at 180, so we have to take the shorter
        of the distances between them -- this gives a hue distance of max 90, which we'll 
        scale into a 0-255 grayscale image.
        
        The minsaturation and minvalue are optional parameters to weed out very weak hue
        signals in the picture, they will be pushed to max distance [255]

        Parameters:
            color = Color object or Color Tuple
            minsaturation - Integer
            minvalue - Integer
        Returns:
            Image

        
        """
        if isinstance(color,  (float,int,long,complex)):
            color_hue = color
        else:
            color_hue = Color.hsv(color)[0]
        
        vsh_matrix = self.toHSV().getNumpy().reshape(-1,3) #again, gets transposed to vsh
        hue_channel = np.cast['int'](vsh_matrix[:,2])
        
        if color_hue < 90:
            hue_loop = 180
        else:
            hue_loop = -180
        #set whether we need to move back or forward on the hue circle
        
        distances = np.minimum( np.abs(hue_channel - color_hue), np.abs(hue_channel - (color_hue + hue_loop)))
        #take the minimum distance for each pixel
        
        
        distances = np.where(
            np.logical_and(vsh_matrix[:,0] > minvalue, vsh_matrix[:,1] > minsaturation),
            distances * (255.0 / 90.0), #normalize 0 - 90 -> 0 - 255
            255.0) #use the maxvalue if it false outside of our value/saturation tolerances
        
        return Image(distances.reshape(self.width, self.height))
        
        
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

        Parameters:
            iterations - Int
        Returns:
            IMAGE
        """
        retVal = self.getEmpty() 
        kern = cv.CreateStructuringElementEx(3, 3, 1, 1, cv.CV_SHAPE_RECT)
        cv.Erode(self.getBitmap(), retVal, kern, iterations)
        return Image(retVal, colorSpace=self._colorSpace)


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


        Parameters:
            iterations - Integer
        Returns:
            IMAGE
        """
        retVal = self.getEmpty() 
        kern = cv.CreateStructuringElementEx(3, 3, 1, 1, cv.CV_SHAPE_RECT)
        cv.Dilate(self.getBitmap(), retVal, kern, iterations)
        return Image(retVal, colorSpace=self._colorSpace) 


    def morphOpen(self):
        """
        morphologyOpen applies a morphological open operation which is effectively
        an erosion operation followed by a morphological dilation. This operation
        helps to 'break apart' or 'open' binary regions which are close together. 


        See: http://en.wikipedia.org/wiki/Opening_(morphology)
        See: http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-morphologyex
        Example Use: two part blobs are 'sticking' together.
        Example Code: ./examples/MorphologyExample.py

        Returns:
            IMAGE
        """
        retVal = self.getEmpty() 
        temp = self.getEmpty()
        kern = cv.CreateStructuringElementEx(3, 3, 1, 1, cv.CV_SHAPE_RECT)
        try:
            cv.MorphologyEx(self.getBitmap(), retVal, temp, kern, cv.MORPH_OPEN, 1)
        except:
            cv.MorphologyEx(self.getBitmap(), retVal, temp, kern, cv.CV_MOP_OPEN, 1)
            #OPENCV 2.2 vs 2.3 compatability 
            
            
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


        Returns:
            IMAGE
        """
        retVal = self.getEmpty() 
        temp = self.getEmpty()
        kern = cv.CreateStructuringElementEx(3, 3, 1, 1, cv.CV_SHAPE_RECT)
        try:
            cv.MorphologyEx(self.getBitmap(), retVal, temp, kern, cv.MORPH_CLOSE, 1)
        except:
            cv.MorphologyEx(self.getBitmap(), retVal, temp, kern, cv.CV_MOP_CLOSE, 1)
            #OPENCV 2.2 vs 2.3 compatability 
        
        return Image(retVal, colorSpace=self._colorSpace)


    def morphGradient(self):
        """
        The morphological gradient is the difference betwen the morphological
        dilation and the morphological gradient. This operation extracts the 
        edges of a blobs in the image. 


        See: http://en.wikipedia.org/wiki/Morphological_Gradient
        See: http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-morphologyex
        Example Use: Use when you have blobs but you really just want to know the blob edges.
        Example Code: ./examples/MorphologyExample.py


        Returns:
            IMAGE
        """
        retVal = self.getEmpty() 
        retVal = self.getEmpty() 
        temp = self.getEmpty()
        kern = cv.CreateStructuringElementEx(3, 3, 1, 1, cv.CV_SHAPE_RECT)
        try:
            cv.MorphologyEx(self.getBitmap(), retVal, temp, kern, cv.MORPH_GRADIENT, 1)
        except:
            cv.MorphologyEx(self.getBitmap(), retVal, temp, kern, cv.CV_MOP_GRADIENT, 1)
        return Image(retVal, colorSpace=self._colorSpace )


    def histogram(self, numbins = 50):
        """
        Return a numpy array of the 1D histogram of intensity for pixels in the image
        Single parameter is how many "bins" to have.


        Parameters:
            numbins - Integer
        
        Returns:
            LIST
        """
        gray = self._getGrayscaleBitmap()


        (hist, bin_edges) = np.histogram(np.asarray(cv.GetMat(gray)), bins=numbins)
        return hist.tolist()
        
    def hueHistogram(self, bins = 179):
        """
        Returns the histogram of the hue channel for the image

        Parameters:
            bins - Integer
        Returns:
            Numpy Histogram
        """
        return np.histogram(self.toHSV().getNumpy()[:,:,2], bins = bins)[0]

    def huePeaks(self, bins = 179):
        """
        Takes the histogram of hues, and returns the peak hue values, which
        can be useful for determining what the "main colors" in a picture now.
        
        The bins parameter can be used to lump hues together, by default it is 179
        (the full resolution in OpenCV's HSV format)
        
        Peak detection code taken from https://gist.github.com/1178136
        Converted from/based on a MATLAB script at http://billauer.co.il/peakdet.html
        
        Returns a list of tuples, each tuple contains the hue, and the fraction
        of the image that has it.

        Parameters:
            bins - Integer
        Returns:
            list of tuples
        
        """
        """
        keyword arguments:
        y_axis -- A list containg the signal over which to find peaks
        x_axis -- A x-axis whose values correspond to the 'y_axis' list and is used
            in the return to specify the postion of the peaks. If omitted the index
            of the y_axis is used. (default: None)
        lookahead -- (optional) distance to look ahead from a peak candidate to
            determine if it is the actual peak (default: 500) 
            '(sample / period) / f' where '4 >= f >= 1.25' might be a good value
        delta -- (optional) this specifies a minimum difference between a peak and
            the following points, before a peak may be considered a peak. Useful
            to hinder the algorithm from picking up false peaks towards to end of
            the signal. To work well delta should be set to 'delta >= RMSnoise * 5'.
            (default: 0)
                Delta function causes a 20% decrease in speed, when omitted
                Correctly used it can double the speed of the algorithm
        
        return --  Each cell of the lists contains a tupple of:
            (position, peak_value) 
            to get the average peak value do 'np.mean(maxtab, 0)[1]' on the results
        """
        y_axis, x_axis = np.histogram(self.toHSV().getNumpy()[:,:,2], bins = bins)
        x_axis = x_axis[0:bins]
        lookahead = int(bins / 17)
        delta = 0
        
        maxtab = []
        mintab = []
        dump = []   #Used to pop the first hit which always if false
           
        length = len(y_axis)
        if x_axis is None:
            x_axis = range(length)
        
        #perform some checks
        if length != len(x_axis):
            raise ValueError, "Input vectors y_axis and x_axis must have same length"
        if lookahead < 1:
            raise ValueError, "Lookahead must be above '1' in value"
        if not (np.isscalar(delta) and delta >= 0):
            raise ValueError, "delta must be a positive number"
        
        #needs to be a numpy array
        y_axis = np.asarray(y_axis)
        
        #maxima and minima candidates are temporarily stored in
        #mx and mn respectively
        mn, mx = np.Inf, -np.Inf
        
        #Only detect peak if there is 'lookahead' amount of points after it
        for index, (x, y) in enumerate(zip(x_axis[:-lookahead], y_axis[:-lookahead])):
            if y > mx:
                mx = y
                mxpos = x
            if y < mn:
                mn = y
                mnpos = x
            
            ####look for max####
            if y < mx-delta and mx != np.Inf:
                #Maxima peak candidate found
                #look ahead in signal to ensure that this is a peak and not jitter
                if y_axis[index:index+lookahead].max() < mx:
                    maxtab.append((mxpos, mx))
                    dump.append(True)
                    #set algorithm to only find minima now
                    mx = np.Inf
                    mn = np.Inf
            
            ####look for min####
            if y > mn+delta and mn != -np.Inf:
                #Minima peak candidate found 
                #look ahead in signal to ensure that this is a peak and not jitter
                if y_axis[index:index+lookahead].min() > mn:
                    mintab.append((mnpos, mn))
                    dump.append(False)
                    #set algorithm to only find maxima now
                    mn = -np.Inf
                    mx = -np.Inf
        
        
        #Remove the false hit on the first value of the y_axis
        try:
            if dump[0]:
                maxtab.pop(0)
                #print "pop max"
            else:
                mintab.pop(0)
                #print "pop min"
            del dump
        except IndexError:
            #no peaks were found, should the function return empty lists?
            pass
      
        huetab = []
        for hue, pixelcount in maxtab:
            huetab.append((hue, pixelcount / float(self.width * self.height)))
        return huetab



    def __getitem__(self, coord):
        ret = self.getMatrix()[tuple(reversed(coord))]
        if (type(ret) == cv.cvmat):
            (width, height) = cv.GetSize(ret)
            newmat = cv.CreateMat(height, width, ret.type)
            cv.Copy(ret, newmat) #this seems to be a bug in opencv
            #if you don't copy the matrix slice, when you convert to bmp you get
            #a slice-sized hunk starting at 0, 0
            return Image(newmat)
            
        if self.isBGR():
            return tuple(reversed(ret))
        else:
            return tuple(ret)


    def __setitem__(self, coord, value):
        value = tuple(reversed(value))  #RGB -> BGR
        if (is_tuple(self.getMatrix()[tuple(reversed(coord))])):
            self.getMatrix()[tuple(reversed(coord))] = value 
        else:
            cv.Set(self.getMatrix()[tuple(reversed(coord))], value)
            self._clearBuffers("_matrix") 


    def __sub__(self, other):
        newbitmap = self.getEmpty() 
        if is_number(other):
            cv.SubS(self.getBitmap(), other, newbitmap)
        else:
            cv.Sub(self.getBitmap(), other.getBitmap(), newbitmap)
        return Image(newbitmap, colorSpace=self._colorSpace)


    def __add__(self, other):
        newbitmap = self.getEmpty() 
        if is_number(other):
            cv.AddS(self.getBitmap(), other, newbitmap)
        else:
            cv.Add(self.getBitmap(), other.getBitmap(), newbitmap)
        return Image(newbitmap, colorSpace=self._colorSpace)


    def __and__(self, other):
        newbitmap = self.getEmpty() 
        if is_number(other):
            cv.AndS(self.getBitmap(), other, newbitmap)
        else:
            cv.And(self.getBitmap(), other.getBitmap(), newbitmap)
        return Image(newbitmap, colorSpace=self._colorSpace)


    def __or__(self, other):
        newbitmap = self.getEmpty() 
        if is_number(other):
            cv.OrS(self.getBitmap(), other, newbitmap)
        else:
            cv.Or(self.getBitmap(), other.getBitmap(), newbitmap)
        return Image(newbitmap, colorSpace=self._colorSpace)


    def __div__(self, other):
        newbitmap = self.getEmpty() 
        if (not is_number(other)):
            cv.Div(self.getBitmap(), other.getBitmap(), newbitmap)
        else:
            cv.ConvertScale(self.getBitmap(), newbitmap, 1.0/float(other))
        return Image(newbitmap, colorSpace=self._colorSpace)


    def __mul__(self, other):
        newbitmap = self.getEmpty() 
        if (not is_number(other)):
            cv.Mul(self.getBitmap(), other.getBitmap(), newbitmap)
        else:
            cv.ConvertScale(self.getBitmap(), newbitmap, float(other))
        return Image(newbitmap, colorSpace=self._colorSpace)

    def __pow__(self, other):
        newbitmap = self.getEmpty() 
        cv.Pow(self.getBitmap(), newbitmap, other)
        return Image(newbitmap, colorSpace=self._colorSpace)


    def __neg__(self):
        newbitmap = self.getEmpty() 
        cv.Not(self.getBitmap(), newbitmap)
        return Image(newbitmap, colorSpace=self._colorSpace)


    def max(self, other):
        """
        The maximum value of my image, and the other image, in each channel
        If other is a number, returns the maximum of that and the number

        Parameters:
            other - Image
        Returns:
            IMAGE
        """ 
        newbitmap = self.getEmpty() 
        if is_number(other):
            cv.MaxS(self.getBitmap(), other.getBitmap(), newbitmap)
        else:
            cv.Max(self.getBitmap(), other.getBitmap(), newbitmap)
        return Image(newbitmap, colorSpace=self._colorSpace)


    def min(self, other):
        """
        The minimum value of my image, and the other image, in each channel
        If other is a number, returns the minimum of that and the number

        Parameters:
            other - Image
        Returns:
            IMAGE
        """ 
        newbitmap = self.getEmpty() 
        if is_number(other):
            cv.MaxS(self.getBitmap(), other.getBitmap(), newbitmap)
        else:
            cv.Max(self.getBitmap(), other.getBitmap(), newbitmap)
        return Image(newbitmap, colorSpace=self._colorSpace)


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

        INSTALLING ZEBRA CROSSING
        1) Download zebra crossing 1.6 from: http://code.google.com/p/zxing/
        2) unpack the zip file where ever you see fit
              cd zxing-1.6 
              ant -f core/build.xml
              ant -f javase/build.xml 
            This should build the library, but double check the readme
        3) Get our helper library 
           git clone git://github.com/oostendo/python-zxing.git
           cd python-zxing
           nosetests tests.py
        4) Our library does not have a setup file. You will need to add
           it to your path variables. On OSX/Linux use a text editor to modify your shell file (e.g. .bashrc)
        
           export ZXING_LIBRARY=<FULL PATH OF ZXING LIBRARY - (i.e. step 2)>
           export PYTHONPATH=$PYTHONPATH:<FULL PATH OF ZXING PYTHON PLUG-IN - (i.e. step 3)>
           
           On windows you will need to add these same variables to the system variable, e.g.
           http://www.computerhope.com/issues/ch000549.htm
        
        5) On OSX/Linux source your shell rc file (e.g. source .bashrc). Windows users may need to restart.
        
        6) Go grab some barcodes!

        WARNING:
        Users on OSX may see the following error:

        RuntimeWarning: tmpnam is a potential security risk to your program        
        
        We are working to resolve this issue. For normal use this should not be a problem.

        Parameters:
        
            zxing_path - String
            
        Returns:
        
            BARCODE
        """
        if not ZXING_ENABLED:
            warnings.warn("Zebra Crossing (ZXing) Library not installed. Please see the release notes.")
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

        Parameters:
            threshold - Int
            minlinelength - Int
            maxlinegap - Int
            cannyth1 - Int
            cannyth2 - Int
            
        Returns:
            FEATURESET
        """
        em = self._getEdgeMap(cannyth1, cannyth2)
    
    
        lines = cv.HoughLines2(em, cv.CreateMemStorage(), cv.CV_HOUGH_PROBABILISTIC, 1.0, cv.CV_PI/180.0, threshold, minlinelength, maxlinegap)


        linesFS = FeatureSet()
        for l in lines:
            linesFS.append(Line(self, l))  
        return linesFS
    
    
    
    
    def findChessboard(self, dimensions = (8, 5), subpixel = True):
        """
        Given an image, finds a chessboard within that image.  Returns the Chessboard featureset.
        The Chessboard is typically used for calibration because of its evenly spaced corners.
    
    
        The single parameter is the dimensions of the chessboard, typical one can be found in \SimpleCV\tools\CalibGrid.png
   
        Parameters:
            dimensions - Tuple
            subpixel - Boolean

        Returns:
            FeatureSet
        """
        corners = cv.FindChessboardCorners(self._getEqualizedGrayscaleBitmap(), dimensions, cv.CV_CALIB_CB_ADAPTIVE_THRESH + cv.CV_CALIB_CB_NORMALIZE_IMAGE )
        if(len(corners[1]) == dimensions[0]*dimensions[1]):
            if (subpixel):
                spCorners = cv.FindCornerSubPix(self.getGrayscaleMatrix(), corners[1], (11, 11), (-1, -1), (cv.CV_TERMCRIT_ITER | cv.CV_TERMCRIT_EPS, 10, 0.01))
            else:
                spCorners = corners[1]
            return FeatureSet([ Chessboard(self, dimensions, spCorners) ])
        else:
            return None


    def edges(self, t1=50, t2=100):
        """
        Finds an edge map Image using the Canny edge detection method.  Edges will be brighter than the surrounding area.


        The t1 parameter is roughly the "strength" of the edge required, and the value between t1 and t2 is used for edge linking.  For more information:


        <http://opencv.willowgarage.com/documentation/python/imgproc_feature_detection.html>
        <http://en.wikipedia.org/wiki/Canny_edge_detector>

        Parameters:
            t1 - Int
            t2 - Int
            
        Returns:
            IMAGE
        """
        return Image(self._getEdgeMap(t1, t2), colorSpace=self._colorSpace)


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


    def rotate(self, angle, fixed=True, point=[-1, -1], scale = 1.0):
        """
        This function rotates an image around a specific point by the given angle 
        By default in "fixed" mode, the returned Image is the same dimensions as the original Image, and the contents will be scaled to fit.  In "full" mode the
        contents retain the original size, and the Image object will scale
        by default, the point is the center of the image. 
        you can also specify a scaling parameter

        Note that when fixed is set to false selecting a rotation point has no effect since the image is move to fit on the screen.

        Parameters:
            angle - angle in degrees positive is clockwise, negative is counter clockwise 
            fixed - if fixed is true,keep the original image dimensions, otherwise scale the image to fit the rotation 
            point - the point about which we want to rotate, if none is defined we use the center.
            scale - and optional floating point scale parameter. 
            
        Returns:
            IMAGE
        """
        if( point[0] == -1 or point[1] == -1 ):
            point[0] = (self.width-1)/2
            point[1] = (self.height-1)/2


        if (fixed):
            retVal = self.getEmpty()
            rotMat = cv.CreateMat(2, 3, cv.CV_32FC1)
            cv.GetRotationMatrix2D((float(point[0]), float(point[1])), float(angle), float(scale), rotMat)
            cv.WarpAffine(self.getBitmap(), retVal, rotMat)
            return Image(retVal, colorSpace=self._colorSpace)




        #otherwise, we're expanding the matrix to fit the image at original size
        rotMat = cv.CreateMat(2, 3, cv.CV_32FC1)
        # first we create what we thing the rotation matrix should be
        cv.GetRotationMatrix2D((float(point[0]), float(point[1])), float(angle), float(scale), rotMat)
        A = np.array([0, 0, 1])
        B = np.array([self.width, 0, 1])
        C = np.array([self.width, self.height, 1])
        D = np.array([0, self.height, 1])
        #So we have defined our image ABC in homogenous coordinates
        #and apply the rotation so we can figure out the image size
        a = np.dot(rotMat, A)
        b = np.dot(rotMat, B)
        c = np.dot(rotMat, C)
        d = np.dot(rotMat, D)
        #I am not sure about this but I think the a/b/c/d are transposed
        #now we calculate the extents of the rotated components. 
        minY = min(a[1], b[1], c[1], d[1])
        minX = min(a[0], b[0], c[0], d[0])
        maxY = max(a[1], b[1], c[1], d[1])
        maxX = max(a[0], b[0], c[0], d[0])
        #from the extents we calculate the new size
        newWidth = np.ceil(maxX-minX)
        newHeight = np.ceil(maxY-minY)
        #now we calculate a new translation
        tX = 0
        tY = 0
        #calculate the translation that will get us centered in the new image
        if( minX < 0 ):
            tX = -1.0*minX
        elif(maxX > newWidth-1 ):
            tX = -1.0*(maxX-newWidth)


        if( minY < 0 ):
            tY = -1.0*minY
        elif(maxY > newHeight-1 ):
            tY = -1.0*(maxY-newHeight)


        #now we construct an affine map that will the rotation and scaling we want with the 
        #the corners all lined up nicely with the output image. 
        src = ((A[0], A[1]), (B[0], B[1]), (C[0], C[1]))
        dst = ((a[0]+tX, a[1]+tY), (b[0]+tX, b[1]+tY), (c[0]+tX, c[1]+tY))


        cv.GetAffineTransform(src, dst, rotMat)


        #calculate the translation of the corners to center the image
        #use these new corner positions as the input to cvGetAffineTransform
        retVal = cv.CreateImage((int(newWidth), int(newHeight)), 8, int(3))
        cv.WarpAffine(self.getBitmap(), retVal, rotMat)
        return Image(retVal, colorSpace=self._colorSpace) 


    def rotate90(self):
        """
        Does a fast 90 degree rotation to the right.
        Note that subsequent calls to this function *WILL NOT* keep rotating it to the right!!!
        This function just does a matrix transpose so following one transpose by another will 
        just yield the original image.  

        Returns:
            Image
        """
        retVal = cv.CreateImage((self.height, self.width), cv.IPL_DEPTH_8U, 3)
        cv.Transpose(self.getBitmap(), retVal)
        return(Image(retVal, colorSpace=self._colorSpace))
    
    
    def shear(self, cornerpoints):
        """
        Given a set of new corner points in clockwise order, return a shear-ed Image
        that transforms the Image contents.  The returned image is the same
        dimensions.


        cornerpoints is a 2x4 array of point tuples

        Returns:
            IMAGE
        """
        src =  ((0, 0), (self.width-1, 0), (self.width-1, self.height-1))
        #set the original points
        aWarp = cv.CreateMat(2, 3, cv.CV_32FC1)
        #create the empty warp matrix
        cv.GetAffineTransform(src, cornerpoints, aWarp)


        return self.transformAffine(aWarp)


    def transformAffine(self, rotMatrix):
        """
        This helper function for shear performs an affine rotation using the supplied matrix. 
        The matrix can be a either an openCV mat or an np.ndarray type. 
        The matrix should be a 2x3

        Parameters:
            rotMatrix - Numpy Array or CvMat
            
        Returns:
            IMAGE
        """
        retVal = self.getEmpty()
        if(type(rotMatrix) == np.ndarray ):
            rotMatrix = npArray2cvMat(rotMatrix)
        cv.WarpAffine(self.getBitmap(), retVal, rotMatrix)
        return Image(retVal, colorSpace=self._colorSpace) 


    def warp(self, cornerpoints):
        """
        Given a new set of corner points in clockwise order, return an Image with 
        the images contents warped to the new coordinates.  The returned image
        will be the same size as the original image


        Parameters:
            cornerpoints - List of Tuples

        Returns:
            IMAGE
        """
        #original coordinates
        src = ((0, 0), (self.width-1, 0), (self.width-1, self.height-1), (0, self.height-1))
    
    
        pWarp = cv.CreateMat(3, 3, cv.CV_32FC1) #create an empty 3x3 matrix
        cv.GetPerspectiveTransform(src, cornerpoints, pWarp) #figure out the warp matrix


        return self.transformPerspective(pWarp)


    def transformPerspective(self, rotMatrix):
        """
        This helper function for warp performs an affine rotation using the supplied matrix. 
        The matrix can be a either an openCV mat or an np.ndarray type. 
        The matrix should be a 3x3

        Parameters:
            rotMatrix - Numpy Array or CvMat

        Returns:
            IMAGE
        """
        retVal = self.getEmpty()
        if(type(rotMatrix) == np.ndarray ):
            rotMatrix = npArray2cvMat(rotMatrix)
        cv.WarpPerspective(self.getBitmap(), retVal, rotMatrix)
        return Image(retVal, colorSpace=self._colorSpace) 
  
  
    def getPixel(self, x, y):
        """
        This function returns the RGB value for a particular image pixel given a specific row and column.
        
        NOTE:
        this function will always return pixels in RGB format even if the image is BGR format. 
        
        Parameters:
            x - Int
            y - Int

        Returns:
            Int
        """
        c = None
        retVal = None
        if( x < 0 or x >= self.width ):
            warnings.warn("getRGBPixel: X value is not valid.")
        elif( y < 0 or y >= self.height ):
            warnings.warn("getRGBPixel: Y value is not valid.")
        else:
            c = cv.Get2D(self.getBitmap(), y, x)
            if( self._colorSpace == ColorSpace.BGR ): 
                retVal = (c[2],c[1],c[0])
            else:
                retVal = (c[0],c[1],c[2])
        
        return retVal
  
  
    def getGrayPixel(self, x, y):
        """
        This function returns the Gray value for a particular image pixel given a specific row and column.

        Parameters:
            x - Int
            y - Int

        Returns:
            Int
        """
        retVal = None
        if( x < 0 or x >= self.width ):
            warnings.warn("getGrayPixel: X value is not valid.") 
        elif( y < 0 or y >= self.height ):
            warnings.warn("getGrayPixel: Y value is not valid.")
        else:
            retVal = cv.Get2D(self._getGrayscaleBitmap(), y, x)
            retVal = retVal[0]
        return retVal
      
      
    def getVertScanline(self, column):
        """
        This function returns a single column of RGB values from the image.

        Parameters:
            column - Int

        Returns:
            Numpy Array
        """
        retVal = None
        if( column < 0 or column >= self.width ):
            warnings.warn("getVertRGBScanline: column value is not valid.")
        else:
            retVal = cv.GetCol(self.getBitmap(), column)
            retVal = np.array(retVal)
            retVal = retVal[:, 0, :] 
        return retVal
  
  
    def getHorzScanline(self, row):
        """
        This function returns a single row of RGB values from the image.

        Parameters:
            row - Int

        Returns:
            Numpy Array
        """
        retVal = None
        if( row < 0 or row >= self.height ):
            warnings.warn("getHorzRGBScanline: row value is not valid.")
        else:
            retVal = cv.GetRow(self.getBitmap(), row)
            retVal = np.array(retVal)
            retVal = retVal[0, :, :]
        return retVal
  
  
    def getVertScanlineGray(self, column):
        """
        This function returns a single column of gray values from the image.

        Parameters:
            row - Int

        Return:
            Numpy Array
        """
        retVal = None
        if( column < 0 or column >= self.width ):
            warnings.warn("getHorzRGBScanline: row value is not valid.")
        else:
            retVal = cv.GetCol(self._getGrayscaleBitmap(), column )
            retVal = np.array(retVal)
            #retVal = retVal.transpose()
        return retVal
  
  
    def getHorzScanlineGray(self, row):
        """
        This function returns a single row of RGB values from the image.

        Parameters:
            row - Int

        Returns:
            Numpy Array
        """
        retVal = None
        if( row < 0 or row >= self.height ):
            warnings.warn("getHorzRGBScanline: row value is not valid.")
        else:
            retVal = cv.GetRow(self._getGrayscaleBitmap(), row )
            retVal = np.array(retVal)
            retVal = retVal.transpose()
        return retVal


    def crop(self, x , y = None, w = None, h = None, centered=False):
        """
        Crop attempts to use the x and y position variables and the w and h width
        and height variables to crop the image. When centered is false, x and y
        define the top and left of the cropped rectangle. When centered is true
        the function uses x and y as the centroid of the cropped region.

        You can also pass a feature into crop and have it automatically return
        the cropped image within the bounding outside area of that feature
    
    
        Parameters:
            x - Int or Image
            y - Int
            w - Int
            h - Int
            centered - Boolean

        Returns:
            Image
        """

        #If it's a feature extract what we need
        if(isinstance(x, Feature)):
            theFeature = x
            x = theFeature.points[0][0]
            y = theFeature.points[0][1]
            w = theFeature.width()
            h = theFeature.height()

        if(y == None or w == None or h == None):
            print "Please provide an x, y, width, height to function"

        if( w <= 0 or h <= 0 ):
            warnings.warn("Can't do a negative crop!")
            return None
        
        retVal = cv.CreateImage((int(w),int(h)), cv.IPL_DEPTH_8U, 3)
        if( x < 0 or y < 0 ):
            warnings.warn("Crop will try to help you, but you have a negative crop position, your width and height may not be what you want them to be.")


        if( centered ):
            rectangle = (int(x-(w/2)), int(y-(h/2)), int(w), int(h))
        else:
            rectangle = (int(x), int(y), int(w), int(h))
    

        (topROI, bottomROI) = self._rectOverlapROIs((rectangle[2],rectangle[3]),(self.width,self.height),(rectangle[0],rectangle[1]))

        if( bottomROI is None ):
            warnings.warn("Hi, your crop rectangle doesn't even overlap your image. I have no choice but to return None.")
            return None

        retVal = cv.CreateImage((bottomROI[2],bottomROI[3]), cv.IPL_DEPTH_8U, 3)
    
        cv.SetImageROI(self.getBitmap(), bottomROI)
        cv.Copy(self.getBitmap(), retVal)
        cv.ResetImageROI(self.getBitmap())
        return Image(retVal, colorSpace=self._colorSpace)
    
    
    def regionSelect(self, x1, y1, x2, y2 ):
        """
        Region select is similar to crop, but instead of taking a position and width
        and height values it simply takes to points on the image and returns the selected
        region. This is very helpful for creating interactive scripts that require
        the user to select a region.

        Parameters:
            x1 - Int
            y1 - Int
            x2 - Int
            y2 - Int

        Returns:
            Image
        """
        w = abs(x1-x2)
        h = abs(y1-y2)


        retVal = None
        if( w <= 0 or h <= 0 or w > self.width or h > self.height ):
            warnings.warn("regionSelect: the given values will not fit in the image or are too small.")
        else:
            xf = x2 
            if( x1 < x2 ):
                xf = x1
            yf = y2
            if( y1 < y2 ):
                yf = y1
            retVal = self.crop(xf, yf, w, h)
      
      
        return retVal
  
  
    def clear(self):
        """
        This is a slightly unsafe method that clears out the entire image state
        it is usually used in conjunction with the drawing blobs to fill in draw
        only a single large blob in the image. 
        """
        cv.SetZero(self._bitmap)
        self._clearBuffers()
    
    


    
    
    def drawText(self, text = "", x = None, y = None, color = Color.BLUE, fontsize = 16):
        """
        This function draws the string that is passed on the screen at the specified coordinates


        The Default Color is blue but you can pass it various colors
        The text will default to the center of the screen if you don't pass it a value


        Parameters:
            text - String
            x - Int
            y - Int
            color - Color object or Color Tuple
            fontsize - Int
            
        Returns:
            Image
        """
        if(x == None):
            x = (self.width / 2)
        if(y == None):
            y = (self.height / 2)
    
    
        self.getDrawingLayer().setFontSize(fontsize)
        self.getDrawingLayer().text(text, (x, y), color)
    
    
    def drawRectangle(self,x,y,w,h,color=Color.RED,width=1,alpha=255):
        """
        Draw a rectangle on the screen given the upper left corner of the rectangle
        and the width and height. 
        
        x - the x position
        y - the y position
        w - the width of the rectangle
        h - the height of the rectangle
        color - an RGB tuple indicating the desired color.
        width - the width of the rectangle, a value less than or equal to zero means filled in completely.
        alpha - the alpha value on the interval from 255 to 0, 255 is opaque, 0 is completely transparent. 

        returns:
        None - this operation is in place. 
        """
        if( width < 1 ):
            self.getDrawingLayer().rectangle((x,y),(w,h),color,filled=True,alpha=alpha)
        else:
            self.getDrawingLayer().rectangle((x,y),(w,h),color,width,alpha=alpha)
            
    def drawRotatedRectangle(self,boundingbox,color=Color.RED,width=1):
        cv.EllipseBox(self.getBitmap(),boundingbox,color,width)


    def show(self, type = 'window'):
        """
        This function automatically pops up a window and shows the current image

        Types:
            window
            browser

        Parameters:
            type - String

        Return:
            Display
        """
        if(type == 'browser'):
          import webbrowser
          js = JpegStreamer(8080)
          self.save(js)
          webbrowser.open("http://localhost:8080", 2)
          return js
        elif (type == 'window'):
          from SimpleCV.Display import Display
          d = Display(self.size())
          self.save(d)
          return d
        else:
          print "Unknown type to show"

    def _surface2Image(self,surface):
        imgarray = pg.surfarray.array3d(surface)
        retVal = Image(imgarray)
        retVal._colorSpace = ColorSpace.RGB
        return retVal.toBGR().rotate90()
    
    def _image2Surface(self,img):
        return pg.image.fromstring(img.getPIL().tostring(),img.size(), "RGB") 
        #return pg.surfarray.make_surface(img.toRGB().getNumpy())

    def toPygameSurface(self):
        """
        Converts this image to a pygame surface. This is useful if you want
        to treat an image as a sprite to render onto an image. An example
        would be rendering blobs on to an image. THIS IS EXPERIMENTAL.
        """
        return pg.image.fromstring(self.getPIL().tostring(),self.size(), "RGB") 
    
        
    def addDrawingLayer(self, layer = None):
        """
        Push a new drawing layer onto the back of the layer stack

        Parameters:
            layer - String

        Returns:
            Int
        """

        if not isinstance(layer, DrawingLayer):
          return "Please pass a DrawingLayer object"
        
        if not layer:
            layer = DrawingLayer(self.size())
        self._mLayers.append(layer)
        return len(self._mLayers)-1
    
    
    def insertDrawingLayer(self, layer, index):
        """
        Insert a new layer into the layer stack at the specified index

        Parameters:
            layer - DrawingLayer
            index - Int

        """
        self._mLayers.insert(index, layer)
        return None    
  
  
    def removeDrawingLayer(self, index):
        """
        Remove a layer from the layer stack based on the layer's index.

        Parameters:
            index - Int
        """
        return self._mLayers.pop(index)
    
    
    def getDrawingLayer(self, index = -1):
        """
        Return a drawing layer based on the provided index.  If not provided, will
        default to the top layer.  If no layers exist, one will be created

        Parameters:
            index - Int
        """
        if not len(self._mLayers):
            layer = DrawingLayer(self.size())
            self.addDrawingLayer(layer)
      
      
        return self._mLayers[index]
    
    
    def dl(self, index = -1):
        """
        Alias for getDrawingLayer()
        """
        return self.getDrawingLayer(index)
  
  
    def clearLayers(self):
        """
        Remove all of the drawing layers. 
        """
        for i in self._mLayers:
            self._mLayers.remove(i)
      
      
        return None

    def layers(self):
        """
        Return the array of DrawingLayer objects associated with the image
        """
        return self._mLayers


        #render the image. 
    def _renderImage(self, layer):
        imgSurf = self.getPGSurface(self).copy()
        imgSurf.blit(layer._mSurface, (0, 0))
        return Image(imgSurf)
    
    def mergedLayers(self):
        """
        Return all DrawingLayer objects as a single DrawingLayer

        Returns:
            DrawingLayer
        """
        final = DrawingLayer(self.size())
        for layers in self._mLayers: #compose all the layers
                layers.renderToOtherLayer(final)
        return final
        
    def applyLayers(self, indicies=-1):
        """
        Render all of the layers onto the current image and return the result.
        Indicies can be a list of integers specifying the layers to be used.

        Parameters:
            indicies - Int
        """
        if not len(self._mLayers):
            return self
        
        if(indicies==-1 and len(self._mLayers) > 0 ):
            final = self.mergedLayers()
            imgSurf = self.getPGSurface().copy()
            imgSurf.blit(final._mSurface, (0, 0))
            return Image(imgSurf)
        else:
            final = DrawingLayer((self.width, self.height))
            retVal = self
            indicies.reverse()
            for idx in indicies:
                retVal = self._mLayers[idx].renderToOtherLayer(final)
            imgSurf = self.getPGSurface().copy()
            imgSurf.blit(final._mSurface, (0, 0))
            indicies.reverse()
            return Image(imgSurf)
            
    def adaptiveScale(self, resolution,fit=True):
        """
        Adapative Scale is used in the Display to automatically
        adjust image size to match the display size.

        This is typically used in this instance:
        >>> d = Display((800,600))
        >>> i = Image((640, 480))
        >>> i.save(d)

        Where this would scale the image to match the display size of 800x600

        Parameters:
            resolution - Tuple
            fit - Boolean

        Returns:
            Image
        """
        
        wndwAR = float(resolution[0])/float(resolution[1])
        imgAR = float(self.width)/float(self.height)
        img = self
        targetx = 0
        targety = 0
        targetw = resolution[0]
        targeth = resolution[1]
        if( self.size() == resolution): # we have to resize
            retVal = self
        elif( imgAR == wndwAR ):
            retVal = img.scale(resolution[0],resolution[1])
        elif(fit):
            #scale factors
            retVal = cv.CreateImage(resolution, cv.IPL_DEPTH_8U, 3)
            cv.Zero(retVal)
            wscale = (float(self.width)/float(resolution[0]))
            hscale = (float(self.height)/float(resolution[1]))
            if(wscale>1): #we're shrinking what is the percent reduction
                wscale=1-(1.0/wscale)
            else: # we need to grow the image by a percentage
                wscale = 1.0-wscale
            if(hscale>1):
                hscale=1-(1.0/hscale)
            else:
                hscale=1.0-hscale
            if( wscale == 0 ): #if we can get away with not scaling do that
                targetx = 0
                targety = (resolution[1]-self.height)/2
                targetw = img.width
                targeth = img.height
            elif( hscale == 0 ): #if we can get away with not scaling do that
                targetx = (resolution[0]-img.width)/2
                targety = 0
                targetw = img.width
                targeth = img.height
            elif(wscale < hscale): # the width has less distortion
                sfactor = float(resolution[0])/float(self.width)
                targetw = int(float(self.width)*sfactor)
                targeth = int(float(self.height)*sfactor)
                if( targetw > resolution[0] or targeth > resolution[1]):
                    #aw shucks that still didn't work do the other way instead
                    sfactor = float(resolution[1])/float(self.height)
                    targetw = int(float(self.width)*sfactor)
                    targeth = int(float(self.height)*sfactor)
                    targetx = (resolution[0]-targetw)/2
                    targety = 0
                else:
                    targetx = 0
                    targety = (resolution[1]-targeth)/2
                img = img.scale(targetw,targeth)
            else: #the height has more distortion
                sfactor = float(resolution[1])/float(self.height)
                targetw = int(float(self.width)*sfactor)
                targeth = int(float(self.height)*sfactor)
                if( targetw > resolution[0] or targeth > resolution[1]):
                    #aw shucks that still didn't work do the other way instead
                    sfactor = float(resolution[0])/float(self.width)
                    targetw = int(float(self.width)*sfactor)
                    targeth = int(float(self.height)*sfactor)
                    targetx = 0
                    targety = (resolution[1]-targeth)/2
                else:
                    targetx = (resolution[0]-targetw)/2
                    targety = 0
                img = img.scale(targetw,targeth)
            cv.SetImageROI(retVal,(targetx,targety,targetw,targeth))
            cv.Copy(img.getBitmap(),retVal)
            cv.ResetImageROI(retVal)
            retVal = Image(retVal)
        else: # we're going to crop instead
            retVal = cv.CreateImage(resolution, cv.IPL_DEPTH_8U, 3) 
            cv.Zero(retVal)
            if(self.width <= resolution[0] and self.height <= resolution[1] ): # center a too small image 
                #we're too small just center the thing
                targetx = (resolution[0]/2)-(self.width/2)
                targety = (resolution[1]/2)-(self.height/2)
            elif(self.width > resolution[0] and self.height > resolution[1]): #crop too big on both axes
                targetw = resolution[0]
                targeth = resolution[1]
                targetx = 0
                targety = 0
                x = (self.width-resolution[0])/2
                y = (self.height-resolution[1])/2
                img = img.crop(x,y,targetw,targeth)
            elif( self.width < resolution[0] and self.height >= resolution[1]): #height too big
                #crop along the y dimension and center along the x dimension
                targetw = self.width
                targeth = resolution[1]
                targetx = (resolution[0]-self.width)/2
                targety = 0
                x = 0
                y = (self.height-resolution[1])/2
                img = img.crop(x,y,targetw,targeth)
            elif( self.width > resolution[0] and self.height <= resolution[1]): #width too big
                #crop along the y dimension and center along the x dimension
                targetw = resolution[0]
                targeth = self.height
                targetx = 0
                targety = (resolution[1]-self.height)/2
                x = (self.width-resolution[0])/2
                y = 0
                img = img.crop(x,y,targetw,targeth)

            cv.SetImageROI(retVal,(x,y,targetw,targeth))
            cv.Copy(img.getBitmap(),retVal)
            cv.ResetImageROI(retVal)
            retval = Image(retVal)
        return(retVal)


    def blit(self, img, pos=None,alpha=None,mask=None,alphaMask=None):
        """
        img - an image to place ontop of this image.
        pos - an xy position tuple of the top left corner of img on this image.
        alpha - a single floating point alpha value (0=see the bottom image, 1=see just img, 0.5 blend the two 50/50).
        mask - a binary mask the same size as the input image. White areas are blitted, black areas are not blitted.
        alphaMask - an alpha mask where each grayscale value maps how much of each image is shown.
        """
        retVal = Image(self.getEmpty())
        cv.Copy(self.getBitmap(),retVal.getBitmap())

        w = img.width
        h = img.height

        if( pos is None ):
            pos = (0,0) 

        (topROI, bottomROI) = self._rectOverlapROIs((img.width,img.height),(self.width,self.height),pos)

        if( alpha is not None ):
            cv.SetImageROI(img.getBitmap(),topROI);
            cv.SetImageROI(retVal.getBitmap(),bottomROI);
            a = float(alpha)
            b = float(1.00-a)
            g = float(0.00)
            cv.AddWeighted(img.getBitmap(),a,retVal.getBitmap(),b,g,retVal.getBitmap())
            cv.ResetImageROI(img.getBitmap());
            cv.ResetImageROI(retVal.getBitmap());
        elif( alphaMask is not None ):
            if( alphaMask is not None and (alphaMask.width != img.width or alphaMask.height != img.height ) ):
                warnings.warn("Image.blit: your mask and image don't match sizes, if the mask doesn't fit, you can not blit! Try using the scale function.")
                return None

            cImg = img.crop(topROI[0],topROI[1],topROI[2],topROI[3])
            cMask = alphaMask.crop(topROI[0],topROI[1],topROI[2],topROI[3])
            retValC = retVal.crop(bottomROI[0],bottomROI[1],bottomROI[2],bottomROI[3])
            r = cImg.getEmpty(1) 
            g = cImg.getEmpty(1) 
            b = cImg.getEmpty(1) 
            cv.Split(cImg.getBitmap(), b, g, r, None)
            rf=cv.CreateImage((cImg.width,cImg.height),cv.IPL_DEPTH_32F,1)
            gf=cv.CreateImage((cImg.width,cImg.height),cv.IPL_DEPTH_32F,1)
            bf=cv.CreateImage((cImg.width,cImg.height),cv.IPL_DEPTH_32F,1)
            af=cv.CreateImage((cImg.width,cImg.height),cv.IPL_DEPTH_32F,1)
            cv.ConvertScale(r,rf)
            cv.ConvertScale(g,gf)
            cv.ConvertScale(b,bf)
            cv.ConvertScale(cMask._getGrayscaleBitmap(),af)
            cv.ConvertScale(af,af,scale=(1.0/255.0))
            cv.Mul(rf,af,rf)
            cv.Mul(gf,af,gf)
            cv.Mul(bf,af,bf)

            dr = retValC.getEmpty(1) 
            dg = retValC.getEmpty(1) 
            db = retValC.getEmpty(1) 
            cv.Split(retValC.getBitmap(), db, dg, dr, None)
            drf=cv.CreateImage((retValC.width,retValC.height),cv.IPL_DEPTH_32F,1)
            dgf=cv.CreateImage((retValC.width,retValC.height),cv.IPL_DEPTH_32F,1)
            dbf=cv.CreateImage((retValC.width,retValC.height),cv.IPL_DEPTH_32F,1)
            daf=cv.CreateImage((retValC.width,retValC.height),cv.IPL_DEPTH_32F,1)
            cv.ConvertScale(dr,drf)
            cv.ConvertScale(dg,dgf)
            cv.ConvertScale(db,dbf)
            cv.ConvertScale(cMask.invert()._getGrayscaleBitmap(),daf)
            cv.ConvertScale(daf,daf,scale=(1.0/255.0))
            cv.Mul(drf,daf,drf)
            cv.Mul(dgf,daf,dgf)
            cv.Mul(dbf,daf,dbf)
            
            cv.Add(rf,drf,rf)
            cv.Add(gf,dgf,gf)
            cv.Add(bf,dbf,bf)
 
            cv.ConvertScaleAbs(rf,r)
            cv.ConvertScaleAbs(gf,g)
            cv.ConvertScaleAbs(bf,b)

            cv.Merge(b,g,r,None,retValC.getBitmap())
            cv.SetImageROI(retVal.getBitmap(),bottomROI)
            cv.Copy(retValC.getBitmap(),retVal.getBitmap())
            cv.ResetImageROI(retVal.getBitmap())

        elif( mask is not None):
            if( mask is not None and (mask.width != img.width or mask.height != img.height ) ):
                warnings.warn("Image.blit: your mask and image don't match sizes, if the mask doesn't fit, you can not blit! Try using the scale function. ")
                return None            
            cv.SetImageROI(img.getBitmap(),topROI)
            cv.SetImageROI(mask.getBitmap(),topROI)
            cv.SetImageROI(retVal.getBitmap(),bottomROI)
            cv.Copy(img.getBitmap(),retVal.getBitmap(),mask.getBitmap())
            cv.ResetImageROI(img.getBitmap())
            cv.ResetImageROI(mask.getBitmap())
            cv.ResetImageROI(retVal.getBitmap())       
        else:  #vanilla blit
            cv.SetImageROI(img.getBitmap(),topROI)
            cv.SetImageROI(retVal.getBitmap(),bottomROI)
            cv.Copy(img.getBitmap(),retVal.getBitmap())
            cv.ResetImageROI(img.getBitmap())
            cv.ResetImageROI(retVal.getBitmap())

        return retVal

    def sideBySide(self, image, side="right", scale=True ):
        """
        Combine two images as a side by side. Great for before and after images.


        side - what side of this image to place the other image on.
               choices are (left/right/top/bottom). 
               
        scale - if true scale the smaller of the two sides to match the 
                edge touching the other image. If false we center the smaller
                of the two images on the edge touching the larger image. 

        """
        #there is probably a cleaner way to do this, but I know I hit every case when they are enumerated
        retVal = None
        if( side == "top" ):
            #clever
            retVal = image.sideBySide(self,"bottom",scale)
        elif( side == "bottom" ):
            if( self.width > image.width ):
                if( scale ):
                    #scale the other image width to fit
                    resized = image.resize(w=self.width)
                    nW = self.width
                    nH = self.height + resized.height
                    newCanvas = cv.CreateImage((nW,nH), cv.IPL_DEPTH_8U, 3)
                    cv.SetZero(newCanvas)
                    cv.SetImageROI(newCanvas,(0,0,nW,self.height))
                    cv.Copy(self.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas)
                    cv.SetImageROI(newCanvas,(0,self.height,resized.width,resized.height))
                    cv.Copy(resized.getBitmap(),newCanvas) 
                    cv.ResetImageROI(newCanvas)
                    retVal = Image(newCanvas,colorSpace=self._colorSpace)
                else:
                    nW = self.width
                    nH = self.height + image.height
                    newCanvas = cv.CreateImage((nW,nH), cv.IPL_DEPTH_8U, 3)
                    cv.SetZero(newCanvas)
                    cv.SetImageROI(newCanvas,(0,0,nW,self.height))
                    cv.Copy(self.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas)
                    xc = (self.width-image.width)/2
                    cv.SetImageROI(newCanvas,(xc,self.height,image.width,image.height))
                    cv.Copy(image.getBitmap(),newCanvas) 
                    cv.ResetImageROI(newCanvas)
                    retVal = Image(newCanvas,colorSpace=self._colorSpace)
            else: #our width is smaller than the other image
                if( scale ):
                    #scale the other image width to fit
                    resized = self.resize(w=image.width)
                    nW = image.width
                    nH = resized.height + image.height
                    newCanvas = cv.CreateImage((nW,nH), cv.IPL_DEPTH_8U, 3)
                    cv.SetZero(newCanvas)
                    cv.SetImageROI(newCanvas,(0,0,resized.width,resized.height))
                    cv.Copy(resized.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas)
                    cv.SetImageROI(newCanvas,(0,resized.height,nW,image.height))
                    cv.Copy(image.getBitmap(),newCanvas) 
                    cv.ResetImageROI(newCanvas)
                    retVal = Image(newCanvas,colorSpace=self._colorSpace)
                else:
                    nW = image.width
                    nH = self.height + image.height
                    newCanvas = cv.CreateImage((nW,nH), cv.IPL_DEPTH_8U, 3)
                    cv.SetZero(newCanvas)
                    xc = (image.width - self.width)/2
                    cv.SetImageROI(newCanvas,(xc,0,self.width,self.height))
                    cv.Copy(self.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas)
                    cv.SetImageROI(newCanvas,(0,self.height,image.width,image.height))
                    cv.Copy(image.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas) 
                    retVal = Image(newCanvas,colorSpace=self._colorSpace)

        elif( side == "right" ):
            retVal = image.sideBySide(self,"left",scale)
        else: #default to left
            if( self.height > image.height ):
                if( scale ):
                    #scale the other image height to fit
                    resized = image.resize(h=self.height)
                    nW = self.width + resized.height
                    nH = self.height
                    newCanvas = cv.CreateImage((nW,nH), cv.IPL_DEPTH_8U, 3)
                    cv.SetZero(newCanvas)
                    cv.SetImageROI(newCanvas,(0,0,resized.width,resized.height))
                    cv.Copy(resized.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas)
                    cv.SetImageROI(newCanvas,(resized.width,0,self.width,self.height))
                    cv.Copy(self.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas) 
                    retVal = Image(newCanvas,colorSpace=self._colorSpace)
                else:
                    nW = self.width+image.width
                    nH = self.height
                    newCanvas = cv.CreateImage((nW,nH), cv.IPL_DEPTH_8U, 3)
                    cv.SetZero(newCanvas)
                    yc = (self.height-image.height)/2
                    cv.SetImageROI(newCanvas,(0,yc,image.width,image.height))
                    cv.Copy(image.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas)
                    cv.SetImageROI(newCanvas,(image.width,0,self.width,self.height))
                    cv.Copy(self.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas) 
                    retVal = Image(newCanvas,colorSpace=self._colorSpace)
            else: #our height is smaller than the other image
                if( scale ):
                    #scale our height to fit
                    resized = self.resize(h=image.height)
                    nW = image.width + resized.width
                    nH = image.height
                    newCanvas = cv.CreateImage((nW,nH), cv.IPL_DEPTH_8U, 3)
                    cv.SetZero(newCanvas)
                    cv.SetImageROI(newCanvas,(0,0,image.width,image.height))
                    cv.Copy(image.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas)
                    cv.SetImageROI(newCanvas,(image.width,0,resized.width,resized.height))
                    cv.Copy(resized.getBitmap(),newCanvas) 
                    cv.ResetImageROI(newCanvas)
                    retVal = Image(newCanvas,colorSpace=self._colorSpace)
                else:
                    nW = image.width + self.width
                    nH = image.height
                    newCanvas = cv.CreateImage((nW,nH), cv.IPL_DEPTH_8U, 3)
                    cv.SetZero(newCanvas)
                    cv.SetImageROI(newCanvas,(0,0,image.width,image.height))
                    cv.Copy(image.getBitmap(),newCanvas)
                    cv.ResetImageROI(newCanvas)
                    yc = (image.height-self.height)/2
                    cv.SetImageROI(newCanvas,(image.width,yc,self.width,self.height))
                    cv.Copy(self.getBitmap(),newCanvas) 
                    cv.ResetImageROI(newCanvas)
                    retVal = Image(newCanvas,colorSpace=self._colorSpace)
        return retVal


    def embiggen(self, size=None, color=Color.BLACK, pos=None):
        """
        Make the canvas larger but keep the image the same size. 

        size - width and heigt tuple of the new canvas. 

        color - the color of the canvas 

        pos - the position of the top left corner of image on the new canvas, 
              if none the image is centered.
        """
        
        if( size == None or size[0] < self.width or size[1] < self.height ):
            warnings.warn("image.embiggenCanvas: the size provided is invalid")
            return None

        newCanvas = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3)
        cv.SetZero(newCanvas)
        newColor = cv.RGB(color[0],color[1],color[2])
        cv.AddS(newCanvas,newColor,newCanvas)
        topROI = None
        bottomROI = None
        if( pos is None ):
            pos = (((size[0]-self.width)/2),((size[1]-self.height)/2))

        (topROI, bottomROI) = self._rectOverlapROIs((self.width,self.height),size,pos)
        if( topROI is None or bottomROI is None):
            warnings.warn("image.embiggenCanvas: the position of the old image doesn't make sense, there is no overlap")
            return None

        cv.SetImageROI(newCanvas, bottomROI)
        cv.SetImageROI(self.getBitmap(),topROI)
        cv.Copy(self.getBitmap(),newCanvas)
        cv.ResetImageROI(newCanvas)
        cv.ResetImageROI(self.getBitmap())
        return Image(newCanvas)



    def _rectOverlapROIs(self,top, bottom, pos):
        """
        top is a rectangle (w,h)
        bottom is a rectangle (w,h)
        pos is the top left corner of the top rectangle with respect to the bottom rectangle's top left corner
        method returns none if the two rectangles do not overlap. Otherwise returns the top rectangle's ROI (x,y,w,h)
        and the bottom rectangle's ROI (x,y,w,h) 
        """  
        # the position of the top rect coordinates give bottom top right = (0,0) 
        tr = (pos[0]+top[0],pos[1]) 
        tl = pos 
        br = (pos[0]+top[0],pos[1]+top[1])
        bl = (pos[0],pos[1]+top[1])
        # do an overlap test to weed out corner cases and errors
        def inBounds((w,h), (x,y)):
            retVal = True
            if( x < 0 or  y < 0 or x > w or y > h):
                retVal = False
            return retVal

        trc = inBounds(bottom,tr) 
        tlc = inBounds(bottom,tl) 
        brc = inBounds(bottom,br) 
        blc = inBounds(bottom,bl) 
        if( not trc and not tlc and not brc and not blc ): # no overlap
            return None,None
        elif( trc and tlc and brc and blc ): # easy case top is fully inside bottom 
            tRet = (0,0,top[0],top[1])
            bRet = (pos[0],pos[1],top[0],top[1])
            return tRet,bRet
        # let's figure out where the top rectangle sits on the bottom
        # we clamp the corners of the top rectangle to live inside
        # the bottom rectangle and from that get the x,y,w,h
        tl = (np.clip(tl[0],0,bottom[0]),np.clip(tl[1],0,bottom[1]))
        br = (np.clip(br[0],0,bottom[0]),np.clip(br[1],0,bottom[1]))

        bx = tl[0]
        by = tl[1] 
        bw = abs(tl[0]-br[0])
        bh = abs(tl[1]-br[1])
        # now let's figure where the bottom rectangle is in the top rectangle 
        # we do the same thing with different coordinates
        pos = (-1*pos[0], -1*pos[1])
        #recalculate the bottoms's corners with respect to the top. 
        tr = (pos[0]+bottom[0],pos[1])
        tl = pos 
        br = (pos[0]+bottom[0],pos[1]+bottom[1])
        bl = (pos[0],pos[1]+bottom[1])
        tl = (np.clip(tl[0],0,top[0]), np.clip(tl[1],0,top[1]))
        br = (np.clip(br[0],0,top[0]), np.clip(br[1],0,top[1]))
        tx = tl[0]
        ty = tl[1] 
        tw = abs(br[0]-tl[0])
        th = abs(br[1]-tl[1])
        return (tx,ty,tw,th),(bx,by,bw,bh)

    def createBinaryMask(self,color1=(0,0,0),color2=(255,255,255)):
        """
        Generate a binary mask of the image based on a range of rgb values.
        A binary mask is a black and white image where the white area is kept and the
        black area is removed. 

        This method is used by specifying two colors as the range between the minimum and maximum
        values that will be masked white.

        example:
        >>>> img.createBinaryMask(color1=(0,128,128),color2=(255,255,255)
       
        """
        if( color1[0]-color2[0] == 0 or 
            color1[1]-color2[1] == 0 or
            color1[2]-color2[2] == 0 ):
            warnings.warn("No color range selected, the result will be black, returning None instead.")
            return None
        if( color1[0] > 255 or color1[0] < 0 or
            color1[1] > 255 or color1[1] < 0 or
            color1[2] > 255 or color1[2] < 0 or
            color2[0] > 255 or color2[0] < 0 or
            color2[1] > 255 or color2[1] < 0 or
            color2[2] > 255 or color2[2] < 0 ):
            warnings.warn("One of the tuple values falls outside of the range of 0 to 255")
            return None 

        r = self.getEmpty(1)
        g = self.getEmpty(1)
        b = self.getEmpty(1)
        
        rl = self.getEmpty(1)
        gl = self.getEmpty(1)
        bl = self.getEmpty(1)
 
        rh = self.getEmpty(1)
        gh = self.getEmpty(1)
        bh = self.getEmpty(1)

        cv.Split(self.getBitmap(),b,g,r,None);
        #the difference == 255 case is where open CV
        #kinda screws up, this should just be a white image
        if( abs(color1[0]-color2[0]) == 255 ):
            cv.Zero(rl)
            cv.AddS(rl,255,rl)
        #there is a corner case here where difference == 0
        #right now we throw an error on this case. 
        #also we use the triplets directly as OpenCV is 
        # SUPER FINICKY about the type of the threshold. 
        elif( color1[0] < color2[0] ):
            cv.Threshold(r,rl,color1[0],255,cv.CV_THRESH_BINARY)
            cv.Threshold(r,rh,color2[0],255,cv.CV_THRESH_BINARY)
            cv.Sub(rl,rh,rl)
        else:
            cv.Threshold(r,rl,color2[0],255,cv.CV_THRESH_BINARY)
            cv.Threshold(r,rh,color1[0],255,cv.CV_THRESH_BINARY)    
            cv.Sub(rl,rh,rl)


        if( abs(color1[1]-color2[1]) == 255 ):
            cv.Zero(gl)
            cv.AddS(gl,255,gl)
        elif( color1[1] < color2[1] ):
            cv.Threshold(g,gl,color1[1],255,cv.CV_THRESH_BINARY)
            cv.Threshold(g,gh,color2[1],255,cv.CV_THRESH_BINARY)
            cv.Sub(gl,gh,gl)
        else:
            cv.Threshold(g,gl,color2[1],255,cv.CV_THRESH_BINARY)
            cv.Threshold(g,gh,color1[1],255,cv.CV_THRESH_BINARY)    
            cv.Sub(gl,gh,gl)

        if( abs(color1[2]-color2[2]) == 255 ):
            cv.Zero(bl)
            cv.AddS(bl,255,bl)
        elif( color1[2] < color2[2] ):
            cv.Threshold(b,bl,color1[2],255,cv.CV_THRESH_BINARY)
            cv.Threshold(b,bh,color2[2],255,cv.CV_THRESH_BINARY)
            cv.Sub(bl,bh,bl)
        else:
            cv.Threshold(b,bl,color2[2],255,cv.CV_THRESH_BINARY)
            cv.Threshold(b,bh,color1[2],255,cv.CV_THRESH_BINARY)    
            cv.Sub(bl,bh,bl)


        cv.And(rl,gl,rl)
        cv.And(rl,bl,rl)
        return Image(rl)

    def applyBinaryMask(self, mask,bg_color=Color.BLACK):
        """
        Apply a binary mask to the image. The white areas of the mask will be kept,
        and the black areas removed. The removed areas will be set to the color of 
        bg_color. 

        mask - the binary mask image. White areas are kept, black areas are removed.
        bg_color - the color of the background on the mask.
        """
        newCanvas = cv.CreateImage((self.width,self.height), cv.IPL_DEPTH_8U, 3)
        cv.SetZero(newCanvas)
        newBG = cv.RGB(bg_color[0],bg_color[1],bg_color[2])
        cv.AddS(newCanvas,newBG,newCanvas)
        if( mask.width != self.width or mask.height != self.height ):
            warnings.warn("Image.applyBinaryMask: your mask and image don't match sizes, if the mask doesn't fit, you can't apply it! Try using the scale function. ")
            return None
        cv.Copy(self.getBitmap(),newCanvas,mask.getBitmap());
        return Image(newCanvas,colorSpace=self._colorSpace);

    def createAlphaMask(self, hue=60, hue_lb=None,hue_ub=None):
        """
        Generate a grayscale or binary mask image based either on a hue or an RGB triplet that can be used
        like an alpha channel. In the resulting mask, the hue/rgb_color will be treated as transparent (black). 

        When a hue is used the mask is treated like an 8bit alpha channel.
        When an RGB triplet is used the result is a binary mask. 
        rgb_thresh is a distance measure between a given a pixel and the mask value that we will
        add to the mask. For example, if rgb_color=(0,255,0) and rgb_thresh=5 then any pixel 
        winthin five color values of the rgb_color will be added to the mask (e.g. (0,250,0),(5,255,0)....)

        Invert flips the mask values.

        Parameters:
             hue = a hue used to generate the alpha mask.
             rgb_color = an rgb triplet used to generate a mask
             rgb_thresh = an integer distance from the rgb_color that will also be added to the mask. 
        """

        if( hue<0 or hue > 180 ):
            warnings.warn("Invalid hue color, valid hue range is 0 to 180.")

        if( self._colorSpace != ColorSpace.HSV ):
            hsv = self.toHSV()
        else:
            hsv = self
        h = hsv.getEmpty(1)
        s = hsv.getEmpty(1)
        mask = hsv.getEmpty(1)
        cv.Split(hsv.getBitmap(),None,s,h,None)
        hlut = np.zeros((256,1),dtype=uint8) #thankfully we're not doing a LUT on saturation 
        if(hue_lb is not None and hue_ub is not None):
            hlut[hue_lb:hue_ub]=255
        else:
            hlut[hue] = 255
        cv.LUT(h,mask,cv.fromarray(hlut))
        cv.Copy(s,h,mask) #we'll save memory using hue
        return Image(h).invert() 


    def applyPixelFunction(self, theFunc):
        """
        apply a function to every pixel and return the result
        The function must be of the form int (r,g,b)=func((r,g,b))
        """
        #there should be a way to do this faster using numpy vectorize
        #but I can get vectorize to work with the three channels together... have to split them
        #TODO: benchmark this against vectorize 
        pixels = np.array(self.getNumpy()).reshape(-1,3).tolist()
        result = np.array(map(theFunc,pixels),dtype=uint8).reshape(self.width,self.height,3) 
        return Image(result) 


    def integralImage(self,tilted=False):
        """
        Calculate the integral image and return it as a numpy array.
        The integral image gives the sum of all of the pixels above and to the
        right of a given pixel location. It is useful for computing Haar cascades.
        The return type is a numpy array the same size of the image. The integral
        image requires 32Bit values which are not easily supported by the SimpleCV
        Image class.

        Parameters:
            tilted - Boolean

        Returns:
            Numpy Array
        """
        
        if(tilted):
            img2 = cv.CreateImage((self.width+1, self.height+1), cv.IPL_DEPTH_32F, 1)
            img3 = cv.CreateImage((self.width+1, self.height+1), cv.IPL_DEPTH_32F, 1) 
            cv.Integral(self._getGrayscaleBitmap(),img3,None,img2)
        else:
            img2 = cv.CreateImage((self.width+1, self.height+1), cv.IPL_DEPTH_32F, 1) 
            cv.Integral(self._getGrayscaleBitmap(),img2)
        return np.array(cv.GetMat(img2))
        
        
    def convolve(self,kernel = [[1,0,0],[0,1,0],[0,0,1]],center=None):
        """
        Convolution performs a shape change on an image.  It is similiar to
        something like a dilate.  You pass it a kernel in the form of a list, np.array, or cvMat


        Example:
        
        >>> img = Image("sampleimages/simplecv.png")
        >>> kernel = [[1,0,0],[0,1,0],[0,0,1]]
        >>> conv = img.convolve()


        Parameters:
            kernel - Array, Numpy Array, CvMat
            center - Boolean

        Returns:
            Image
        """
        if(isinstance(kernel, list)):
            kernel = np.array(kernel)
            
        if(type(kernel)==np.ndarray):
            sz = kernel.shape
            kernel = kernel.astype(np.float32)
            myKernel = cv.CreateMat(sz[0], sz[1], cv.CV_32FC1)
            cv.SetData(myKernel, kernel.tostring(), kernel.dtype.itemsize * kernel.shape[1])
        elif(type(kernel)==cv.mat):
            myKernel = kernel
        else:
            warnings.warn("Convolution uses numpy arrays or cv.mat type.")
            return None
        retVal = self.getEmpty(3)
        if(center is None):
            cv.Filter2D(self.getBitmap(),retVal,myKernel)
        else:
            cv.Filter2D(self.getBitmap(),retVal,myKernel,center)
        return Image(retVal)

    def findTemplate(self, template_image = None, threshold = 5, method = "SQR_DIFF_NORM"):
        """
        This function searches an image for a template image.  The template
        image is a smaller image that is searched for in the bigger image.
        This is a basic pattern finder in an image.  This uses the standard
        OpenCV template (pattern) matching and cannot handle scaling or rotation

        
        Template matching returns a match score for every pixel in the image.
        Often pixels that are near to each other and a close match to the template
        are returned as a match. If the threshold is set too low expect to get
        a huge number of values. The threshold parameter is in terms of the
        number of standard deviations from the mean match value you are looking
        
        For example, matches that are above three standard deviations will return
        0.1% of the pixels. In a 800x600 image this means there will be
        800*600*0.001 = 480 matches.

        This method returns the locations of wherever it finds a match above a
        threshold. Because of how template matching works, very often multiple
        instances of the template overlap significantly. The best approach is to
        find the centroid of all of these values. We suggest using an iterative
        k-means approach to find the centroids.
        
        methods:
        SQR_DIFF_NORM - Normalized square difference
        SQR_DIFF      - Square difference
        CCOEFF        -
        CCOEFF_NORM   -
        CCORR         - Cross correlation
        CCORR_NORM    - Normalize cross correlation

        Example:
        
        >>> image = Image("/path/to/img.png")
        >>> pattern_image = image.crop(100,100,100,100)
        >>> found_patterns = image.findTemplate(pattern_image)
        >>> found_patterns.draw()
        >>> image.show()


        Parameters:
            template_image - Image
            threshold - Int
            method - String
        
        RETURNS:
            FeatureSet
        """
        if(template_image == None):
            print "Need image for matching"
            return

        if(template_image.width > self.width):
            print "Image too wide"
            return

        if(template_image.height > self.height):
            print "Image too tall"
            return

        check = 0; # if check = 0 we want maximal value, otherwise minimal
        if(method is None or method == "" or method == "SQR_DIFF_NORM"):#minimal
            method = cv.CV_TM_SQDIFF_NORMED
            check = 1;
        elif(method == "SQR_DIFF"): #minimal
            method = cv.CV_TM_SQDIFF
            check = 1
        elif(method == "CCOEFF"): #maximal
            method = cv.CV_TM_CCOEFF
        elif(method == "CCOEFF_NORM"): #maximal
            method = cv.CV_TM_CCOEFF_NORMED
        elif(method == "CCORR"): #maximal
            method = cv.CV_TM_CCORR
        elif(method == "CCORR_NORM"): #maximal 
            method = cv.CV_TM_CCORR_NORMED
        else:
            warnings.warn("ooops.. I don't know what template matching method you are looking for.")
            return None
        #create new image for template matching computation
        matches = cv.CreateMat( (self.height - template_image.height + 1),
                                (self.width - template_image.width + 1),
                                cv.CV_32FC1)
            
        #choose template matching method to be used
        
        cv.MatchTemplate( self._getGrayscaleBitmap(), template_image._getGrayscaleBitmap(), matches, method )
        mean = np.mean(matches)
        sd = np.std(matches)
        if(check > 0):
            compute = np.where((matches < mean-threshold*sd) )
        else:
            compute = np.where((matches > mean+threshold*sd) )

        mapped = map(tuple, np.column_stack(compute))
        fs = FeatureSet()
        for location in mapped:
            fs.append(TemplateMatch(self, template_image.getBitmap(), (location[1],location[0]), matches[location[0], location[1]]))

        #cluster overlapping template matches 
        finalfs = FeatureSet()
        if( len(fs) > 0 ):
            print(str(len(fs)))
            finalfs.append(fs[0])
            for f in fs:
                match = False
                for f2 in finalfs:
                    if( f2.overlaps(f) ): #if they overlap
                        f2.consume(f) #merge them
                        match = True
                        break
                    if( not match ):
                        finalfs.append(f)
        
            for f in finalfs: #rescale the resulting clusters to fit the template size
                f.rescale(template_image.width,template_image.height)
            
            fs = finalfs
        
        return fs                           
         

    def readText(self):
        """
        This function will return any text it can find using OCR on the
        image.

        Please note that it does not handle rotation well, so if you need
        it in your application try to rotate and/or crop the area so that
        the text would be the same way a document is read

        RETURNS: String

        If you're having run-time problems I feel bad for your son,
        I've got 99 problems but dependencies ain't one:

        http://code.google.com/p/tesseract-ocr/
        http://code.google.com/p/python-tesseract/


        """

        if(not OCR_ENABLED):
            return "Please install the correct OCR library required - http://code.google.com/p/tesseract-ocr/ http://code.google.com/p/python-tesseract/"
        
        api = tesseract.TessBaseAPI()
        api.SetOutputName("outputName")
        api.Init(".","eng",tesseract.OEM_DEFAULT)
        api.SetPageSegMode(tesseract.PSM_AUTO)


        jpgdata = StringIO()
        self.getPIL().save(jpgdata, "jpeg")
        jpgdata.seek(0)
        stringbuffer = jpgdata.read()
        result = tesseract.ProcessPagesBuffer(stringbuffer,len(stringbuffer),api)
        return result

    def findCircle(self,canny=100,thresh=350,distance=-1):
        """
        Perform the Hough Circle transform to extract _perfect_ circles from the image
        canny - the upper bound on a canny edge detector used to find circle edges.

        thresh - the threshold at which to count a circle. Small parts of a circle get
        added to the accumulator array used internally to the array. This value is the
        minimum threshold. Lower thresholds give more circles, higher thresholds give fewer circles.

        Warning: if this threshold is too high, and no circles are found the underlying OpenCV
        routine fails and causes a segfault. 
        
        distance - the minimum distance between each successive circle in pixels. 10 is a good
        starting value.

        returns: a circle feature set. 
        """
        storage = cv.CreateMat(self.width, 1, cv.CV_32FC3)
        #a distnace metric for how apart our circles should be - this is sa good bench mark
        if(distance < 0 ):
            distance = 1 + max(self.width,self.height)/50
        cv.HoughCircles(self._getGrayscaleBitmap(),storage, cv.CV_HOUGH_GRADIENT, 2, distance,canny,thresh)
        if storage.rows == 0:
            return None
        circs = np.asarray(storage)
        sz = circs.shape
        circleFS = FeatureSet()
        for i in range(sz[0]):
            circleFS.append(Circle(self,int(circs[i][0][0]),int(circs[i][0][1]),int(circs[i][0][2])))  
        return circleFS

    def whiteBalance(self,method="Simple"):
        """
        Attempts to perform automatic white balancing. 
        Gray World see: http://scien.stanford.edu/pages/labsite/2000/psych221/projects/00/trek/GWimages.html
        Robust AWB: http://scien.stanford.edu/pages/labsite/2010/psych221/projects/2010/JasonSu/robustawb.html
        http://scien.stanford.edu/pages/labsite/2010/psych221/projects/2010/JasonSu/Papers/Robust%20Automatic%20White%20Balance%20Algorithm%20using%20Gray%20Color%20Points%20in%20Images.pdf
        Simple AWB:
        http://www.ipol.im/pub/algo/lmps_simplest_color_balance/
        http://scien.stanford.edu/pages/labsite/2010/psych221/projects/2010/JasonSu/simplestcb.html
        """
        img = self
        if(method=="GrayWorld"):           
            avg = cv.Avg(img.getBitmap());
            bf = float(avg[0])
            gf = float(avg[1])
            rf = float(avg[2])
            af = (bf+gf+rf)/3.0
            if( bf == 0.00 ):
                b_factor = 1.00
            else:
                b_factor = af/bf

            if( gf == 0.00 ):
                g_factor = 1.00
            else:
                g_factor = af/gf

            if( rf == 0.00 ):
                r_factor = 1.00
            else:
                r_factor = af/rf
            
            b = img.getEmpty(1) 
            g = img.getEmpty(1) 
            r = img.getEmpty(1) 
            cv.Split(self.getBitmap(), b, g, r, None)
            bfloat = cv.CreateImage((img.width, img.height), cv.IPL_DEPTH_32F, 1) 
            gfloat = cv.CreateImage((img.width, img.height), cv.IPL_DEPTH_32F, 1) 
            rfloat = cv.CreateImage((img.width, img.height), cv.IPL_DEPTH_32F, 1) 
            
            cv.ConvertScale(b,bfloat,b_factor)
            cv.ConvertScale(g,gfloat,g_factor)
            cv.ConvertScale(r,rfloat,r_factor)
           
            (minB,maxB,minBLoc,maxBLoc) = cv.MinMaxLoc(bfloat)
            (minG,maxG,minGLoc,maxGLoc) = cv.MinMaxLoc(gfloat)
            (minR,maxR,minRLoc,maxRLoc) = cv.MinMaxLoc(rfloat)
            scale = max([maxR,maxG,maxB])
            sfactor = 1.00
            if(scale > 255 ):
                sfactor = 255.00/float(scale)

            cv.ConvertScale(bfloat,b,sfactor);
            cv.ConvertScale(gfloat,g,sfactor);
            cv.ConvertScale(rfloat,r,sfactor);
            
            retVal = img.getEmpty()
            cv.Merge(b,g,r,None,retVal);
            retVal = Image(retVal)
        elif( method == "Simple" ):
            thresh = 0.003
            sz = img.width*img.height
            tempMat = img.getNumpy() 
            bcf = sss.cumfreq(tempMat[:,:,0], numbins=256)
            bcf = bcf[0] # get our cumulative histogram of values for this color

            blb = -1 #our upper bound
            bub = 256 # our lower bound
            lower_thresh = 0.00
            upper_thresh = 0.00
            #now find the upper and lower thresh% of our values live
            while( lower_thresh < thresh ):
                blb = blb+1
                lower_thresh = bcf[blb]/sz
            while( upper_thresh < thresh ):
                bub = bub-1
                upper_thresh = (sz-bcf[bub])/sz


            gcf = sss.cumfreq(tempMat[:,:,1], numbins=256)
            gcf = gcf[0]
            glb = -1 #our upper bound
            gub = 256 # our lower bound
            lower_thresh = 0.00
            upper_thresh = 0.00
            #now find the upper and lower thresh% of our values live
            while( lower_thresh < thresh ):
                glb = glb+1
                lower_thresh = gcf[glb]/sz
            while( upper_thresh < thresh ):
                gub = gub-1
                upper_thresh = (sz-gcf[gub])/sz


            rcf = sss.cumfreq(tempMat[:,:,2], numbins=256)
            rcf = rcf[0]
            rlb = -1 #our upper bound
            rub = 256 # our lower bound
            lower_thresh = 0.00 
            upper_thresh = 0.00
            #now find the upper and lower thresh% of our values live
            while( lower_thresh < thresh ):
                rlb = rlb+1
                lower_thresh = rcf[rlb]/sz
            while( upper_thresh < thresh ):
                rub = rub-1
                upper_thresh = (sz-rcf[rub])/sz
            #now we create the scale factors for the remaining pixels
            rlbf = float(rlb)
            rubf = float(rub)
            glbf = float(glb)
            gubf = float(gub)
            blbf = float(blb)
            bubf = float(bub)

            rLUT = np.ones((256,1),dtype=uint8)
            gLUT = np.ones((256,1),dtype=uint8)
            bLUT = np.ones((256,1),dtype=uint8)
            for i in range(256):
                if(i <= rlb):
                    rLUT[i][0] = 0
                elif( i >= rub):
                    rLUT[i][0] = 255
                else:
                    rf = ((float(i)-rlbf)*255.00/(rubf-rlbf))
                    rLUT[i][0] = int(rf)
                if( i <= glb):
                    gLUT[i][0] = 0
                elif( i >= gub):
                    gLUT[i][0] = 255
                else:
                    gf = ((float(i)-glbf)*255.00/(gubf-glbf))
                    gLUT[i][0] = int(gf)
                if( i <= blb):
                    bLUT[i][0] = 0
                elif( i >= bub):
                    bLUT[i][0] = 255
                else:
                    bf = ((float(i)-blbf)*255.00/(bubf-blbf))
                    bLUT[i][0] = int(bf)
            retVal = img.applyLUT(bLUT,rLUT,gLUT)
        return retVal 
        
    def applyLUT(self,rLUT=None,bLUT=None,gLUT=None):
        """
        Apply LUT allows you to apply a LUT (look up table) to the pixels in a image. Each LUT is just 
        an array where each index in the array points to its value in the result image. For example 
        rLUT[0]=255 would change all pixels where the red channel is zero to the value 255.
        
        params:
        rLUT = a tuple or np.array of size (256x1) with dtype=uint8
        gLUT = a tuple or np.array of size (256x1) with dtype=uint8
        bLUT = a tuple or np.array of size (256x1) with dtype=uint8
        !The dtype is very important. Will throw the following error without it:
        
        error: dst.size() == src.size() && dst.type() == CV_MAKETYPE(lut.depth(), src.channels())
        
        
        returns:
        The image remapped using the LUT.
        
        example:
        This example saturates the red channel
        >>>> rlut = np.ones((256,1),dtype=uint8)*255
        >>>> img=img.applyLUT(rLUT=rlut)
       
        """
        r = self.getEmpty(1)
        g = self.getEmpty(1)
        b = self.getEmpty(1)
        cv.Split(self.getBitmap(),b,g,r,None);
        if(rLUT is not None):
            cv.LUT(r,r,cv.fromarray(rLUT))
        if(gLUT is not None):
            cv.LUT(g,g,cv.fromarray(gLUT))
        if(bLUT is not None):
            cv.LUT(b,b,cv.fromarray(bLUT))
        temp = self.getEmpty()
        cv.Merge(b,g,r,None,temp)
        return Image(temp)
        

    def _getRawKeypoints(self,thresh=500.00,flavor="SURF", highQuality=1, forceReset=False):
        """
        This method finds keypoints in an image and returns them as the raw keypoints
        and keypoint descriptors. When this method is called it caches a the features
        and keypoints locally for quick and easy access.
       
        Parameters:
        min_quality - The minimum quality metric for SURF descriptors. Good values
                      range between about 300.00 and 600.00
        
        flavor - a string indicating the method to use to extract features.
                 A good primer on how feature/keypoint extractiors can be found here:

                 http://en.wikipedia.org/wiki/Feature_detection_(computer_vision)
                 http://www.cg.tu-berlin.de/fileadmin/fg144/Courses/07WS/compPhoto/Feature_Detection.pdf
        

                 "SURF" - extract the SURF features and descriptors. If you don't know
                 what to use, use this. 
                 See: http://en.wikipedia.org/wiki/SURF

                 "STAR" - The STAR feature extraction algorithm
                 See: http://pr.willowgarage.com/wiki/Star_Detector

                 "FAST" - The FAST keypoint extraction algorithm
                 See: http://en.wikipedia.org/wiki/Corner_detection#AST_based_feature_detectors


        highQuality - The SURF descriptor comes in two forms, a vector of 64 descriptor 
                      values and a vector of 128 descriptor values. The latter are "high" 
                      quality descriptors. 
                     
        forceReset - If keypoints have already been calculated for this image those
                     keypoints are returned veresus recalculating the values. If 
                     force reset is True we always recalculate the values, otherwise
                     we will used the cached copies. 
                      
        Returns:
        A tuple of keypoint objects and optionally a numpy array of the descriptors. 

        Example:
        >>>> img = Image("aerospace.jpg")
        >>>> kp,d = img._getRawKeypoints() 

        Notes:
        If you would prefer to work with the raw keypoints and descriptors each image keeps
        a local cache of the raw values. These are named:
        
        self._mKeyPoints # A tuple of keypoint objects
        See: http://opencv.itseez.com/modules/features2d/doc/common_interfaces_of_feature_detectors.html#keypoint-keypoint
        self._mKPDescriptors # The descriptor as a floating point numpy array
        self._mKPFlavor = "NONE" # The flavor of the keypoints as a string. 

        See Also:
         ImageClass._getRawKeypoints(self,thresh=500.00,forceReset=False,flavor="SURF",highQuality=1)
         ImageClass._getFLANNMatches(self,sd,td)
         ImageClass.findKeypointMatch(self,template,quality=500.00,minDist=0.2,minMatch=0.4)
         ImageClass.drawKeypointMatches(self,template,thresh=500.00,minDist=0.15,width=1)

        """
        if( forceReset ):
            self._mKeyPoints = None
            self._mKPDescriptors = None
        if( self._mKeyPoints is None or self._mKPFlavor != flavor ):
            if( flavor == "SURF" ):
                surfer = cv2.SURF(thresh,_extended=highQuality,_upright=1) 
                self._mKeyPoints,self._mKPDescriptors = surfer.detect(self.getGrayNumpy(),None,False)
                if( len(self._mKPDescriptors) == 0 ):
                    return None, None                     
                
                if( highQuality == 1 ):
                    self._mKPDescriptors = self._mKPDescriptors.reshape((-1,128))
                else:
                    self._mKPDescriptors = self._mKPDescriptors.reshape((-1,64))
                
                self._mKPFlavor = "SURF"
                del surfer
            
            elif( flavor == "FAST" ):
                faster = cv2.FastFeatureDetector(threshold=int(thresh),nonmaxSuppression=True)
                self._mKeyPoints = faster.detect(self.getGrayNumpy())
                self._mKPDescriptors = None
                self._mKPFlavor = "FAST"
                del faster

            #elif( flavor == "MSER"):
            #    mserer = cv2.MSER()
            #    self._mKeyPoints = mserer.detect(self.getGrayNumpy(),None)
            #    self._mKPDescriptors = None
            #    self._mKPFlavor = "MSER"
            #    del mserer

            elif( flavor == "STAR"):
                starer = cv2.StarDetector()
                self._mKeyPoints = starer.detect(self.getGrayNumpy())
                self._mKPDescriptors = None
                self._mKPFlavor = "STAR"
                del starer
          
            else:
                warnings.warn("ImageClass.Keypoints: I don't know the method you want to use")
                return None, None

        return self._mKeyPoints,self._mKPDescriptors 

    def _getFLANNMatches(self,sd,td):
        """
        Summary:
        This method does a fast local approximate nearest neighbors (FLANN) calculation between two sets
        of feature vectors. The result are two numpy arrays the first one is a list of indexes of the
        matches and the second one is the match distance value. For the match indices or idx, the index
        values correspond to the values of td, and the value in the array is the index in td. I.
        I.e. j = idx[i] is where td[i] matches sd[j]. 
        The second numpy array, at the index i is the match distance between td[i] and sd[j].
        Lower distances mean better matches. 

        Parameters:
        sd - A numpy array of feature vectors of any size.
        td - A numpy array of feature vectors of any size, this vector is used for indexing
             and the result arrays will have a length matching this vector. 

        Returns:
        Two numpy arrays, the first one, idx, is the idx of the matches of the vector td with sd.
        The second one, dist, is the distance value for the closest match.

        Example:
        >>>> kpt,td = img1._getRawKeypoints() # t is template
        >>>> kps,sd = img2._getRawKeypoints() # s is source
        >>>> idx,dist = img1._getFLANNMatches(sd,td)
        >>>> j = idx[42]
        >>>> print kps[j] # matches kp 42
        >>>> print dist[i] # the match quality.

        Notes:
        If you would prefer to work with the raw keypoints and descriptors each image keeps
        a local cache of the raw values. These are named:
        
        self._mKeyPoints # A tuple of keypoint objects
        See: http://opencv.itseez.com/modules/features2d/doc/common_interfaces_of_feature_detectors.html#keypoint-keypoint
        self._mKPDescriptors # The descriptor as a floating point numpy array
        self._mKPFlavor = "NONE" # The flavor of the keypoints as a string. 

        See:
         ImageClass._getRawKeypoints(self,thresh=500.00,forceReset=False,flavor="SURF",highQuality=1)
         ImageClass._getFLANNMatches(self,sd,td)
         ImageClass.drawKeypointMatches(self,template,thresh=500.00,minDist=0.15,width=1)
         ImageClass.findKeypoints(self,min_quality=300.00,flavor="SURF",highQuality=False ) 
         ImageClass.findKeypointMatch(self,template,quality=500.00,minDist=0.2,minMatch=0.4)
        """
        FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
        flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 4)
        flann = cv2.flann_Index(sd, flann_params)
        idx, dist = flann.knnSearch(td, 1, params = {}) # bug: need to provide empty dict
        del flann
        return idx,dist

    def drawKeypointMatches(self,template,thresh=500.00,minDist=0.15,width=1):
        """
        Summary:
        Draw keypoints draws a side by side representation of two images, calculates
        keypoints for both images, determines the keypoint correspondences, and then draws
        the correspondences. This method is helpful for debugging keypoint calculations
        and also looks really cool :) .  The parameters mirror the parameters used 
        for findKeypointMatches to assist with debugging 

        Parameters:
        template - A template image. 

        quality - The feature quality metric. This can be any value between about 300 and 500. Higher
        values should return fewer, but higher quality features. 

        minDist - The value below which the feature correspondence is considered a match. This 
                  is the distance between two feature vectors. Good values are between 0.05 and 0.3

        width    - The width of the drawn line.

        Returns:
        A side by side image of the template and source image with each feature correspondence 
        draw in a different color. 

        Example:
        >>>> img = cam.getImage()
        >>>> template = Image("myTemplate.png")
        >>>> result = img.drawKeypointMatches(self,template,300.00,0.4):

        Notes:
        If you would prefer to work with the raw keypoints and descriptors each image keeps
        a local cache of the raw values. These are named:
        
        self._mKeyPoints # A tuple of keypoint objects
        See: http://opencv.itseez.com/modules/features2d/doc/common_interfaces_of_feature_detectors.html#keypoint-keypoint
        self._mKPDescriptors # The descriptor as a floating point numpy array
        self._mKPFlavor = "NONE" # The flavor of the keypoints as a string. 

        See:
         ImageClass._getRawKeypoints(self,thresh=500.00,forceReset=False,flavor="SURF",highQuality=1)
         ImageClass._getFLANNMatches(self,sd,td)
         ImageClass.drawKeypointMatches(self,template,thresh=500.00,minDist=0.15,width=1)
         ImageClass.findKeypoints(self,min_quality=300.00,flavor="SURF",highQuality=False ) 
         ImageClass.findKeypointMatch(self,template,quality=500.00,minDist=0.2,minMatch=0.4)

        """
        if template == None:
          return None
          
        resultImg = template.sideBySide(self,scale=False)
        hdif = (self.height-template.height)/2
        skp,sd = self._getRawKeypoints(thresh)
        tkp,td = template._getRawKeypoints(thresh)
        if( td == None or sd == None ):
            warnings.warn("We didn't get any descriptors. Image might be too uniform or blurry." )
            return resultImg
        template_points = float(td.shape[0])
        sample_points = float(sd.shape[0])
        magic_ratio = 1.00
        if( sample_points > template_points ):
            magic_ratio = float(sd.shape[0])/float(td.shape[0])

        idx,dist = self._getFLANNMatches(sd,td) # match our keypoint descriptors
        p = dist[:,0]
        result = p*magic_ratio < minDist #, = np.where( p*magic_ratio < minDist ) 
        for i in range(0,len(idx)):
            if( result[i] ):
                pt_a = (tkp[i].pt[1], tkp[i].pt[0]+hdif)
                pt_b = (skp[idx[i]].pt[1]+template.width,skp[idx[i]].pt[0])
                resultImg.drawLine(pt_a,pt_b,color=Color.getRandom(Color()),thickness=width)
        return resultImg
                  

    def findKeypointMatch(self,template,quality=500.00,minDist=0.2,minMatch=0.4):
        """
        findKeypointMatch allows you to match a template image with another image using 
        SURF keypoints. The method extracts keypoints from each image, uses the Fast Local
        Approximate Nearest Neighbors algorithm to find correspondences between the feature
        points, filters the correspondences based on quality, and then, attempts to calculate
        a homography between the two images. This homography allows us to draw a matching
        bounding box in the source image that corresponds to the template. This method allows
        you to perform matchs the ordinarily fail when using the findTemplate method. 
        This method should be able to handle a reasonable changes in camera orientation and
        illumination. Using a template that is close to the target image will yield much
        better results.

        Warning:
        This method is only capable of finding one instance of the template in an image. 
        If more than one instance is visible the homography calculation and the method will 
        fail.

        Parameters:
        template - A template image. 

        quality - The feature quality metric. This can be any value between about 300 and 500. Higher
        values should return fewer, but higher quality features. 

        minDist - The value below which the feature correspondence is considered a match. This 
                  is the distance between two feature vectors. Good values are between 0.05 and 0.3

        minMatch - The percentage of features which must have matches to proceed with homography calculation.
                   A value of 0.4 means 40% of features must match. Higher values mean better matches
                   are used. Good values are between about 0.3 and 0.7
 
        Returns:
                  If a homography (match) is found this method returns a feature set with a single 
                  KeypointMatch feature. If no match is found None is returned.
        Example:
                  >>>> template = Image("template.png")
                  >>>> img = camera.getImage()
                  >>>> fs = img.findKeypointMatch(template)
                  >>>> if( fs is not None ):
                  >>>>      fs[0].draw()
                  >>>>      img.show()

        Notes:
        If you would prefer to work with the raw keypoints and descriptors each image keeps
        a local cache of the raw values. These are named:
        
        self._mKeyPoints # A tuple of keypoint objects
        See: http://opencv.itseez.com/modules/features2d/doc/common_interfaces_of_feature_detectors.html#keypoint-keypoint
        self._mKPDescriptors # The descriptor as a floating point numpy array
        self._mKPFlavor = "NONE" # The flavor of the keypoints as a string. 

        See Also:
         ImageClass._getRawKeypoints(self,thresh=500.00,forceReset=False,flavor="SURF",highQuality=1)
         ImageClass._getFLANNMatches(self,sd,td)
         ImageClass.drawKeypointMatches(self,template,thresh=500.00,minDist=0.15,width=1)
         ImageClass.findKeypoints(self,min_quality=300.00,flavor="SURF",highQuality=False ) 


        """
        if template == None:
          return None
        
        skp,sd = self._getRawKeypoints(quality)
        tkp,td = template._getRawKeypoints(quality)
        if( skp == None or tkp == None ):
            warnings.warn("I didn't get any keypoints. Image might be too uniform or blurry." )
            return None

        template_points = float(td.shape[0])
        sample_points = float(sd.shape[0])
        magic_ratio = 1.00
        if( sample_points > template_points ):
            magic_ratio = float(sd.shape[0])/float(td.shape[0])

        idx,dist = self._getFLANNMatches(sd,td) # match our keypoint descriptors
        p = dist[:,0]
        result = p*magic_ratio < minDist #, = np.where( p*magic_ratio < minDist ) 
        pr = result.shape[0]/float(dist.shape[0])

        if( pr >  minMatch and len(result)>4 ): # if more than minMatch % matches we go ahead and get the data 
            lhs = []
            rhs = []
            for i in range(0,len(idx)):
                if( result[i] ):
                    lhs.append((tkp[i].pt[0], tkp[i].pt[1]))
                    rhs.append((skp[idx[i]].pt[0], skp[idx[i]].pt[1]))
            
            rhs_pt = np.array(rhs)
            lhs_pt = np.array(lhs)
            if( len(rhs_pt) < 16  or len(lhs_pt) < 16 ):
                return None
            homography = []         
            (homography,mask) = cv2.findHomography(lhs_pt,rhs_pt,cv2.RANSAC, ransacReprojThreshold=1.0 )
            w = template.width
            h = template.height
            yo = homography[0][2] # get the x/y offset from the affine transform
            xo = homography[1][2]
            # draw our template
            pt0 = np.array([0,0,1]) 
            pt1 = np.array([0,h,1])
            pt2 = np.array([w,h,1])
            pt3 = np.array([w,0,1])
            # apply the affine transform to our points
            pt0p = np.array(pt0*np.matrix(homography)) 
            pt1p = np.array(pt1*np.matrix(homography))
            pt2p = np.array(pt2*np.matrix(homography))
            pt3p = np.array(pt3*np.matrix(homography))
            #update and clamp the corners to get our template in the other image
            pt0i = (abs(pt0p[0][0]+xo),abs(pt0p[0][1]+yo)) 
            pt1i = (abs(pt1p[0][0]+xo),abs(pt1p[0][1]+yo))
            pt2i = (abs(pt2p[0][0]+xo),abs(pt2p[0][1]+yo))
            pt3i = (abs(pt3p[0][0]+xo),abs(pt3p[0][1]+yo))
            #construct the feature set and return it. 
            fs = FeatureSet()
            fs.append(KeypointMatch(self,template,(pt0i,pt1i,pt2i,pt3i),homography))
            return fs
        else:
            return None 


    def findKeypoints(self,min_quality=300.00,flavor="SURF",highQuality=False ): 
        """
        This method finds keypoints in an image and returns them as a feature set.
        Keypoints are unique regions in an image that demonstrate some degree of 
        invariance to changes in camera pose and illumination. They are helpful
        for calculating homographies between camera views, object rotations, and
        multiple view overlaps.

        We support four keypoint detectors and only one form of keypoint descriptors.
        Only the surf flavor of keypoint returns feature and descriptors at this time.
       
        Parameters:
        min_quality - The minimum quality metric for SURF descriptors. Good values
                      range between about 300.00 and 600.00
        
        flavor - a string indicating the method to use to extract features.
                 A good primer on how feature/keypoint extractiors can be found here:

                 http://en.wikipedia.org/wiki/Feature_detection_(computer_vision)
                 http://www.cg.tu-berlin.de/fileadmin/fg144/Courses/07WS/compPhoto/Feature_Detection.pdf
        

                 "SURF" - extract the SURF features and descriptors. If you don't know
                 what to use, use this. 
                 See: http://en.wikipedia.org/wiki/SURF

                 "STAR" - The STAR feature extraction algorithm
                 See: http://pr.willowgarage.com/wiki/Star_Detector

                 "FAST" - The FAST keypoint extraction algorithm
                 See: http://en.wikipedia.org/wiki/Corner_detection#AST_based_feature_detectors


        highQuality - The SURF descriptor comes in two forms, a vector of 64 descriptor 
                      values and a vector of 128 descriptor values. The latter are "high" 
                      quality descriptors. 
                      
        Returns:
        A feature set of KeypointFeatures. These KeypointFeatures let's you draw each 
        feature, crop the features, get the feature descriptors, etc. 

        Example:
        >>>> img = Image("aerospace.jpg")
        >>>> fs = img.findKeypoints(flavor="SURF",min_quality=500,highQuality=True)
        >>>> fs = fs.sortArea()
        >>>> fs[-1].draw()
        >>>> img.draw()

        Notes:
        If you would prefer to work with the raw keypoints and descriptors each image keeps
        a local cache of the raw values. These are named:
        
        self._mKeyPoints # A tuple of keypoint objects
        See: http://opencv.itseez.com/modules/features2d/doc/common_interfaces_of_feature_detectors.html#keypoint-keypoint
        self._mKPDescriptors # The descriptor as a floating point numpy array
        self._mKPFlavor = "NONE" # The flavor of the keypoints as a string. 

        See Also:
         ImageClass._getRawKeypoints(self,thresh=500.00,forceReset=False,flavor="SURF",highQuality=1)
         ImageClass._getFLANNMatches(self,sd,td)
         ImageClass.findKeypointMatch(self,template,quality=500.00,minDist=0.2,minMatch=0.4)
         ImageClass.drawKeypointMatches(self,template,thresh=500.00,minDist=0.15,width=1)

        """
        fs = FeatureSet()
        kp = []
        d = []
        if highQuality:
            kp,d = self._getRawKeypoints(thresh=min_quality,forceReset=True,flavor=flavor,highQuality=1)
        else:
            kp,d = self._getRawKeypoints(thresh=min_quality,forceReset=True,flavor=flavor,highQuality=0)

        if( flavor == "SURF" ):
            for i in range(0,len(kp)):
                fs.append(KeyPoint(self,kp[i],d[i],flavor))
        elif(flavor == "STAR" or flavor == "FAST" ):
            for i in range(0,len(kp)):
                fs.append(KeyPoint(self,kp[i],None,flavor))
        else:
            warnings.warn("ImageClass.Keypoints: I don't know the method you want to use")
            return None

        return fs

    def findMotion(self, previous_frame, window=11, method='BM', aggregate=True):
        """
        findMotion - perform an optical flow calculation. This method attempts to find 
                     motion between two subsequent frames of an image. You provide it 
                     with the previous frame image and it returns a feature set of motion
                     fetures that are vectors in the direction of motion.

        previous_frame - The last frame as an Image. 

        window         - The block size for the algorithm. For the the HS and LK methods 
                         this is the regular sample grid at which we return motion samples.
                         For the block matching method this is the matching window size.

        method         - The algorithm to use as a string. Your choices are:
                         'BM' - default block matching robust but slow - if you are unsure use this.
                         'LK' - Lucas-Kanade method - http://en.wikipedia.org/wiki/Lucas%E2%80%93Kanade_method 
                         'HS' - Horn-Schunck method - http://en.wikipedia.org/wiki/Horn%E2%80%93Schunck_method


        aggregate      - If aggregate is true, each of our motion features is the average of
                         motion around the sample grid defined by window. If aggregate is false
                         we just return the the value as sampled at the window grid interval. For 
                         block matching this flag is ignored.
        """
        if( self.width != previous_frame.width or self.height != previous_frame.height):
            warnings.warn("ImageClass.getMotion: To find motion the current and previous frames must match")
            return None
        fs = FeatureSet()
        max_mag = 0.00

        if( method == "LK" or method == "HS" ):
            # create the result images. 
            xf = cv.CreateImage((self.width, self.height), cv.IPL_DEPTH_32F, 1) 
            yf = cv.CreateImage((self.width, self.height), cv.IPL_DEPTH_32F, 1)         
            win = (window,window)
            if( method == "LK" ):
                cv.CalcOpticalFlowLK(self._getGrayscaleBitmap(),previous_frame._getGrayscaleBitmap(),win,xf,yf)
            else:
                cv.CalcOpticalFlowHS(previous_frame._getGrayscaleBitmap(),self._getGrayscaleBitmap(),0,xf,yf,1.0,(cv.CV_TERMCRIT_ITER | cv.CV_TERMCRIT_EPS, 10, 0.01))
                
            w = math.floor((float(window))/2.0) 
            cx = ((self.width-window)/window)+1 #our sample rate
            cy = ((self.height-window)/window)+1
            vx = 0.00
            vy = 0.00
            for x in range(0,int(cx)): # go through our sample grid
                for y in range(0,int(cy)): 
                    xi = (x*window)+w # calculate the sample point
                    yi = (y*window)+w
                    if( aggregate ):
                        lowx = int(xi-w)
                        highx = int(xi+w)
                        lowy = int(yi-w)
                        highy = int(yi+w)
                        xderp = xf[lowy:highy,lowx:highx] # get the average x/y components in the output
                        yderp = yf[lowy:highy,lowx:highx]
                        vx = np.average(xderp)
                        vy = np.average(yderp)
                    else: # other wise just sample
                        vx = xf[yi,xi]
                        vy = yf[yi,xi]
 
                    mag = (vx*vx)+(vy*vy)
                    if(mag > max_mag): # calculate the max magnitude for normalizing our vectors
                        max_mag = mag
                    fs.append(Motion(self,xi,yi,vx,vy,window)) # add the sample to the feature set

        elif( method == "BM"):
            # In the interest of keep the parameter list short
            # I am pegging these to the window size. 
            block = (window,window) # block size
            shift = (int(window*1.2),int(window*1.2)) # how far to shift the block
            spread = (window*2,window*2) # the search windows.
            wv = (self.width - block[0]) / shift[0] # the result image size
            hv = (self.height - block[1]) / shift[1]
            xf = cv.CreateMat(hv, wv, cv.CV_32FC1)
            yf = cv.CreateMat(hv, wv, cv.CV_32FC1)
            cv.CalcOpticalFlowBM(previous_frame._getGrayscaleBitmap(),self._getGrayscaleBitmap(),block,shift,spread,0,xf,yf)
            for x in range(0,int(wv)): # go through the sample grid
                for y in range(0,int(hv)):
                    xi = (shift[0]*(x))+block[0] #where on the input image the samples live
                    yi = (shift[1]*(y))+block[1]
                    vx = xf[y,x] # the result image values
                    vy = yf[y,x]
                    fs.append(Motion(self,xi,yi,vx,vy,window)) # add the feature
                    mag = (vx*vx)+(vy*vy) # same the magnitude
                    if(mag > max_mag):
                        max_mag = mag
        else:
            warnings.warn("ImageClass.findMotion: I don't know what algorithm you want to use. Valid method choices are Block Matching -> \"BM\" Horn-Schunck -> \"HS\" and Lucas-Kanade->\"LK\" ") 
            return None
	
        max_mag = math.sqrt(max_mag) # do the normalization
        for f in fs:
            f.normalizeTo(max_mag)

        return fs


    
    def _generatePalette(self,bins,hue):
        """
        Summary:
        This is the main entry point for palette generation. A palette, for our purposes,
        is a list of the main colors in an image. Creating a palette with 10 bins, tries 
        to cluster the colors in rgb space into ten distinct groups. In hue space we only
        look at the hue channel. All of the relevant palette data is cached in the image 
        class. 

        Parameters:
        bins - an integer number of bins into which to divide the colors in the image.
        hue  - if hue is true we do only cluster on the image hue values. 

        Returns:
        Nothing, but creates the image's cached values for: 
        
        self._mDoHuePalette
        self._mPaletteBins
        self._mPalette 
        self._mPaletteMembers 
        self._mPalettePercentages


        Example:
        
        >>>> img._generatePalette(bins=42)

        Notes:
        The hue calculations should be siginificantly faster than the generic RGB calculation as 
        it works in a one dimensional space. Sometimes the underlying scipy method freaks out 
        about k-means initialization with the following warning:
        
        UserWarning: One of the clusters is empty. Re-run kmean with a different initialization.

        This shouldn't be a real problem. 
        
        See Also:
        ImageClass.getPalette(self,bins=10,hue=False
        ImageClass.rePalette(self,palette,hue=False):
        ImageClass.drawPaletteColors(self,size=(-1,-1),horizontal=True,bins=10,hue=False)
        ImageClass.palettize(self,bins=10,hue=False)
        ImageClass.binarizeFromPalette(self, palette_selection)
        ImageClass.findBlobsFromPalette(self, palette_selection, dilate = 0, minsize=5, maxsize=0)
        """
        if( self._mPaletteBins != bins or
            self._mDoHuePalette != hue ):
            total = float(self.width*self.height)
            percentages = []
            result = None
            if( not hue ):
                pixels = np.array(self.getNumpy()).reshape(-1, 3)   #reshape our matrix to 1xN
                result = scv.kmeans2(pixels,bins)

            else:
                hsv = self
                if( self._colorSpace != ColorSpace.HSV ):
                    hsv = self.toHSV()
                
                h = hsv.getEmpty(1)       
                cv.Split(hsv.getBitmap(),None,None,h,None)
                mat =  cv.GetMat(h)
                pixels = np.array(mat).reshape(-1,1)
                result = scv.kmeans2(pixels,bins)                


            for i in range(0,bins):
                count = np.where(result[1]==i)
                v = float(count[0].shape[0])/total
                percentages.append(v)

            self._mDoHuePalette = hue
            self._mPaletteBins = bins
            self._mPalette = np.array(result[0],dtype='uint8')
            self._mPaletteMembers = result[1]
            self._mPalettePercentages = percentages


    def getPalette(self,bins=10,hue=False):
        """
        Summary:
        This method returns the colors in the palette of the image. A palette is the 
        set of the most common colors in an image. This method is helpful for segmentation.

        Parameters:
        bins - an integer number of bins into which to divide the colors in the image.
        hue  - if hue is true we do only cluster on the image hue values. 

        Returns:
        an numpy array of the BGR color tuples. 

        Example:
        
        >>>> p = img.getPalette(bins=42)
        >>>> print p[2]
       
        Notes:
        The hue calculations should be siginificantly faster than the generic RGB calculation as 
        it works in a one dimensional space. Sometimes the underlying scipy method freaks out 
        about k-means initialization with the following warning:
        
        UserWarning: One of the clusters is empty. Re-run kmean with a different initialization.

        This shouldn't be a real problem. 
        
        See Also:
        
        ImageClass.rePalette(self,palette,hue=False):
        ImageClass.drawPaletteColors(self,size=(-1,-1),horizontal=True,bins=10,hue=False)
        ImageClass.palettize(self,bins=10,hue=False)
        ImageClass.binarizeFromPalette(self, palette_selection)
        ImageClass.findBlobsFromPalette(self, palette_selection, dilate = 0, minsize=5, maxsize=0)
        """
        self._generatePalette(bins,hue)
        return self._mPalette


    def rePalette(self,palette,hue=False):
        retVal = None
        if(hue):
            hsv = self
            if( self._colorSpace != ColorSpace.HSV ):
                hsv = self.toHSV()
                
            h = hsv.getEmpty(1)       
            cv.Split(hsv.getBitmap(),None,None,h,None)
            mat =  cv.GetMat(h)
            pixels = np.array(mat).reshape(-1,1)
            result = scv.vq(pixels,palette)
            derp = palette[result[0]]
            retVal = Image(derp[::-1].reshape(self.height,self.width)[::-1])
            retVal = retVal.rotate(-90,fixed=False)
        else:
            result = scv.vq(self.getNumpy().reshape(-1,3),palette)
            retVal = Image(palette[result[0]].reshape(self.width,self.height,3))
        return retVal

    def drawPaletteColors(self,size=(-1,-1),horizontal=True,bins=10,hue=False):
        """
        Summary:
        This method returns the visual representation (swatches) of the palette in an image. The palette 
        is orientated either horizontally or vertically, and each color is given an area 
        proportional to the number of pixels that have that color in the image. The palette 
        is arranged as it is returned from the clustering algorithm. When size is left
        to its default value, the palette size will match the size of the 
        orientation, and then be 10% of the other dimension. E.g. if our image is 640X480 the horizontal
        palette will be (640x48) likewise the vertical palette will be (480x64)
        
        If a Hue palette is used this method will return a grayscale palette
        
        Parameters:
        bins      - an integer number of bins into which to divide the colors in the image.
        hue       - if hue is true we do only cluster on the image hue values. 
        size      - The size of the generated palette as a (width,height) tuple, if left default we select 
                    a size based on the image so it can be nicely displayed with the 
                    image. 
        horizontal- If true we orientate our palette horizontally, otherwise vertically. 

        Returns:
        A palette swatch image. 

        Example:
        
        >>>> p = img1.drawPaletteColors()
        >>>> img2 = img1.sideBySide(p,side="bottom")
        >>>> img2.show()

        Notes:
        The hue calculations should be siginificantly faster than the generic RGB calculation as 
        it works in a one dimensional space. Sometimes the underlying scipy method freaks out 
        about k-means initialization with the following warning:
        
        UserWarning: One of the clusters is empty. Re-run kmean with a different initialization.

        This shouldn't be a real problem. 
        
        See Also:
        ImageClass.getPalette(self,bins=10,hue=False
        ImageClass.rePalette(self,palette,hue=False):
        ImageClass.drawPaletteColors(self,size=(-1,-1),horizontal=True,bins=10,hue=False)
        ImageClass.palettize(self,bins=10,hue=False)
        ImageClass.binarizeFromPalette(self, palette_selection)
        ImageClass.findBlobsFromPalette(self, palette_selection, dilate = 0, minsize=5, maxsize=0)
        """
        self._generatePalette(bins,hue)
        retVal = None
        if( not hue ):
            if( horizontal ):
                if( size[0] == -1 or size[1] == -1 ):
                    size = (int(self.width),int(self.height*.1))
                pal = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3) 
                cv.Zero(pal)
                idxL = 0
                idxH = 0
                for i in range(0,bins):
                    idxH =np.clip(idxH+(self._mPalettePercentages[i]*float(size[0])),0,size[0]-1)
                    roi = (int(idxL),0,int(idxH-idxL),size[1])
                    cv.SetImageROI(pal,roi)
                    color = np.array((float(self._mPalette[i][2]),float(self._mPalette[i][1]),float(self._mPalette[i][0])))
                    cv.AddS(pal,color,pal)
                    cv.ResetImageROI(pal)
                    idxL = idxH
                retVal = Image(pal)
            else:
                if( size[0] == -1 or size[1] == -1 ):
                    size = (int(self.width*.1),int(self.height))
                pal = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3) 
                cv.Zero(pal)
                idxL = 0
                idxH = 0
                for i in range(0,bins):
                    idxH =np.clip(idxH+self._mPalettePercentages[i]*size[1],0,size[1]-1)
                    roi = (0,int(idxL),size[0],int(idxH-idxL))
                    cv.SetImageROI(pal,roi)
                    color = np.array((float(self._mPalette[i][2]),float(self._mPalette[i][1]),float(self._mPalette[i][0])))
                    cv.AddS(pal,color,pal)
                    cv.ResetImageROI(pal)
                    idxL = idxH
                retVal = Image(pal)
        else: # do hue
            if( horizontal ):
                if( size[0] == -1 or size[1] == -1 ):
                    size = (int(self.width),int(self.height*.1))
                pal = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1) 
                cv.Zero(pal)
                idxL = 0
                idxH = 0
                for i in range(0,bins):
                    idxH =np.clip(idxH+(self._mPalettePercentages[i]*float(size[0])),0,size[0]-1)
                    roi = (int(idxL),0,int(idxH-idxL),size[1])
                    cv.SetImageROI(pal,roi)
                    cv.AddS(pal,self._mPalette[i],pal)
                    cv.ResetImageROI(pal)
                    idxL = idxH
                retVal = Image(pal)
            else:
                if( size[0] == -1 or size[1] == -1 ):
                    size = (int(self.width*.1),int(self.height))
                pal = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1) 
                cv.Zero(pal)
                idxL = 0
                idxH = 0
                for i in range(0,bins):
                    idxH =np.clip(idxH+self._mPalettePercentages[i]*size[1],0,size[1]-1)
                    roi = (0,int(idxL),size[0],int(idxH-idxL))
                    cv.SetImageROI(pal,roi)
                    cv.AddS(pal,self._mPalette[i],pal)
                    cv.ResetImageROI(pal)
                    idxL = idxH
                retVal = Image(pal)
                 
        return retVal 

    def palettize(self,bins=10,hue=False):
        """
        Summary:
        This method analyzes an image and determines the most common colors using a k-means algorithm.
        The method then goes through and replaces each pixel with the centroid of the clutsters found
        by k-means. This reduces the number of colors in an image to the number of bins. This can be particularly
        handy for doing segementation based on color.

        Parameters:
        bins      - an integer number of bins into which to divide the colors in the image.
        hue       - if hue is true we do only cluster on the image hue values. 
        

        Returns:
        An image matching the original where each color is replaced with its palette value.  

        Example:
        
        >>>> img2 = img1.palettize()
        >>>> img2.show()

        Notes:
        The hue calculations should be siginificantly faster than the generic RGB calculation as 
        it works in a one dimensional space. Sometimes the underlying scipy method freaks out 
        about k-means initialization with the following warning:
        
        UserWarning: One of the clusters is empty. Re-run kmean with a different initialization.

        This shouldn't be a real problem. 
        
        See Also:
        ImageClass.getPalette(self,bins=10,hue=False
        ImageClass.rePalette(self,palette,hue=False):
        ImageClass.drawPaletteColors(self,size=(-1,-1),horizontal=True,bins=10,hue=False)
        ImageClass.palettize(self,bins=10,hue=False)
        ImageClass.binarizeFromPalette(self, palette_selection)
        ImageClass.findBlobsFromPalette(self, palette_selection, dilate = 0, minsize=5, maxsize=0)

        """
        retVal = None
        self._generatePalette(bins,hue)
        if( hue ):
            derp = self._mPalette[self._mPaletteMembers]
            retVal = Image(derp[::-1].reshape(self.height,self.width)[::-1])
            retVal = retVal.rotate(-90,fixed=False)
        else:
            retVal = Image(self._mPalette[self._mPaletteMembers].reshape(self.width,self.height,3))
        return retVal 


    def findBlobsFromPalette(self, palette_selection, dilate = 0, minsize=5, maxsize=0):
        """
        Description:
        This method attempts to use palettization to do segmentation and behaves similar to the 
        findBlobs blob in that it returs a feature set of blob objects. Once a palette has been 
        extracted using getPalette() we can then select colors from that palette to be labeled 
        white within our blobs. 

        Parameters:
        palette_selection - color triplets selected from our palette that will serve turned into blobs
                            These values can either be a 3xN numpy array, or a list of RGB triplets.

        dilate            - the optional number of dilation operations to perform on the binary image
                            prior to performing blob extraction.
        minsize           - the minimum blob size in pixels
        maxsize           - the maximim blob size in pixels.

        Returns:
        If the method executes successfully a FeatureSet of Blobs is returned from the image. If the method 
        fails a value of None is returned. 

        Example:
        >>>> img = Image("lenna")
        >>>> p = img.getPalette()
        >>>> blobs = img.findBlobsFromPalette( (p[0],p[1],[6]) )
        >>>> blobs.draw()
        >>>> img.show()

        Notes: 

        See Also:
        ImageClass.getPalette(self,bins=10,hue=False
        ImageClass.rePalette(self,palette,hue=False):
        ImageClass.drawPaletteColors(self,size=(-1,-1),horizontal=True,bins=10,hue=False)
        ImageClass.palettize(self,bins=10,hue=False)
        ImageClass.binarizeFromPalette(self, palette_selection)
        ImageClass.findBlobsFromPalette(self, palette_selection, dilate = 0, minsize=5, maxsize=0,)
        """

        #we get the palette from find palete 
        #ASSUME: GET PALLETE WAS CALLED!
        if( self._mPalette == None ):
            warning.warn("No palette exists, call getPalette())")
            return None
        img = self.palettize(self._mPaletteBins)
        npimg = img.getNumpy()
        white = np.array([255,255,255])
        black = np.array([0,0,0])

        for p in palette_selection:
            npimg = np.where(npimg != p,npimg,white)
            
        npimg = np.where(npimg != white,black,white)
        bwimg = Image(npimg)
        if( dilate > 0 ):
            bwimg =bwimg.dilate(dilate)
        
        if (maxsize == 0):  
            maxsize = self.width * self.height / 2
        #create a single channel image, thresholded to parameters
    
        blobmaker = BlobMaker()
        blobs = blobmaker.extractFromBinary(bwimg,
            self, minsize = minsize, maxsize = maxsize)
    
        if not len(blobs):
            return None


    def binarizeFromPalette(self, palette_selection):
        """
        Description:
        This method uses the color palette to generate a binary (black and white) image. Palaette selection
        is a list of color tuples retrieved from img.getPalette(). The provided values will be drawn white
        while other values will be black. 

        Parameters:
        palette_selection - color triplets selected from our palette that will serve turned into blobs
                            These values can either be a 3xN numpy array, or a list of RGB triplets.

        Returns:
        This method returns a black and white images, where colors that are close to the colors
        in palette_selection are set to white

        Example:
        >>>> img = Image("lenna")
        >>>> p = img.getPalette()
        >>>> b = img.binarizeFromPalette( (p[0],p[1],[6]) )
        >>>> b.show()

        Notes: 

        See Also:
        ImageClass.getPalette(self,bins=10,hue=False
        ImageClass.rePalette(self,palette,hue=False):
        ImageClass.drawPaletteColors(self,size=(-1,-1),horizontal=True,bins=10,hue=False)
        ImageClass.palettize(self,bins=10,hue=False)
        ImageClass.findBlobsFromPalette(self, palette_selection, dilate = 0, minsize=5, maxsize=0,)
        """

        #we get the palette from find palete 
        #ASSUME: GET PALLETE WAS CALLED!
        if( self._mPalette == None ):
            warning.warn("Image.binarizeFromPalette: No palette exists, call getPalette())")
            return None
        img = self.palettize(self._mPaletteBins)
        npimg = img.getNumpy()
        white = np.array([255,255,255])
        black = np.array([0,0,0])

        for p in palette_selection:
            npimg = np.where(npimg != p,npimg,white)
            
        npimg = np.where(npimg != white,black,white)
        bwimg = Image(npimg)
        return bwimg

    def skeletonize(self, radius = 5):
        """
        Summary:

        Skeletonization is the process of taking in a set of blobs (here blobs are white
        on a black background) and finding a squigly line that would be the back bone of
        the blobs were they some sort of vertebrate animal. Another way of thinking about 
        skeletonization is that it finds a series of lines that approximates a blob's shape.

        A good summary can be found here:
        http://www.inf.u-szeged.hu/~palagyi/skel/skel.html

        Parameters:
        
        radius - an intenger that defines how roughly how wide a blob must be to be added 
                 to the skeleton, lower values give more skeleton lines, higher values give
                 fewer skeleton lines. 
        
        Example:
       
        >>>> cam = Camera()
        >>>> while True:
        >>>>     img = cam.getImage()
        >>>>     b = img.binarize().invert()
        >>>>     s = img.skeletonize()
        >>>>     r = b-s
        >>>>     r.show()

        Notes:
        This code was a suggested improvement by Alex Wiltchko, check out his awesome blog here:
        http://alexbw.posterous.com/

        See Also:
        None
        
        """
        img = self.toGray().getNumpy()[:,:,0]
        distance_img = ndimage.distance_transform_edt(img)
        morph_laplace_img = ndimage.morphological_laplace(distance_img, (radius, radius))
        skeleton = morph_laplace_img < morph_laplace_img.min()/2
        retVal = np.zeros([self.width,self.height])
        retVal[skeleton] = 255
        return Image(retVal)

    def __getstate__(self):
        return dict( size = self.size(), colorspace = self._colorSpace, image = self.applyLayers().getBitmap().tostring() )
        
    def __setstate__(self, mydict):        
        self._bitmap = cv.CreateImageHeader(mydict['size'], cv.IPL_DEPTH_8U, 3)
        cv.SetData(self._bitmap, mydict['image'])
        self._colorSpace = mydict['colorspace']


Image.greyscale = Image.grayscale


from SimpleCV.Features import FeatureSet, Feature, Barcode, Corner, HaarFeature, Line, Chessboard, TemplateMatch, BlobMaker, Circle, KeyPoint, Motion, KeypointMatch
from SimpleCV.Stream import JpegStreamer
from SimpleCV.Font import *
from SimpleCV.DrawingLayer import *
from SimpleCV.Images import *
