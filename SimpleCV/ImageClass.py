# Load required libraries
from SimpleCV.base import *
from SimpleCV.Color import *


class ColorSpace:
    """
    **SUMMARY**

    The colorspace  class is used to encapsulate the color space of a given image.
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
    YCrCb = 7
  
class ImageSet(list):
    """
    **SUMMARY**

    This is an abstract class for keeping a list of images.  It has a few
    advantages in that you can use it to auto load data sets from a directory
    or the net.

    Keep in mind it inherits from a list too, so all the functionality a
    normal python list has this will too.

    **EXAMPLES**
    

    >>> imgs = ImageSet()
    >>> imgs.download("ninjas")
    >>> imgs.show(ninjas)


    or you can load a directory path:

    >>> imgs = ImageSet('/path/to/imgs/')
    >>> imgs.show()
    
    This will download and show a bunch of random ninjas.  If you want to
    save all those images locally then just use:

    >>> imgs.save()

    You can also load up the sample images that come with simplecv as:

    >>> imgs = ImageSet('samples')
    >>> imgs.filelist
    >>> logo = imgs.find('simplecv.png')
    
    **TO DO**

    Eventually this should allow us to pull image urls / paths from csv files.
    The method also allow us to associate an arbitraty bunch of data with each
    image, and on load/save pickle that data or write it to a CSV file. 

    """

    filelist = None
    def __init__(self, directory = None):

      if not directory:
          return
      if directory.lower() == 'samples' or directory.lower() == 'sample':
        #~ import pdb
        #~ pdb.set_trace()
        pth = __file__
        
        if sys.platform.lower() == 'win32' or sys.platform.lower() == 'win64':
          pth = pth.split('\\')[-2]
        else:
          pth = pth.split('/')[-2]
        pth = os.path.realpath(pth)
        directory = os.path.join(pth, 'sampleimages')

          
      self.load(directory)


    def download(self, tag=None, number=10, size='thumb'):
      """
      **SUMMARY** 

      This function downloads images from Google Image search based
      on the tag you provide. The number is the number of images you
      want to have in the list. Valid values for size are 'thumb', 'small',
      'medium', 'large' or a tuple of exact dimensions i.e. (640,480).
      Note that 'thumb' is exceptionally faster than others.

      .. Warning::
        This requires the python library Beautiful Soup to be installed
        http://www.crummy.com/software/BeautifulSoup/

      **PARAMETERS**

      * *tag* - A string of tag values you would like to download.
      * *number* - An integer of the number of images to try and download.
      * *size* - the size of the images to download. Valid options a tuple
        of the exact size or a string of the following approximate sizes:
        
        * thumb ~ less than 128x128
        * small  ~ approximately less than 640x480 but larger than 128x128
        * medium ~  approximately less than 1024x768 but larger than 640x480.
        * large ~ > 1024x768

      **RETURNS**
      
      Nothing - but caches local copy of images. 

      **EXAMPLE**

      >>> imgs = ImageSet()
      >>> imgs.download("ninjas")
      >>> imgs.show(ninjas)


      """

      try:
        from BeautifulSoup import BeautifulSoup

      except:
        print "You need to install Beatutiul Soup to use this function"
        print "to install you can use:"
        print "easy_install beautifulsoup"

        return


      INVALID_SIZE_MSG = """I don't understand what size images you want.
Valid options: 'thumb', 'small', 'medium', 'large'
 or a tuple of exact dimensions i.e. (640,480)."""

      if isinstance(size, basestring):
          size = size.lower()
          if size == 'thumb':
              size_param = ''
          elif size == 'small':
              size_param = '&tbs=isz:s'
          elif size == 'medium':
              size_param = '&tbs=isz:m'
          elif size == 'large':
              size_param = '&tbs=isz:l'
          else:
              print INVALID_SIZE_MSG
              return None
              
      elif type(size) == tuple:
          width, height = size
          size_param = '&tbs=isz:ex,iszw:' + str(width) + ',iszh:' + str(height)

      else:
          print INVALID_SIZE_MSG
          return None

      # Used to extract imgurl parameter value from a URL
      imgurl_re = re.compile('(?<=(&|\?)imgurl=)[^&]*((?=&)|$)')
      
      add_set = ImageSet()
      candidate_count = 0
      
      
      while len(add_set) < number:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        url = ("http://www.google.com/search?tbm=isch&q=" + urllib2.quote(tag) +
               size_param + "&start=" + str(candidate_count))
        page = opener.open(url)
        soup = BeautifulSoup(page)

        img_urls = []

        # Gets URLs of the thumbnail images 
        if size == 'thumb':
            imgs = soup.findAll('img')
            for img in imgs:
                dl_url = str(dict(img.attrs)['src'])
                img_urls.append(dl_url)

        # Gets the direct image URLs
        else:
            for link_tag in soup.findAll('a', {'href': re.compile('imgurl=')}):
              dirty_url = link_tag.get('href') # URL to an image as given by Google Images
              dl_url = str(re.search(imgurl_re, dirty_url).group()) # The direct URL to the image
              img_urls.append(dl_url)
        

        for dl_url in img_urls:
          try:
            add_img = Image(dl_url, verbose=False)

            # Don't know a better way to check if the image was actually returned
            if add_img.height <> 0 and add_img.width <> 0:
              add_set.append(add_img)

          except:
            #do nothing
            None

          if len(add_set) >= number:
              break

      self.extend(add_set)


    def show(self, showtime = 0.25):
      """
      **SUMMARY**

      This is a quick way to show all the items in a ImageSet.
      The time is in seconds. You can also provide a decimal value, so
      showtime can be 1.5, 0.02, etc.
      to show each image.

      **PARAMETERS**

      * *showtime* - the time, in seconds, to show each image in the set. 
 
      **RETURNS**
      
      Nothing.
      
      **EXAMPLE**

      >>> imgs = ImageSet()
      >>> imgs.download("ninjas")
      >>> imgs.show()
      
      
     """

      for i in self:
        i.show()
        time.sleep(showtime)

    def _get_app_ext(self, loops=0):
        """ Application extention. Part that secifies amount of loops. 
        if loops is 0, if goes on infinitely.
        """
        bb = "\x21\xFF\x0B"  # application extension
        bb += "NETSCAPE2.0"
        bb += "\x03\x01"
        if loops == 0:
            loops = 2**16-1
        bb += int_to_bin(loops)
        bb += '\x00'  # end
        return bb

    def _get_graphics_control_ext(self, duration=0.1):
        """ Graphics Control Extension. A sort of header at the start of
        each image. Specifies transparancy and duration. """
        bb = '\x21\xF9\x04'
        bb += '\x08'  # no transparency
        bb += int_to_bin( int(duration*100) ) # in 100th of seconds
        bb += '\x00'  # no transparent color
        bb += '\x00'  # end
        return bb
    
    def _write_gif(self, filename, duration=0.1, loops=0, dither=1):
        """ Given a set of images writes the bytes to the specified stream.
        """
        frames = 0
        previous = None
        fp = open(filename, 'wb')

        if not PIL_ENABLED:
            logger.warning("Need PIL to write animated gif files.") 
            return

        converted = []

        for img in self:
            if not isinstance(img,pil.Image):
                pil_img = img.getPIL()
            else:
                pil_img = img

            converted.append((pil_img.convert('P',dither=dither), img._get_header_anim()))

        #try:
        for img, header_anim in converted:
            if not previous:
                # gather data
                palette = getheader(img)[1]
                data = getdata(img)
                imdes, data = data[0], data[1:]            
                header = header_anim
                appext = self._get_app_ext(loops)
                graphext = self._get_graphics_control_ext(duration)
                
                # write global header
                fp.write(header)
                fp.write(palette)
                fp.write(appext)
                
                # write image
                fp.write(graphext)
                fp.write(imdes)
                for d in data:
                    fp.write(d)
                
            else:
                # gather info (compress difference)              
                data = getdata(img) 
                imdes, data = data[0], data[1:]       
                graphext = self._get_graphics_control_ext(duration)
                
                # write image
                fp.write(graphext)
                fp.write(imdes)
                for d in data:
                    fp.write(d)

            previous = img.copy()        
            frames = frames + 1

        fp.write(";") # end gif

        #finally:
        #    fp.close()
        #    return frames

    def save(self, destination=None, dt=0.2, verbose = False, displaytype=None):
        """
        **SUMMARY**

        This is a quick way to save all the images in a data set.
        Or to Display in webInterface.

        If you didn't specify a path one will randomly be generated.
        To see the location the files are being saved to then pass
        verbose = True.

        **PARAMETERS**

        * *destination* - path to which images should be saved, or name of gif
        * file. If this ends in .gif, the pictures will be saved accordingly.
        * *dt* - time between frames, for creating gif files.
        * *verbose* - print the path of the saved files to the console. 
        * *displaytype* - the method use for saving or displaying images.
        valid values are:

        * 'notebook' - display to the ipython notebook.
        * None - save to a temporary file. 

        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> imgs = ImageSet()
        >>> imgs.download("ninjas")
        >>> imgs.save(destination="ninjas_folder", verbose=True)

        >>> imgs.save(destination="ninjas.gif", verbose=True)

        """
        if displaytype=='notebook':
            try:
                from IPython.core.display import Image as IPImage
            except ImportError:
                print "You need IPython Notebooks to use this display mode"
                return
            from IPython.core import display as Idisplay
            for i in self:
                tf = tempfile.NamedTemporaryFile(suffix=".png")
                loc = '/tmp/' + tf.name.split('/')[-1]
                tf.close()
                i.save(loc)
                Idisplay.display(IPImage(filename=loc))
                return
        else:
            if destination:
                if destination.endswith(".gif"):
                    self._write_gif(destination, dt)
                else:
                    for i in self:
                        i.save(path=destination, temp=True, verbose=verbose)
            else:
                for i in self:
                    i.save(verbose=verbose)
      
    def showPaths(self):
      """
      **SUMMARY**

      This shows the file paths of all the images in the set.

      If they haven't been saved to disk then they will not have a filepath
      

      **RETURNS** 
      
      Nothing.

      **EXAMPLE**

      >>> imgs = ImageSet()
      >>> imgs.download("ninjas")
      >>> imgs.save(verbose=True)
      >>> imgs.showPaths()
      

      **TO DO**

      This should return paths as a list too.

      """

      for i in self:
        print i.filename

    def _read_gif(self, filename):
        """ read_gif(filename)

        Reads images from an animated GIF file. Returns the number of images loaded.
        """

        if not PIL_ENABLED:
            return
        elif not os.path.isfile(filename):
            return

        pil_img = pil.open(filename)
        pil_img.seek(0)

        pil_images = []
        try:
            while True:
                pil_images.append(pil_img.copy())
                pil_img.seek(pil_img.tell()+1)

        except EOFError:
            pass

        loaded = 0
        for img in pil_images:
            self.append(Image(img))
            loaded += 1

        return loaded

    def load(self, directory = None, extension = None):
      """
      **SUMMARY**

      This function loads up files automatically from the directory you pass
      it.  If you give it an extension it will only load that extension
      otherwise it will try to load all know file types in that directory.

      extension should be in the format:
      extension = 'png'

      **PARAMETERS**
      
      * *directory* - The path or directory from which to load images. If this
      * ends with .gif, it'll read from the gif file accordingly.
      * *extension* - The extension to use. If none is given png is the default.

      **RETURNS**

      The number of images in the image set.

      **EXAMPLE**

      >>> imgs = ImageSet()
      >>> imgs.load("images/faces")
      >>> imgs.load("images/eyes", "png")

      """

      if not directory:
        print "You need to give a directory to load from"
        return
      elif directory.endswith(".gif"):
        return self._read_gif(directory)
        
        
      if not os.path.exists(directory):
        print "Invalid image path given"
        return
      
      
      if extension:
        extension = "*." + extension
        formats = [os.path.join(directory, extension)]
        
      else:
        formats = [os.path.join(directory, x) for x in IMAGE_FORMATS]

      
      file_set = [glob.glob(p) for p in formats]

      self.filelist = dict()

      for f in file_set:
        for i in f:
          tmp = Image(i)
          if sys.platform.lower() == 'win32' or sys.platform.lower() == 'win64':
            self.filelist[tmp.filename.split('\\')[-1]] = tmp
          else:
            self.filelist[tmp.filename.split('/')[-1]] = tmp
          self.append(tmp)
          
      return len(self)
  
class Image:
    """
    **SUMMARY**

    The Image class is the heart of SimpleCV and allows you to convert to and 
    from a number of source types with ease.  It also has intelligent buffer
    management, so that modified copies of the Image required for algorithms
    such as edge detection, etc can be cached and reused when appropriate.

    
    Image are converted into 8-bit, 3-channel images in RGB colorspace.  It will
    automatically handle conversion from other representations into this
    standard format.  If dimensions are passed, an empty image is created.

    **EXAMPLE**
    
    >>> i = Image("/path/to/image.png")
    >>> i = Camera().getImage()


    You can also just load the SimpleCV logo using:

    >>> img = Image("simplecv")
    >>> img = Image("logo")
    >>> img = Image("logo_inverted")
    >>> img = Image("logo_transparent")

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
    _cv2Numpy = None #numpy array for OpenCV >= 2.3
    _cv2GrayNumpy = None #grayscale numpy array for OpenCV >= 2.3
  
    #For DFT Caching 
    _DFT = [] #an array of 2 channel (real,imaginary) 64F images

    #Keypoint caching values
    _mKeyPoints = None
    _mKPDescriptors = None
    _mKPFlavor = "NONE"
    
    #temp files
    _tempFiles = []

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
    
   
    def __repr__(self):
        if len(self.filename) == 0:
          fn = "None"
        else:
          fn = self.filename
        return "<SimpleCV.Image Object size:(%d, %d), filename: (%s), at memory location: (%s)>" % (self.width, self.height, fn, hex(id(self)))
      

    #initialize the frame
    #parameters: source designation (filename)
    #todo: handle camera/capture from file cases (detect on file extension)
    def __init__(self, source = None, camera = None, colorSpace = ColorSpace.UNKNOWN,verbose=True, sample=False, cv2image=False):
        """ 
        **SUMMARY**

        The constructor takes a single polymorphic parameter, which it tests
        to see how it should convert into an RGB image.  Supported types include:
    
        **PARAMETERS**

        * *source* - The source of the image. This can be just about anything, a numpy arrray, a file name, a width and height
          tuple, a url. Certain strings such as "lenna" or "logo" are loaded automatically for quick testing.

        * *camera* - A camera to pull a live image.
 
        * *colorspace* - A default camera color space. If none is specified this will usually default to the BGR colorspace.

        * *sample* - This is set to true if you want to load some of the included sample images without having to specify the complete path
        

        **EXAMPLES**

        >>> img = Image('simplecv')
        >>> img = Image('test.png')
        >>> img = Image('http://www.website.com/my_image.jpg')
        >>> img.show()
  
        **NOTES**

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
        #Temp files
        self._tempFiles = []
    

        #Check if need to load from URL
        #(this can be made shorter)if type(source) == str and (source[:7].lower() == "http://" or source[:8].lower() == "https://"):
        if isinstance(source, basestring) and (source.lower().startswith("http://") or source.lower().startswith("https://")):
            #try:
            # added spoofed user agent for images that are blocking bots (like wikipedia)
            req = urllib2.Request(source, headers={'User-Agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.54 Safari/536.5"}) 
            img_file = urllib2.urlopen(req)
            #except:
            #if verbose:
                #print "Couldn't open Image from URL:" + source
            #return None

            im = StringIO(img_file.read())
            source = pil.open(im).convert("RGB")

        #This section loads custom built-in images    
        if isinstance(source, basestring):
            tmpname = source.lower()

            if tmpname == "simplecv" or tmpname == "logo":
                imgpth = os.path.join(LAUNCH_PATH, 'sampleimages','simplecv.png')
                source = imgpth
            elif tmpname == "simplecv_inverted" or tmpname == "inverted" or tmpname == "logo_inverted":
                imgpth = os.path.join(LAUNCH_PATH, 'sampleimages','simplecv_inverted.png')
                source = imgpth
            elif tmpname == "lenna":
                imgpth = os.path.join(LAUNCH_PATH, 'sampleimages','lenna.png')
                source = imgpth
            elif sample:
                imgpth = os.path.join(LAUNCH_PATH, 'sampleimages', source)
                source = imgpth

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
                if not cv2image:
                    invertedsource = source[:, :, ::-1].transpose([1, 0, 2])
                else:
                    # If the numpy array is from cv2, then it must not be transposed.
                    invertedsource = source

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

            elif source.split('.')[-1] == 'webp':

                try:
                    from webm import decode as webmDecode
                except ImportError:
                      logger.warning('The webm module needs to be installed to load webp files: https://github.com/ingenuitas/python-webm')
                      return

                WEBP_IMAGE_DATA = bytearray(file(source, "rb").read())
                result = webmDecode.DecodeRGB(WEBP_IMAGE_DATA)
                webpImage = pil.frombuffer(
                    "RGB", (result.width, result.height), str(result.bitmap),
                    "raw", "RGB", 0, 1
                )
                self._pil = webpImage.convert("RGB")
                self._bitmap = cv.CreateImageHeader(self._pil.size, cv.IPL_DEPTH_8U, 3)
                self.filename = source
                cv.SetData(self._bitmap, self._pil.tostring())
                cv.CvtColor(self._bitmap, self._bitmap, cv.CV_RGB2BGR)

            else:
                self.filename = source
                try:
                    self._bitmap = cv.LoadImage(self.filename, iscolor=cv.CV_LOAD_IMAGE_COLOR)
                except:
                    self._pil = pil.open(self.filename).convert("RGB")
                    self._bitmap = cv.CreateImageHeader(self._pil.size, cv.IPL_DEPTH_8U, 3)
                    cv.SetData(self._bitmap, self._pil.tostring())
                    cv.CvtColor(self._bitmap, self._bitmap, cv.CV_RGB2BGR)

                #TODO, on IOError fail back to PIL
                self._colorSpace = ColorSpace.BGR
    
    
        elif (type(source) == pg.Surface):
            self._pgsurface = source
            self._bitmap = cv.CreateImageHeader(self._pgsurface.get_size(), cv.IPL_DEPTH_8U, 3)
            cv.SetData(self._bitmap, pg.image.tostring(self._pgsurface, "RGB"))
            cv.CvtColor(self._bitmap, self._bitmap, cv.CV_RGB2BGR)
            self._colorSpace = ColorSpace.BGR


        elif (PIL_ENABLED and (
                (len(source.__class__.__bases__) and source.__class__.__bases__[0].__name__ == "ImageFile")
                or source.__class__.__name__ == "JpegImageFile"
                or source.__class__.__name__ == "WebPPImageFile"
                or  source.__class__.__name__ == "Image")):
                
            if source.mode != 'RGB':
                source = source.convert('RGB')
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
    
    
    def __del__(self):
        """
        This is called when the instance is about to be destroyed also called a destructor.
        """
        try :
           for i in self._tempFiles:
               if (isinstance(i,str)):
                   os.remove(i)
        except :
           pass
           
    def getEXIFData(self):
        """
        **SUMMARY**

        This function extracts the exif data from an image file like JPEG or TIFF. The data is returned as a dict. 

        **RETURNS**

        A dictionary of key value pairs. The value pairs are defined in the EXIF.py file. 

        **EXAMPLE**
   
        >>> img = Image("./SimpleCV/sampleimages/OWS.jpg")
        >>> data = img.getEXIFData()
        >>> data['Image GPSInfo'].values

        **NOTES**

        * Compliments of: http://exif-py.sourceforge.net/

        * See also: http://en.wikipedia.org/wiki/Exchangeable_image_file_format

        **See Also**

        :py:class:`EXIF`
        """
        import os, string
        if( len(self.filename) < 5 or self.filename is None ):
            #I am not going to warn, better of img sets
            #logger.warning("ImageClass.getEXIFData: This image did not come from a file, can't get EXIF data.")
            return {}

        fileName, fileExtension = os.path.splitext(self.filename)
        fileExtension = string.lower(fileExtension)
        if( fileExtension != '.jpeg' and fileExtension != '.jpg' and
            fileExtension != 'tiff' and fileExtension != '.tif'):
            #logger.warning("ImageClass.getEXIFData: This image format does not support EXIF")
            return {}

        raw = open(self.filename,'rb')
        data = process_file(raw)
        return data

    def live(self):
        """
        **SUMMARY**

        This shows a live view of the camera. 
        * Left click will show mouse coordinates and color.
        * Right click will kill the live image.

        **RETURNS**
        
        Nothing. In place method. 

        **EXAMPLE** 

        >>> cam = Camera()
        >>> cam.live()

        """

        start_time = time.time()
        
        from SimpleCV.Display import Display
        i = self
        d = Display(i.size())
        i.save(d)
        col = Color.RED

        while d.isNotDone():
          i = self
          i.clearLayers()
          elapsed_time = time.time() - start_time
          

          if d.mouseLeft:
            txt = "coord: (" + str(d.mouseX) + "," + str(d.mouseY) + ")"
            i.dl().text(txt, (10,i.height / 2), color=col)
            txt = "color: " + str(i.getPixel(d.mouseX,d.mouseY))
            i.dl().text(txt, (10,(i.height / 2) + 10), color=col)
            print "coord: (" + str(d.mouseX) + "," + str(d.mouseY) + "), color: " + str(i.getPixel(d.mouseX,d.mouseY))


          if elapsed_time > 0 and elapsed_time < 5:
            
            i.dl().text("In live mode", (10,10), color=col)
            i.dl().text("Left click will show mouse coordinates and color", (10,20), color=col)
            i.dl().text("Right click will kill the live image", (10,30), color=col)
            
          
          i.save(d)
          if d.mouseRight:
            print "Closing Window"
            d.done = True

        
        pg.quit()

    def getColorSpace(self):
        """
        **SUMMARY**
        
        Returns the value matched in the color space class
        
        **RETURNS**

        Integer corresponding to the color space. 
        
        **EXAMPLE**

        >>> if(image.getColorSpace() == ColorSpace.RGB)

        **SEE ALSO** 

        :py:class:`ColorSpace` 

        """
        return self._colorSpace
  
  
    def isRGB(self):
        """
        **SUMMARY**

        Returns true if this image uses the RGB colorspace.
        
        **RETURNS**

        True if the image uses the RGB colorspace, False otherwise. 
        
        **EXAMPLE**
        
        >>> if( img.isRGB() ):
        >>>    r,g,b = img.splitChannels()

        **SEE ALSO**

        :py:meth:`toRGB`

        
        """
        return(self._colorSpace==ColorSpace.RGB)


    def isBGR(self):
        """
        **SUMMARY**

        Returns true if this image uses the BGR colorspace.
        
        **RETURNS**

        True if the image uses the BGR colorspace, False otherwise. 
        
        **EXAMPLE**
        
        >>> if( img.isBGR() ):
        >>>    b,g,r = img.splitChannels()

        **SEE ALSO**

        :py:meth:`toBGR`
        
        """
        return(self._colorSpace==ColorSpace.BGR)
    
    
    def isHSV(self):
        """
        **SUMMARY**

        Returns true if this image uses the HSV colorspace.
        
        **RETURNS**

        True if the image uses the HSV colorspace, False otherwise. 
        
        **EXAMPLE**
        
        >>> if( img.isHSV() ):
        >>>    h,s,v = img.splitChannels()

        **SEE ALSO**

        :py:meth:`toHSV`
        
        """
        return(self._colorSpace==ColorSpace.HSV)
    
    
    def isHLS(self):
        """
        **SUMMARY**

        Returns true if this image uses the HLS colorspace.
        
        **RETURNS**

        True if the image uses the HLS colorspace, False otherwise. 
        
        **EXAMPLE**
        
        >>> if( img.isHLS() ):
        >>>    h,l,s = img.splitChannels()

        **SEE ALSO**

        :py:meth:`toHLS`
        
        """
        return(self._colorSpace==ColorSpace.HLS)  
  
  
    def isXYZ(self):
        """
        **SUMMARY**

        Returns true if this image uses the XYZ colorspace.
        
        **RETURNS**

        True if the image uses the XYZ colorspace, False otherwise. 
        
        **EXAMPLE**
        
        >>> if( img.isXYZ() ):
        >>>    x,y,z = img.splitChannels()

        **SEE ALSO**

        :py:meth:`toXYZ`
        
        """
        return(self._colorSpace==ColorSpace.XYZ)
    
    
    def isGray(self):
        """
        **SUMMARY**

        Returns true if this image uses the Gray colorspace.
        
        **RETURNS**

        True if the image uses the Gray colorspace, False otherwise. 
        
        **EXAMPLE**
        
        >>> if( img.isGray() ):
        >>>    print "The image is in Grayscale."

        **SEE ALSO**

        :py:meth:`toGray`
        
        """
        return(self._colorSpace==ColorSpace.GRAY)    

    def isYCrCb(self):
        """
        **SUMMARY**

        Returns true if this image uses the YCrCb colorspace.
        
        **RETURNS**

        True if the image uses the YCrCb colorspace, False otherwise. 
        
        **EXAMPLE**
        
        >>> if( img.isYCrCb() ):
        >>>    Y,Cr,Cb = img.splitChannels()

        **SEE ALSO**

        :py:meth:`toYCrCb`
        
        """
        return(self._colorSpace==ColorSpace.YCrCb)
    
    def toRGB(self):
        """
        **SUMMARY**

        This method attemps to convert the image to the RGB colorspace. 
        If the color space is unknown we assume it is in the BGR format
        
        **RETURNS**

        Returns the converted image if the conversion was successful, 
        otherwise None is returned.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> RGBImg = img.toRGB()

        **SEE ALSO**

        :py:meth:`isRGB`
        
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
        elif( self._colorSpace == ColorSpace.YCrCb ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_YCrCb2RGB)    
        elif( self._colorSpace == ColorSpace.RGB ):
            retVal = self.getBitmap()
        else:
            logger.warning("Image.toRGB: There is no supported conversion to RGB colorspace")
            return None
        return Image(retVal, colorSpace=ColorSpace.RGB )


    def toBGR(self):
        """
        **SUMMARY**

        This method attemps to convert the image to the BGR colorspace. 
        If the color space is unknown we assume it is in the BGR format.
        
        **RETURNS**

        Returns the converted image if the conversion was successful, 
        otherwise None is returned.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> BGRImg = img.toBGR()

        **SEE ALSO**

        :py:meth:`isBGR`
        
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
        elif( self._colorSpace == ColorSpace.YCrCb ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_YCrCb2BGR)    
        elif( self._colorSpace == ColorSpace.BGR ):
            retVal = self.getBitmap()    
        else:
            logger.warning("Image.toBGR: There is no supported conversion to BGR colorspace")
            return None
        return Image(retVal, colorSpace = ColorSpace.BGR )
  
  
    def toHLS(self):
        """
        **SUMMARY**

        This method attempts to convert the image to the HLS colorspace. 
        If the color space is unknown we assume it is in the BGR format.
        
        **RETURNS**

        Returns the converted image if the conversion was successful, 
        otherwise None is returned.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> HLSImg = img.toHLS()

        **SEE ALSO**

        :py:meth:`isHLS`
        
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
        elif( self._colorSpace == ColorSpace.YCrCb ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_YCrCb2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2HLS)        
        elif( self._colorSpace == ColorSpace.HLS ):
            retVal = self.getBitmap()      
        else:
            logger.warning("Image.toHSL: There is no supported conversion to HSL colorspace")
            return None
        return Image(retVal, colorSpace = ColorSpace.HLS )
    
    
    def toHSV(self):
        """
        **SUMMARY**

        This method attempts to convert the image to the HSV colorspace. 
        If the color space is unknown we assume it is in the BGR format
        
        **RETURNS**

        Returns the converted image if the conversion was successful, 
        otherwise None is returned.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> HSVImg = img.toHSV()

        **SEE ALSO**

        :py:meth:`isHSV`
        
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
        elif( self._colorSpace == ColorSpace.YCrCb ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_YCrCb2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2HSV)        
        elif( self._colorSpace == ColorSpace.HSV ):
            retVal = self.getBitmap()      
        else:
            logger.warning("Image.toHSV: There is no supported conversion to HSV colorspace")
            return None
        return Image(retVal, colorSpace = ColorSpace.HSV )
    
    
    def toXYZ(self):
        """
        **SUMMARY**

        This method attemps to convert the image to the XYZ colorspace. 
        If the color space is unknown we assume it is in the BGR format
        
        **RETURNS**

        Returns the converted image if the conversion was successful, 
        otherwise None is returned.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> XYZImg = img.toXYZ()

        **SEE ALSO**

        :py:meth:`isXYZ`
        
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
        elif( self._colorSpace == ColorSpace.YCrCb ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_YCrCb2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2XYZ)            
        elif( self._colorSpace == ColorSpace.XYZ ):
            retVal = self.getBitmap()      
        else:
            logger.warning("Image.toXYZ: There is no supported conversion to XYZ colorspace")
            return None
        return Image(retVal, colorSpace=ColorSpace.XYZ )
    
    
    def toGray(self):
        """
        **SUMMARY**

        This method attemps to convert the image to the grayscale colorspace. 
        If the color space is unknown we assume it is in the BGR format.
        
        **RETURNS**

        A grayscale SimpleCV image if successful.
        otherwise None is returned.
        
        **EXAMPLE**

        >>> img = Image("lenna")
        >>> img.toGray().binarize().show()

        **SEE ALSO**

        :py:meth:`isGray`
        :py:meth:`binarize`
        
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
        elif( self._colorSpace == ColorSpace.YCrCb ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_YCrCb2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2GRAY)        
        elif( self._colorSpace == ColorSpace.GRAY ):
            retVal = self.getBitmap()
        else:
            logger.warning("Image.toGray: There is no supported conversion to gray colorspace")
            return None
        return Image(retVal, colorSpace = ColorSpace.GRAY )   
        
    def toYCrCb(self):
        """
        **SUMMARY**

        This method attemps to convert the image to the YCrCb colorspace. 
        If the color space is unknown we assume it is in the BGR format
        
        **RETURNS**

        Returns the converted image if the conversion was successful, 
        otherwise None is returned.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> RGBImg = img.toYCrCb()

        **SEE ALSO**

        :py:meth:`isYCrCb`
        
        """

        retVal = self.getEmpty()
        if( self._colorSpace == ColorSpace.BGR or
                self._colorSpace == ColorSpace.UNKNOWN ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_BGR2YCrCb)
        elif( self._colorSpace == ColorSpace.RGB ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_RGB2YCrCb)
        elif( self._colorSpace == ColorSpace.HSV ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HSV2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2YCrCb)
        elif( self._colorSpace == ColorSpace.HLS ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_HLS2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2YCrCb)    
        elif( self._colorSpace == ColorSpace.XYZ ):
            cv.CvtColor(self.getBitmap(), retVal, cv.CV_XYZ2RGB)
            cv.CvtColor(retVal, retVal, cv.CV_RGB2YCrCb)
        elif( self._colorSpace == ColorSpace.YCrCb ):
            retVal = self.getBitmap()      
        else:
            logger.warning("Image.toYCrCb: There is no supported conversion to YCrCb colorspace")
            return None
        return Image(retVal, colorSpace=ColorSpace.YCrCb )     
    
    
    def getEmpty(self, channels=3):
        """
        **SUMMARY**
        
        Create a new, empty OpenCV bitmap with the specified number of channels (default 3).
        This method basically creates an empty copy of the image. This is handy for 
        interfacing with OpenCV functions directly. 
        
        **PARAMETERS**

        * *channels* - The number of channels in the returned OpenCV image. 
        
        **RETURNS**

        Returns an black OpenCV IplImage that matches the width, height, and color 
        depth of the source image.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> rawImg  = img.getEmpty()
        >>> cv.SomeOpenCVFunc(img.getBitmap(),rawImg)

        **SEE ALSO**

        :py:meth:`getBitmap`
        :py:meth:`getFPMatrix`
        :py:meth:`getPIL`
        :py:meth:`getNumpy`
        :py:meth:`getGrayNumpy`
        :py:meth:`getGrayscaleMatrix`
        
        """
        bitmap = cv.CreateImage(self.size(), cv.IPL_DEPTH_8U, channels)
        cv.SetZero(bitmap)
        return bitmap


    def getBitmap(self):
        """
        **SUMMARY**
       
        Retrieve the bitmap (iplImage) of the Image.  This is useful if you want
        to use functions from OpenCV with SimpleCV's image class
        
        **RETURNS**

        Returns black OpenCV IplImage from this image.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> rawImg  = img.getBitmap()
        >>> rawOut  = img.getEmpty()
        >>> cv.SomeOpenCVFunc(rawImg,rawOut)

        **SEE ALSO**

        :py:meth:`getEmpty`
        :py:meth:`getFPMatrix`
        :py:meth:`getPIL`
        :py:meth:`getNumpy`
        :py:meth:`getGrayNumpy`
        :py:meth:`getGrayscaleMatrix`

        """
        if (self._bitmap):
            return self._bitmap
        elif (self._matrix):
            self._bitmap = cv.GetImage(self._matrix)
        return self._bitmap


    def getMatrix(self):
        """
        **SUMMARY**
       
        Get the matrix (cvMat) version of the image, required for some OpenCV algorithms.
        
        **RETURNS**

        Returns the OpenCV CvMat version of this image.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> rawImg  = img.getMatrix()
        >>> rawOut  = img.getEmpty()
        >>> cv.SomeOpenCVFunc(rawImg,rawOut)

        **SEE ALSO**

        :py:meth:`getEmpty`
        :py:meth:`getBitmap`
        :py:meth:`getFPMatrix`
        :py:meth:`getPIL`
        :py:meth:`getNumpy`
        :py:meth:`getGrayNumpy`
        :py:meth:`getGrayscaleMatrix`
        
        """
        if (self._matrix):
            return self._matrix
        else:
            self._matrix = cv.GetMat(self.getBitmap()) #convert the bitmap to a matrix
            return self._matrix


    def getFPMatrix(self):
        """
        **SUMMARY**
       
        Converts the standard int bitmap to a floating point bitmap. 
        This is handy for some OpenCV functions. 

        
        **RETURNS**

        Returns the floating point OpenCV CvMat version of this image.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> rawImg  = img.getFPMatrix()
        >>> rawOut  = img.getEmpty()
        >>> cv.SomeOpenCVFunc(rawImg,rawOut)

        **SEE ALSO**

        :py:meth:`getEmpty`
        :py:meth:`getBitmap`
        :py:meth:`getMatrix`
        :py:meth:`getPIL`
        :py:meth:`getNumpy`
        :py:meth:`getGrayNumpy`
        :py:meth:`getGrayscaleMatrix`
        
        """
        retVal =  cv.CreateImage((self.width,self.height), cv.IPL_DEPTH_32F, 3)
        cv.Convert(self.getBitmap(),retVal)
        return retVal
    
    def getPIL(self):
        """
        **SUMMARY**
       
        Get a PIL Image object for use with the Python Image Library
        This is handy for some PIL functions. 

        
        **RETURNS**

        Returns the Python Imaging Library (PIL) version of this image.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> rawImg  = img.getPIL()


        **SEE ALSO**

        :py:meth:`getEmpty`
        :py:meth:`getBitmap`
        :py:meth:`getMatrix`
        :py:meth:`getFPMatrix`
        :py:meth:`getNumpy`
        :py:meth:`getGrayNumpy`
        :py:meth:`getGrayscaleMatrix`
   
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
        **SUMMARY**
       
        Return a grayscale Numpy array of the image. 
        
        **RETURNS**

        Returns the image, converted first to grayscale and then converted to a 2D numpy array. 
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> rawImg  = img.getGrayNumpy()

        **SEE ALSO**

        :py:meth:`getEmpty`
        :py:meth:`getBitmap`
        :py:meth:`getMatrix`
        :py:meth:`getPIL`
        :py:meth:`getNumpy`
        :py:meth:`getGrayNumpy`
        :py:meth:`getGrayscaleMatrix`
        
        """
        if( self._grayNumpy != "" ):
            return self._grayNumpy
        else:
            self._grayNumpy = uint8(np.array(cv.GetMat(self._getGrayscaleBitmap())).transpose())

        return self._grayNumpy

    def getNumpy(self):
        """
        **SUMMARY**
       
        Get a Numpy array of the image in width x height x RGB dimensions
        
        **RETURNS**

        Returns the image, converted first to grayscale and then converted to a 3D numpy array. 
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> rawImg  = img.getNumpy()

        **SEE ALSO**

        :py:meth:`getEmpty`
        :py:meth:`getBitmap`
        :py:meth:`getMatrix`
        :py:meth:`getPIL`
        :py:meth:`getGrayNumpy`
        :py:meth:`getGrayscaleMatrix`
        
        """

        if self._numpy != "":
            return self._numpy
    
    
        self._numpy = np.array(self.getMatrix())[:, :, ::-1].transpose([1, 0, 2])
        return self._numpy

    def getNumpyCv2(self):
        """
        **SUMMARY**
       
        Get a Numpy array of the image in width x height x RGB dimensions compatible with OpenCV >= 2.3
        
        **RETURNS**

        Returns the  3D numpy array of the image compatible with OpenCV >= 2.3
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> rawImg  = img.getNumpyCv2()

        **SEE ALSO**

        :py:meth:`getEmpty`
        :py:meth:`getBitmap`
        :py:meth:`getMatrix`
        :py:meth:`getPIL`
        :py:meth:`getGrayNumpy`
        :py:meth:`getGrayscaleMatrix`
        :py:meth:`getNumpy`
        :py:meth:`getGrayNumpyCv2`
        
        """
        
        if type(self._cv2Numpy) is not np.ndarray:
            self._cv2Numpy = np.array(self.getMatrix())
        return self._cv2Numpy
        
    def getGrayNumpyCv2(self):
        """
        **SUMMARY**
       
        Get a Grayscale Numpy array of the image in width x height y compatible with OpenCV >= 2.3
        
        **RETURNS**

        Returns the grayscale numpy array compatible with OpenCV >= 2.3 
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> rawImg  = img.getNumpyCv2()

        **SEE ALSO**

        :py:meth:`getEmpty`
        :py:meth:`getBitmap`
        :py:meth:`getMatrix`
        :py:meth:`getPIL`
        :py:meth:`getGrayNumpy`
        :py:meth:`getGrayscaleMatrix`
        :py:meth:`getNumpy`
        :py:meth:`getGrayNumpyCv2`
        
        """
        if not type(self._cv2GrayNumpy) is not np.ndarray:
            self._cv2GrayNumpy = np.array(self.getGrayscaleMatrix())
        return self._cv2GrayNumpy

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
            logger.warning("Image._getGrayscaleBitmap: There is no supported conversion to gray colorspace")
            return None    
        return self._graybitmap


    def getGrayscaleMatrix(self):
        """
        **SUMMARY**
       
        Get the grayscale matrix (cvMat) version of the image, required for some OpenCV algorithms.
        
        **RETURNS**

        Returns the OpenCV CvMat version of this image.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> rawImg  = img.getGrayscaleMatrix()
        >>> rawOut  = img.getEmpty()
        >>> cv.SomeOpenCVFunc(rawImg,rawOut)

        **SEE ALSO**

        :py:meth:`getEmpty`
        :py:meth:`getBitmap`
        :py:meth:`getFPMatrix`
        :py:meth:`getPIL`
        :py:meth:`getNumpy`
        :py:meth:`getGrayNumpy`
        :py:meth:`getMatrix`
        
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
        **SUMMARY**

        Perform a histogram equalization on the image. 

        **RETURNS**

        Returns a grayscale SimpleCV image.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> img = img.equalize()


        """
        return Image(self._getEqualizedGrayscaleBitmap())
    
    def getPGSurface(self):
        """
        **SUMMARY**

        Returns the image as a pygame surface.  This is used for rendering the display

        **RETURNS**

        A pygame surface object used for rendering.

        
        """
        if (self._pgsurface):
            return self._pgsurface
        else:
            if self.isGray():
                self._pgsurface = pg.image.fromstring(self.getBitmap().tostring(), self.size(), "RGB")
            else:
                self._pgsurface = pg.image.fromstring(self.toRGB().getBitmap().tostring(), self.size(), "RGB")
            return self._pgsurface
    
    def toString(self):
        """
        **SUMMARY**
        
        Returns the image as a string, useful for moving data around.

        
        **RETURNS**

        The image, converted to rgb, then converted to a string.

        """
        return self.toRGB().getBitmap().tostring()
    
    
    def save(self, filehandle_or_filename="", mode="", verbose=False, temp=False, path=None, fname=None, **params):
        """
        **SUMMARY**

        Save the image to the specified filename.  If no filename is provided then
        then it will use the filename the Image was loaded from or the last
        place it was saved to. You can save to lots of places, not just files.
        For example you can save to the Display, a JpegStream, VideoStream, 
        temporary file, or Ipython Notebook.

    
        Save will implicitly render the image's layers before saving, but the layers are 
        not applied to the Image itself.


        **PARAMETERS**

        * *filehandle_or_filename* - the filename to which to store the file. The method will infer the file type.

        * *mode* - This flag is used for saving using pul.

        * *verbose* - If this flag is true we return the path where we saved the file. 

        * *temp* - If temp is True we save the image as a temporary file and return the path
        
        * *path* - path where temporary files needed to be stored
        
        * *fname* - name(Prefix) of the temporary file.

        * *params* - This object is used for overloading the PIL save methods. In particular 
          this method is useful for setting the jpeg compression level. For JPG see this documentation:
          http://www.pythonware.com/library/pil/handbook/format-jpeg.htm          

        **EXAMPLES**

        To save as a temporary file just use:

        >>> img = Image('simplecv')
        >>> img.save(temp=True)

        It will return the path that it saved to.

        Save also supports IPython Notebooks when passing it a Display object
        that has been instainted with the notebook flag.

        To do this just use:
        
        >>> disp = Display(displaytype='notebook')
        >>> img.save(disp)

        .. Note::
          You must have IPython notebooks installed for this to work
          
          path and fname are valid if and only if temp is set to True.
          
        .. attention:: 
          We need examples for all save methods as they are unintuitve. 
        """
        #TODO, we use the term mode here when we mean format
        #TODO, if any params are passed, use PIL
        
        if temp and path!=None :
            import glob
            if fname==None :
                fname = 'Image'                
            if glob.os.path.exists(path):
                path = glob.os.path.abspath(path) 
                imagefiles = glob.glob(glob.os.path.join(path,fname+"*.png"))
                num = [0]
                for img in imagefiles :
                    num.append(int(glob.re.findall('[0-9]+$',img[:-4])[-1]))
                num.sort()
                fnum = num[-1]+1
                fname = glob.os.path.join(path,fname+str(fnum)+".png") 
                self._tempFiles.append(fname)
                self.save(self._tempFiles[-1])
                return self._tempFiles[-1]
            else :
                print "Path does not exist!"
                        
        #if it's a temporary file
        elif temp :
            self._tempFiles.append(tempfile.NamedTemporaryFile(suffix=".png"))
            self.save(self._tempFiles[-1].name)
            return self._tempFiles[-1].name
       
        if (not filehandle_or_filename):
            if (self.filename):
                filehandle_or_filename = self.filename
            else:
                filehandle_or_filename = self.filehandle

            
        if (len(self._mLayers)):
            saveimg = self.applyLayers()
        else:
            saveimg = self

        if self._colorSpace != ColorSpace.BGR and self._colorSpace != ColorSpace.GRAY:
            saveimg = saveimg.toBGR()

        if not isinstance(filehandle_or_filename, basestring):
            fh = filehandle_or_filename

            if (not PIL_ENABLED):
                logger.warning("You need the python image library to save by filehandle")
                return 0


            if (type(fh) == InstanceType and fh.__class__.__name__ == "JpegStreamer"):
                fh.jpgdata = StringIO() 
                saveimg.getPIL().save(fh.jpgdata, "jpeg", **params) #save via PIL to a StringIO handle 
                fh.refreshtime = time.time()
                self.filename = "" 
                self.filehandle = fh


            elif (type(fh) == InstanceType and fh.__class__.__name__ == "VideoStream"):
                self.filename = "" 
                self.filehandle = fh
                fh.writeFrame(saveimg)


            elif (type(fh) == InstanceType and fh.__class__.__name__ == "Display"):

                if fh.displaytype == 'notebook':
                  try:
                    from IPython.core.display import Image as IPImage
                  except ImportError:
                    print "You need IPython Notebooks to use this display mode"
                    return

                  from IPython.core import display as Idisplay
                  tf = tempfile.NamedTemporaryFile(suffix=".png")
                  loc = '/tmp/' + tf.name.split('/')[-1]
                  tf.close()
                  self.save(loc)
                  Idisplay.display(IPImage(filename=loc))
                  return
                else:
                  self.filename = "" 
                  self.filehandle = fh
                  fh.writeFrame(saveimg)


            else:
                if (not mode):
                    mode = "jpeg"
      
                saveimg.getPIL().save(fh, mode, **params)
                self.filehandle = fh #set the filename for future save operations
                self.filename = ""
                
            if verbose:
              print self.filename
              
            return 1

        #make a temporary file location if there isn't one
        if not filehandle_or_filename:
          filename = tempfile.mkstemp(suffix=".png")[-1]
        else:  
          filename = filehandle_or_filename

        #allow saving in webp format
        if re.search('\.webp$', filename):
            try:
              #newer versions of PIL support webp format, try that first
              self.getPIL().save(filename, **params)
            except:
              #if PIL doesn't support it, maybe we have the python-webm library
              try:
                from webm import encode as webmEncode
                from webm.handlers import BitmapHandler, WebPHandler
              except:
                logger.warning('You need the webm library to save to webp format. You can download from: https://github.com/ingenuitas/python-webm')
                return 0

              #PNG_BITMAP_DATA = bytearray(Image.open(PNG_IMAGE_FILE).tostring())
              PNG_BITMAP_DATA = bytearray(self.toString()) 
              IMAGE_WIDTH = self.width
              IMAGE_HEIGHT = self.height
              
              
              image = BitmapHandler(
                  PNG_BITMAP_DATA, BitmapHandler.RGB,
                  IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_WIDTH * 3
              )
              result = webmEncode.EncodeRGB(image)

              file(filename.format("RGB"), "wb").write(result.data)
              return 1
        #if the user is passing kwargs use the PIL save method.
        if( params ): #usually this is just the compression rate for the image
            if (not mode):
                mode = "jpeg"
            saveimg.getPIL().save(filename, mode, **params)
            return 1
        
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

        if temp:
          return filename
        else:
          return 1

    
    def copy(self):
        """
        **SUMMARY**

        Return a full copy of the Image's bitmap.  Note that this is different
        from using python's implicit copy function in that only the bitmap itself
        is copied. This method essentially performs a deep copy.
    
        **RETURNS**

        A copy of this SimpleCV image.

        **EXAMPLE**
        
        >>> img = Image("logo")
        >>> img2 = img.copy()

        """
        newimg = self.getEmpty() 
        cv.Copy(self.getBitmap(), newimg)
        return Image(newimg, colorSpace=self._colorSpace) 
    
    def upload(self,dest,api_key=None,api_secret=None, verbose = True):
        """
        **SUMMARY**
        Uploads image to imgur or flickr. In verbose mode URL values are printed.
          
        **PARAMETERS**
        * *api_key* - a string of the API key.
        * *api_secret* (required only for flickr) - a string of the API secret.
        * *verbose* - If verbose is true all values are printed to the
          screen
          
        **RETURNS**
        if uploading is successful, 
         - Imgur return the original image URL on success and None if it fails.
         - Flick returns True on success, else returns False.
          
        **EXAMPLE**
        TO upload image to imgur
           >>> img = Image("lenna")
           >>> result = img.upload( 'imgur',"MY_API_KEY1234567890" )
           >>> print "Uploaded To: " + result[0] 
           
        To upload image to flickr
           >>> img.upload('flickr','api_key','api_secret')
           >>> img.invert().upload('flickr') #Once the api keys and secret keys are cached.
           
        **NOTES**
        .. Warning::
           This method requires two packages to be installed 
           -PyCurl 
           -flickr api.
           
        .. Warning::
           You must supply your own API key. See here: 
           - http://imgur.com/register/api_anon
           - http://www.flickr.com/services/api/misc.api_keys.html
        """
        if ( dest=='imgur' ) :
            try:
                import pycurl
            except ImportError:
                print "PycURL Library not installed."
                return
                    
            response = StringIO()
            c = pycurl.Curl()
            values = [("key", api_key),
                      ("image", (c.FORM_FILE, self.filename))]
            c.setopt(c.URL, "http://api.imgur.com/2/upload.xml")
            c.setopt(c.HTTPPOST, values)
            c.setopt(c.WRITEFUNCTION, response.write)
            c.perform()
            c.close()
                
            match = re.search(r'<hash>(\w+).*?<deletehash>(\w+).*?<original>(http://[\w.]+/[\w.]+)', response.getvalue() , re.DOTALL)
            if match:
                if(verbose):
               	    print "Imgur page: http://imgur.com/" + match.group(1)
                    print "Original image: " + match.group(3)
                    print "Delete page: http://imgur.com/delete/" + match.group(2)
                return [match.group(1),match.group(3),match.group(2)]
            else :
                if(verbose):
                    print "The API Key given is not valid"
                return None
        
        elif (dest=='flickr'):
            global temp_token
            flickr = None 
            try :
                import flickrapi
            except ImportError:
            	print "Flickr API is not installed. Please install it from http://pypi.python.org/pypi/flickrapi"
                return False
            try :
                if (not(api_key==None and api_secret==None)):
            	    self.flickr = flickrapi.FlickrAPI(api_key,api_secret,cache=True)
            	    self.flickr.cache = flickrapi.SimpleCache(timeout=3600, max_entries=200)
            	    self.flickr.authenticate_console('write')
            	    temp_token = (api_key,api_secret)
            	else :
            	    try :
            	        self.flickr = flickrapi.FlickrAPI(temp_token[0],temp_token[1],cache=True)
            	        self.flickr.authenticate_console('write')
            	    except NameError :
            	        print "API key and Secret key are not set."
            	        return           	            	    
            except :
            	print "The API Key and Secret Key are not valid"
            	return False
            if (self.filename) :	
                try :
            	    self.flickr.upload(self.filename,self.filehandle)
                except :
            	    print "Uploading Failed !"
            	    return False
            else :
            	 import tempfile
                 tf=tempfile.NamedTemporaryFile(suffix='.jpg')
                 self.save(tf.name)
	    	 temp = Image(tf.name)
	    	 self.flickr.upload(tf.name,temp.filehandle)
            return True

    def scale(self, width, height = -1):
        """
        **SUMMARY**

        Scale the image to a new width and height.

        If no height is provided, the width is considered a scaling value.
        
        **PARAMETERS**
        
        * *width* - either the new width in pixels, if the height parameter is > 0, or if this value
          is a floating point value, this is the scaling factor. 

        * *height* - the new height in pixels.

        **RETURNS**

        The resized image. 
  
        **EXAMPLE**
        
        >>> img.scale(200, 100) #scales the image to 200px x 100px
        >>> img.scale(2.0) #enlarges the image to 2x its current size
        
        
        .. Warning:: 
          The two value scale command is deprecated. To set width and height
          use the resize function. 
        
        :py:meth:`resize`
        
        """
        w, h = width, height
        if height == -1:
          w = int(self.width * width)
          h = int(self.height * width)
          if( w > MAX_DIMENSION or h > MAX_DIMENSION or h < 1 or w < 1 ):
              logger.warning("Holy Heck! You tried to make an image really big or impossibly small. I can't scale that")
              return self
           

        scaled_bitmap = cv.CreateImage((w, h), 8, 3)
        cv.Resize(self.getBitmap(), scaled_bitmap)
        return Image(scaled_bitmap, colorSpace=self._colorSpace)

    
    def resize(self, w=None,h=None):
        """
        **SUMMARY**

        This method resizes an image based on a width, a height, or both. 
        If either width or height is not provided the value is inferred by keeping the aspect ratio. 
        If both values are provided then the image is resized accordingly.
        
        **PARAMETERS**

        * *width* - The width of the output image in pixels.

        * *height* - The height of the output image in pixels.
  
        **RETURNS** 
        
        Returns a resized image, if the size is invalid a warning is issued and
        None is returned. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> img2 = img.resize(w=1024) # h is guessed from w
        >>> img3 = img.resize(h=1024) # w is guessed from h
        >>> img4 = img.resize(w=200,h=100)

        """
        retVal = None
        if( w is None and h is None ):
            logger.warning("Image.resize has no parameters. No operation is performed")
            return None
        elif( w is not None and h is None):
            sfactor = float(w)/float(self.width)
            h = int( sfactor*float(self.height) )
        elif( w is None and h is not None):
            sfactor = float(h)/float(self.height)
            w = int( sfactor*float(self.width) )
        if( w > MAX_DIMENSION or h > MAX_DIMENSION ):
            logger.warning("Image.resize Holy Heck! You tried to make an image really big or impossibly small. I can't scale that")
            return retVal           
        scaled_bitmap = cv.CreateImage((w, h), 8, 3)
        cv.Resize(self.getBitmap(), scaled_bitmap)
        return Image(scaled_bitmap, colorSpace=self._colorSpace)
        

    def smooth(self, algorithm_name='gaussian', aperture=(3,3), sigma=0, spatial_sigma=0, grayscale=False, aperature=None):
        """
        **SUMMARY**

        Smooth the image, by default with the Gaussian blur.  If desired,
        additional algorithms and apertures can be specified.  Optional parameters
        are passed directly to OpenCV's cv.Smooth() function.

        If grayscale is true the smoothing operation is only performed on a single channel
        otherwise the operation is performed on each channel of the image. 
       
        for OpenCV versions >= 2.3.0 it is advisible to take a look at 
               - :py:meth:`bilateralFilter`
               - :py:meth:`medianFilter`
               - :py:meth:`blur`
               - :py:meth:`gaussianBlur`
           
        **PARAMETERS**

        * *algorithm_name* - valid options are 'blur' or gaussian, 'bilateral', and 'median'.
          
          * `Median Filter <http://en.wikipedia.org/wiki/Median_filter>`_
          
          * `Gaussian Blur <http://en.wikipedia.org/wiki/Gaussian_blur>`_
          
          * `Bilateral Filter <http://en.wikipedia.org/wiki/Bilateral_filter>`_

        * *aperture* - A tuple for the aperture of the gaussian blur as an (x,y) tuple. 
                     - Note there was rampant spelling mistakes in both smooth & sobel,
                       aperture is spelled as such, and not "aperature". This code is backwards
                       compatible.
       
        .. Warning:: 
          These must be odd numbers.

        * *sigma* -

        * *spatial_sigma* - 

        * *grayscale* - Return just the grayscale image. 



        **RETURNS**
        
        The smoothed image.

        **EXAMPLE**
        
        >>> img = Image("Lenna") 
        >>> img2 = img.smooth()
        >>> img3 = img.smooth('median')

        **SEE ALSO**

        :py:meth:`bilateralFilter`
        :py:meth:`medianFilter`
        :py:meth:`blur`
        
        """
        # see comment on argument documentation (spelling error)
        aperture = aperature if aperature else aperture

        if is_tuple(aperture):
            win_x, win_y = aperture
            if win_x <= 0 or win_y <= 0 or win_x % 2 == 0 or win_y % 2 == 0:  
                logger.warning("The aperture (x,y) must be odd number and greater than 0.")
                return None
        else:
            raise ValueError("Please provide a tuple to aperture, got: %s" % type(aperture))


        #gauss and blur can work in-place, others need a buffer frame
        #use a string to ID rather than the openCV constant
        if algorithm_name == "blur":
            algorithm = cv.CV_BLUR
        elif algorithm_name == "bilateral":
            algorithm = cv.CV_BILATERAL
            win_y = win_x #aperture must be square
        elif algorithm_name == "median":
            algorithm = cv.CV_MEDIAN
            win_y = win_x #aperture must be square
        else:
            algorithm = cv.CV_GAUSSIAN #default algorithm is gaussian 
        
        if grayscale:
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
            cv.Merge(bo,go,ro, None, newimg)

        return Image(newimg, colorSpace=self._colorSpace)


    def medianFilter(self, window='',grayscale=False):
        """
        **SUMMARY**
        
        Smooths the image, with the median filter. Performs a median filtering operation to denoise/despeckle the image.
        The optional parameter is the window size.
        see : http://en.wikipedia.org/wiki/Median_filter 

        **Parameters**
        * *window* - should be in the form a tuple (win_x,win_y). Where win_x should be equal to win_y. 
                   - By default it is set to 3x3, i.e window = (3x3).        
        
        **Note**
        win_x and win_y should be greater than zero, a odd number and equal.  
        
        For OpenCV versions <= 2.3.0 
        -- this acts as Convience function derived from the :py:meth:`smooth` method. Which internally calls cv.Smooth
        
        For OpenCV versions >= 2.3.0
        -- cv2.medianBlur function is called.
        """
        try:
            import cv2
            new_version = True
        except :
            new_version = False
            pass    
        
        
        if is_tuple(window):
            win_x, win_y = window
            if ( win_x>=0 and win_y>=0 and win_x%2==1 and win_y%2==1 ) :
                if win_x != win_y :
                    win_x=win_y
            else :
                logger.warning("The aperture (win_x,win_y) must be odd number and greater than 0.")
                return None
        
        elif( is_number(window) ): 
            win_x = window
        else :
            win_x = 3 #set the default aperture window size (3x3)

        if ( not new_version ) : 
            grayscale_ = grayscale
            return self.smooth(algorithm_name='median', aperture=(win_x,win_y),grayscale=grayscale_)
        else :
            if (grayscale) :
                img_medianBlur = cv2.medianBlur(self.getGrayNumpy(),win_x)
                return Image(img_medianBlur, colorSpace=ColorSpace.GRAY)
            else :        
                img_medianBlur = cv2.medianBlur(self.getNumpy()[:,:, ::-1].transpose([1,0,2]),win_x)
                img_medianBlur = img_medianBlur[:,:, ::-1].transpose([1,0,2]) 
                return Image(img_medianBlur, colorSpace=self._colorSpace)    
    
    
    def bilateralFilter(self, diameter=5,sigmaColor=10, sigmaSpace=10,grayscale=False):
        """
        **SUMMARY**
        
        Smooths the image, using bilateral filtering. Potential of bilateral filtering is for the removal of texture.
        The optional parameter are diameter, sigmaColor, sigmaSpace.

        Bilateral Filter 
        see : http://en.wikipedia.org/wiki/Bilateral_filter
        see : http://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/MANDUCHI1/Bilateral_Filtering.html  
        
        **Parameters**
        
        * *diameter* - A tuple for the window of the form (diameter,diameter). By default window = (3x3). ( for OpenCV versions <= 2.3.0)
                     - Diameter of each pixel neighborhood that is used during filtering. ( for OpenCV versions >= 2.3.0)
                     

        * *sigmaColor* - Filter the specified value in the color space. A larger value of the parameter means that farther colors within the pixel neighborhood (see sigmaSpace ) will be mixed together, resulting in larger areas of semi-equal color.
        
        * *sigmaSpace* - Filter the specified value in the coordinate space. A larger value of the parameter means that farther pixels will influence each other as long as their colors are close enough
        
        **NOTE**
        For OpenCV versions <= 2.3.0 
        -- this acts as Convience function derived from the :py:meth:`smooth` method. Which internally calls cv.Smooth.
        -- where aperture(window) is (diameter,diameter)
        -- sigmaColor and sigmanSpace become obsolete
        
        For OpenCV versions higher than 2.3.0. i.e >= 2.3.0
        -- cv.bilateralFilter function is called
        -- If the sigmaColor and sigmaSpace values are small (< 10), the filter will not have much effect, whereas if they are large (> 150), they will have a very strong effect, making the image look 'cartoonish'
        -- It is recommended to use diamter=5 for real time applications, and perhaps diameter=9 for offile applications that needs heavy noise filtering.
        """
        try:
            import cv2
            new_version = True
        except :
            new_version = False
            pass    
        
        if is_tuple(diameter):
            win_x, win_y = diameter
            if ( win_x>=0 and win_y>=0 and win_x%2==1 and win_y%2==1 ) :
                if win_x != win_y :
                    diameter = (win_x, win_y)
            else :
                logger.warning("The aperture (win_x,win_y) must be odd number and greater than 0.")
                return None
        
        elif( is_number(diameter) ): 
            pass
            
        else :
            win_x = 3 #set the default aperture window size (3x3)
            diameter = (win_x,win_x)
             
        if ( not new_version ) : 
            grayscale_ = grayscale
            if( is_number(diameter) ) :
                diameter = (diameter,diameter)
            return self.smooth(algorithm_name='bilateral', aperture=diameter,grayscale=grayscale_)
        else :
            if (grayscale) :
                img_bilateral = cv2.bilateralFilter(self.getGrayNumpy(),diameter,sigmaColor, sigmaSpace)
                return Image(img_bilateral, colorSpace=ColorSpace.GRAY)
            else :    
                img_bilateral = cv2.bilateralFilter(self.getNumpy()[:,:, ::-1].transpose([1,0,2]),diameter,sigmaColor, sigmaSpace)
                img_bilateral = img_bilateral[:,:, ::-1].transpose([1,0,2]) 
                return Image(img_bilateral,colorSpace=self._colorSpace)    
    
    def blur(self, window = '', grayscale=False):
        """
        **SUMMARY**
        
        Smoothes an image using the normalized box filter.
        The optional parameter is window.

        see : http://en.wikipedia.org/wiki/Blur
        
        **Parameters**
        
        * *window* - should be in the form a tuple (win_x,win_y).
                   - By default it is set to 3x3, i.e window = (3x3).        

        **NOTE**
        For OpenCV versions <= 2.3.0 
        -- this acts as Convience function derived from the :py:meth:`smooth` method. Which internally calls cv.Smooth
        
        For OpenCV versions higher than 2.3.0. i.e >= 2.3.0
        -- cv.blur function is called
        """
        try:
            import cv2
            new_version = True
        except :
            new_version = False
            pass    
        
        if is_tuple(window):
            win_x, win_y = window
            if ( win_x<=0 or win_y<=0 ) :
                logger.warning("win_x and win_y should be greater than 0.")
                return None          
        elif( is_number(window) ): 
            window = (window,window)
        else :
            window = (3,3)
        
        if ( not new_version ) : 
            grayscale_ = grayscale
            return self.smooth(algorithm_name='blur', aperture=window, grayscale=grayscale_)
        else :
            if grayscale:
                img_blur = cv2.blur(self.getGrayNumpy(),window)
                return Image(img_blur,colorSpace=ColorSpace.GRAY)
            else :
                img_blur = cv2.blur(self.getNumpy()[:,:, ::-1].transpose([1,0,2]),window)
                img_blur = img_blur[:,:, ::-1].transpose([1,0,2]) 
                return Image(img_blur,colorSpace=self._colorSpace)    
            
    def gaussianBlur(self, window = '', sigmaX=0 , sigmaY=0 ,grayscale=False):
        """
        **SUMMARY**
        
        Smoothes an image, typically used to reduce image noise and reduce detail.
        The optional parameter is window.

        see : http://en.wikipedia.org/wiki/Gaussian_blur
        
        **Parameters**
        
        * *window* - should be in the form a tuple (win_x,win_y). Where win_x and win_y should be positive and odd.
                   - By default it is set to 3x3, i.e window = (3x3).
                           
        * *sigmaX* - Gaussian kernel standard deviation in X direction.
        
        * *sigmaY* - Gaussian kernel standard deviation in Y direction.
        
        * *grayscale* - If true, the effect is applied on grayscale images.
        
        **NOTE**
        For OpenCV versions <= 2.3.0 
        -- this acts as Convience function derived from the :py:meth:`smooth` method. Which internally calls cv.Smooth
        
        For OpenCV versions higher than 2.3.0. i.e >= 2.3.0
        -- cv.GaussianBlur function is called
        """
        try:
            import cv2
            ver = cv2.__version__
            new_version = False
            #For OpenCV versions till 2.4.0,  cv2.__versions__ are of the form "$Rev: 4557 $" 
            if not ver.startswith('$Rev:'):
	        if int(ver.replace('.','0'))>=20300 :
                    new_version = True
        except :
            new_version = False
            pass    
        
        if is_tuple(window):
            win_x, win_y = window
            if ( win_x>=0 and win_y>=0 and win_x%2==1 and win_y%2==1 ) :
                pass
            else :
                logger.warning("The aperture (win_x,win_y) must be odd number and greater than 0.")
                return None
        
        elif( is_number(window) ): 
            window = (window, window)
     
        else :
            window = (3,3) #set the default aperture window size (3x3)
        
        if ( not new_version ) : 
            grayscale_ = grayscale
            return self.smooth(algorithm_name='blur', aperture=window, grayscale=grayscale_)
        else :
            if grayscale :
                img_guass = self.getGrayNumpy()
                cv2.GaussianBlur(self.getGrayNumpy(),window,sigmaX,img_guass,sigmaY)
                return Image(img_guass, colorSpace=ColorSpace.GRAY)
            
            else :    
                img_guass =  self.getNumpy()[:,:, ::-1].transpose([1,0,2])
                cv2.GaussianBlur(self.getNumpy()[:,:, ::-1].transpose([1,0,2]),window,sigmaX,img_guass,sigmaY)
                img_guass = img_guass[:,:, ::-1].transpose([1,0,2]) 
                return Image(img_guass,colorSpace=self._colorSpace)

    def invert(self):
        """
        **SUMMARY**

        Invert (negative) the image note that this can also be done with the
        unary minus (-) operator. For binary image this turns black into white and white into black (i.e. white is the new black). 

        **RETURNS**
        
        The opposite of the current image.

        **EXAMPLE**
        
        >>> img  = Image("polar_bear_in_the_snow.png")
        >>> img.invert().save("black_bear_at_night.png")

        **SEE ALSO**

        :py:meth:`binarize`

        """
        return -self 


    def grayscale(self):
        """
        **SUMMARY**

        This method returns a gray scale version of the image. It makes everything look like an old movie.

        **RETURNS**

        A grayscale SimpleCV image.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> img.grayscale().binarize().show()

        **SEE ALSO**

        :py:meth:`binarize`
        """ 
        return Image(self._getGrayscaleBitmap(), colorSpace = ColorSpace.GRAY)


    def flipHorizontal(self):
        """
        **SUMMARY**
        
        Horizontally mirror an image.
        
        
        .. Warning:: 
          Note that flip does not mean rotate 180 degrees! The two are different.
        
        **RETURNS**
        
        The flipped SimpleCV image.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> upsidedown = img.flipHorizontal()
        
        
        **SEE ALSO**
        
        :py:meth:`flipVertical`
        :py:meth:`rotate`
        
        """
        newimg = self.getEmpty()
        cv.Flip(self.getBitmap(), newimg, 1)
        return Image(newimg, colorSpace=self._colorSpace) 
    
    def flipVertical(self):
        """
        **SUMMARY**
        
        Vertically mirror an image.
        
        
        .. Warning:: 
          Note that flip does not mean rotate 180 degrees! The two are different.
        
        **RETURNS**

        The flipped SimpleCV image.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> upsidedown = img.flipHorizontal()


        **SEE ALSO**
        
        :py:meth:`rotate`
        :py:meth:`flipHorizontal`

        """
  
        newimg = self.getEmpty()
        cv.Flip(self.getBitmap(), newimg, 0)
        return Image(newimg, colorSpace=self._colorSpace)     

    
    def stretch(self, thresh_low = 0, thresh_high = 255):
        """
        **SUMMARY**
        
        The stretch filter works on a greyscale image, if the image
        is color, it returns a greyscale image.  The filter works by
        taking in a lower and upper threshold.  Anything below the lower
        threshold is pushed to black (0) and anything above the upper
        threshold is pushed to white (255)

        **PARAMETERS**

        * *thresh_low* - The lower threshold for the stretch operation. 
          This should be a value between 0 and 255. 

        * *thresh_high* - The upper threshold for the stretch operation. 
          This should be a value between 0 and 255. 

        **RETURNS**
        
        A gray scale version of the image with the appropriate histogram stretching. 

        
        **EXAMPLE**
        
        >>> img = Image("orson_welles.jpg")
        >>> img2 = img.stretch(56.200)
        >>> img2.show()
        
        **NOTES**

        TODO - make this work on RGB images with thresholds for each channel. 

        **SEE ALSO**

        :py:meth:`binarize`
        :py:meth:`equalize`

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
        **SUMMARY**

        Do a binary threshold the image, changing all values below thresh to maxv
        and all above to black.  If a color tuple is provided, each color channel
        is thresholded separately.
    

        If threshold is -1 (default), an adaptive method (OTSU's method) is used. 
        If then a blocksize is specified, a moving average over each region of block*block 
        pixels a threshold is applied where threshold = local_mean - p.

        **PARAMETERS**
        
        * *thresh* - the threshold as an integer or an (r,g,b) tuple , where pixels below (darker) than thresh are set to to max value,
          and all values above this value are set to black. If this parameter is -1 we use Otsu's method.

        * *maxv* - The maximum value for pixels below the threshold. Ordinarily this should be 255 (white)

        * *blocksize* - the size of the block used in the adaptive binarize operation.

        .. Warning:: 
          This parameter must be an odd number.

        * *p* - The difference from the local mean to use for thresholding in Otsu's method. 
        
        **RETURNS**

        A binary (two colors, usually black and white) SimpleCV image. This works great for the findBlobs
        family of functions.
        
        **EXAMPLE**
        
        Example of a vanila threshold versus an adaptive threshold:

        >>> img = Image("orson_welles.jpg")
        >>> b1 = img.binarize(128)
        >>> b2 = img.binarize(blocksize=11,p=7)
        >>> b3 = b1.sideBySide(b2)
        >>> b3.show()
        

        **NOTES**
        
        `Otsu's Method Description<http://en.wikipedia.org/wiki/Otsu's_method>`

        **SEE ALSO**

        :py:meth:`threshold`
        :py:meth:`findBlobs`
        :py:meth:`invert`
        :py:meth:`dilate`
        :py:meth:`erode`

        """
        if is_tuple(thresh):
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
        **SUMMARY**
        
        This method finds the average color of all the pixels in the image.
        
        **RETURNS**
        
        A tuple of the average image values. Tuples are in the channel order. *For most images this means the results are (B,G,R).*

        **EXAMPLE** 

        >>> img = Image('lenna')
        >>> colors = img.meanColor()
      
        """
        # I changed this to keep channel order - KAS
        return tuple(cv.Avg(self.getBitmap())[0:3])  

    def findCorners(self, maxnum = 50, minquality = 0.04, mindistance = 1.0):
        """
        **SUMMARY**
        
        This will find corner Feature objects and return them as a FeatureSet
        strongest corners first.  The parameters give the number of corners to look
        for, the minimum quality of the corner feature, and the minimum distance
        between corners.
        
        **PARAMETERS**
   
        * *maxnum* - The maximum number of corners to return.

        * *minquality* - The minimum quality metric. This shoudl be a number between zero and one. 

        * *mindistance* - The minimum distance, in pixels, between successive corners. 

        **RETURNS**

        A featureset of :py:class:`Corner` features or None if no corners are found.


        **EXAMPLE**
        
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

        **SEE ALSO**

        :py:class:`Corner`
        :py:meth:`findKeypoints`

        """
        #initialize buffer frames
        eig_image = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_32F, 1)
        temp_image = cv.CreateImage(cv.GetSize(self.getBitmap()), cv.IPL_DEPTH_32F, 1)


        corner_coordinates = cv.GoodFeaturesToTrack(self._getGrayscaleBitmap(), eig_image, temp_image, maxnum, minquality, mindistance, None)


        corner_features = []   
        for (x, y) in corner_coordinates:
            corner_features.append(Corner(self, x, y))


        return FeatureSet(corner_features)


    def findBlobs(self, threshval = -1, minsize=10, maxsize=0, threshblocksize=0, threshconstant=5,appx_level=3):
        """
        **SUMMARY**
        
        Find blobs  will look for continuous
        light regions and return them as Blob features in a FeatureSet.  Parameters
        specify the binarize filter threshold value, and minimum and maximum size for blobs.  
        If a threshold value is -1, it will use an adaptive threshold.  See binarize() for
        more information about thresholding.  The threshblocksize and threshconstant
        parameters are only used for adaptive threshold.
        
        
        **PARAMETERS**
        
        * *threshval* - the threshold as an integer or an (r,g,b) tuple , where pixels below (darker) than thresh are set to to max value,
          and all values above this value are set to black. If this parameter is -1 we use Otsu's method.

        * *minsize* - the minimum size of the blobs, in pixels, of the returned blobs. This helps to filter out noise.
        
        * *maxsize* - the maximim size of the blobs, in pixels, of the returned blobs.

        * *threshblocksize* - the size of the block used in the adaptive binarize operation. *TODO - make this match binarize*
    
        * *appx_level* - The blob approximation level - an integer for the maximum distance between the true edge and the 
          approximation edge - lower numbers yield better approximation. 
        
          .. Warning:: 
          This parameter must be an odd number.
          
        * *threshconstant* - The difference from the local mean to use for thresholding in Otsu's method. *TODO - make this match binarize*
 
    
        **RETURNS**
        
        Returns a featureset (basically a list) of :py:class:`blob` features. If no blobs are found this method returns None.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> fs = img.findBlobs() 
        >>> if( fs is not None ):
        >>>     fs.draw()

        **NOTES**

        .. Warning:: 
          For blobs that live right on the edge of the image OpenCV reports the position and width
          height as being one over for the true position. E.g. if a blob is at (0,0) OpenCV reports 
          its position as (1,1). Likewise the width and height for the other corners is reported as
          being one less than the width and height. This is a known bug. 

        **SEE ALSO**
        :py:meth:`threshold`
        :py:meth:`binarize`
        :py:meth:`invert`
        :py:meth:`dilate`
        :py:meth:`erode`
        :py:meth:`findBlobsFromPalette`
        :py:meth:`smartFindBlobs`
        """
        if (maxsize == 0):  
            maxsize = self.width * self.height
        #create a single channel image, thresholded to parameters
            
        blobmaker = BlobMaker()
        blobs = blobmaker.extractFromBinary(self.binarize(threshval, 255, threshblocksize, threshconstant).invert(),
            self, minsize = minsize, maxsize = maxsize,appx_level=appx_level)
    
        if not len(blobs):
            return None
            
        return FeatureSet(blobs).sortArea()
    
    def findSkintoneBlobs(self, minsize=10, maxsize=0,dilate_iter=1):
        """
        **SUMMARY**
        
        Find Skintone blobs will look for continuous
        regions of Skintone in a color image and return them as Blob features in a FeatureSet.  
        Parameters specify the binarize filter threshold value, and minimum and maximum size for 
        blobs. If a threshold value is -1, it will use an adaptive threshold.  See binarize() for
        more information about thresholding.  The threshblocksize and threshconstant
        parameters are only used for adaptive threshold.
        
        
        **PARAMETERS**
        
        * *minsize* - the minimum size of the blobs, in pixels, of the returned blobs. This helps to filter out noise.
        
        * *maxsize* - the maximim size of the blobs, in pixels, of the returned blobs.

    	* *dilate_iter* - the number of times to run the dilation operation.   
    
        **RETURNS**
        
        Returns a featureset (basically a list) of :py:class:`blob` features. If no blobs are found this method returns None.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> fs = img.findSkintoneBlobs() 
        >>> if( fs is not None ):
        >>>     fs.draw()

        **NOTES**
        It will be really awesome for making UI type stuff, where you want to track a hand or a face.

        **SEE ALSO**
        :py:meth:`threshold`
        :py:meth:`binarize`
        :py:meth:`invert`
        :py:meth:`dilate`
        :py:meth:`erode`
        :py:meth:`findBlobsFromPalette`
        :py:meth:`smartFindBlobs`
        """
        if (maxsize == 0):  
            maxsize = self.width * self.height
        mask = self.getSkintoneMask(dilate_iter)
	blobmaker = BlobMaker()
        blobs = blobmaker.extractFromBinary(mask, self, minsize = minsize, maxsize = maxsize)
        if not len(blobs):
            return None
        return FeatureSet(blobs).sortArea()    
    
    def getSkintoneMask(self, dilate_iter=0):
        """
        **SUMMARY**
        
        Find Skintone mask will look for continuous
        regions of Skintone in a color image and return a binary mask where the white pixels denote Skintone region.         
        
        **PARAMETERS**
        
    	* *dilate_iter* - the number of times to run the dilation operation.  
        **RETURNS**
        
        Returns a binary mask.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> mask = img.findSkintoneMask() 
        >>> mask.show()
        
        """
        if( self._colorSpace != ColorSpace.YCrCb ):
            YCrCb = self.toYCrCb()
        else:
            YCrCb = self
    
        Y =  np.ones((256,1),dtype=uint8)*0
	Y[5:] = 255
	Cr =  np.ones((256,1),dtype=uint8)*0
        Cr[140:180] = 255
	Cb =  np.ones((256,1),dtype=uint8)*0
	Cb[77:135] = 255
	Y_img = YCrCb.getEmpty(1)
	Cr_img = YCrCb.getEmpty(1)
	Cb_img = YCrCb.getEmpty(1)
	cv.Split(YCrCb.getBitmap(),Y_img,Cr_img,Cb_img,None)
	cv.LUT(Y_img,Y_img,cv.fromarray(Y))
	cv.LUT(Cr_img,Cr_img,cv.fromarray(Cr))
	cv.LUT(Cb_img,Cb_img,cv.fromarray(Cb))
	temp = self.getEmpty()
	cv.Merge(Y_img,Cr_img,Cb_img,None,temp)
	mask=Image(temp,colorSpace = ColorSpace.YCrCb)
	mask = mask.binarize((128,128,128))
	mask = mask.toRGB().binarize()
	mask.dilate(dilate_iter)
	return mask
        
    #this code is based on code that's based on code from
    #http://blog.jozilla.net/2008/06/27/fun-with-python-opencv-and-face-detection/
    def findHaarFeatures(self, cascade, scale_factor=1.2, min_neighbors=2, use_canny=cv.CV_HAAR_DO_CANNY_PRUNING, min_size=(20,20)):
        """
        **SUMMARY**

        A Haar like feature cascase is a really robust way of finding the location
        of a known object. This technique works really well for a few specific applications
        like face, pedestrian, and vehicle detection. It is worth noting that this
        approach **IS NOT A MAGIC BULLET** . Creating a cascade file requires a large
        number of images that have been sorted by a human.vIf you want to find Haar 
        Features (useful for face detection among other purposes) this will return 
        Haar feature objects in a FeatureSet.  

        For more information, consult the cv.HaarDetectObjects documentation.
   
        To see what features are available run img.listHaarFeatures() or you can
        provide your own haarcascade file if you have one available.
        
        Note that the cascade parameter can be either a filename, or a HaarCascade
        loaded with cv.Load(), or a SimpleCV HaarCascade object. 

        **PARAMETERS**

        * *cascade* - The Haar Cascade file, this can be either the path to a cascade
          file or a HaarCascased SimpleCV object that has already been
          loaded.

        * *scale_factor* - The scaling factor for subsequent rounds of the Haar cascade 
          (default 1.2) in terms of a percentage (i.e. 1.2 = 20% increase in size)

        * *min_neighbors* - The minimum number of rectangles that makes up an object. Ususally
          detected faces are clustered around the face, this is the number
          of detections in a cluster that we need for detection. Higher
          values here should reduce false positives and decrease false negatives.

        * *use-canny* - Whether or not to use Canny pruning to reject areas with too many edges 
          (default yes, set to 0 to disable) 

        * *min_size* - Minimum window size. By default, it is set to the size
          of samples the classifier has been trained on ((20,20) for face detection) 

        **RETURNS**

        A feature set of HaarFeatures 
        
        **EXAMPLE**

        >>> faces = HaarCascade("./SimpleCV/Features/HaarCascades/face.xml","myFaces")
        >>> cam = Camera()
        >>> while True:
        >>>     f = cam.getImage().findHaarFeatures(faces)
        >>>     if( f is not None ):
        >>>          f.show()

        **NOTES**

        OpenCV Docs:
        - http://opencv.willowgarage.com/documentation/python/objdetect_cascade_classification.html

        Wikipedia:
        - http://en.wikipedia.org/wiki/Viola-Jones_object_detection_framework
        - http://en.wikipedia.org/wiki/Haar-like_features

        The video on this pages shows how Haar features and cascades work to located faces:
        - http://dismagazine.com/dystopia/evolved-lifestyles/8115/anti-surveillance-how-to-hide-from-machines/
        
        """
        storage = cv.CreateMemStorage(0)


        #lovely.  This segfaults if not present
        if isinstance(cascade, basestring):
          from SimpleCV.Features.HaarCascade import HaarCascade
          cascade = HaarCascade(cascade)
          if not cascade.getCascade(): return None
          
         
        # added all of the arguments from the opencv docs arglist
        objects = cv.HaarDetectObjects(self._getEqualizedGrayscaleBitmap(),
                cascade.getCascade(), storage, scale_factor, min_neighbors,
                use_canny, min_size)

        if objects: 
            return FeatureSet([HaarFeature(self, o, cascade) for o in objects])
    
        return None


    def drawCircle(self, ctr, rad, color = (0, 0, 0), thickness = 1):
        """
        **SUMMARY**
        
        Draw a circle on the image.
        
        **PARAMETERS**
        
        * *ctr* - The center of the circle as an (x,y) tuple.
        * *rad* - The radius of the circle in pixels
        * *color* - A color tuple (default black)
        * *thickness* - The thickness of the circle, -1 means filled in. 

        **RETURNS**

        .. Warning:: 
          This is an inline operation. Nothing is returned, but a circle is drawn on the images's 
          drawing layer. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> img.drawCircle((img.width/2,img.height/2),r=50,color=Colors.RED,width=3)
        >>> img.show()

        **NOTES**

        .. Warning:: 
          Note that this function is depricated, try to use DrawingLayer.circle() instead.

        **SEE ALSO**
        
        :py:meth:`drawLine`
        :py:meth:`drawText`
        :py:meth:`dl`
        :py:meth:`drawRectangle`
        :py:class:`DrawingLayer`

        """
        if( thickness < 0):
            self.getDrawingLayer().circle((int(ctr[0]), int(ctr[1])), int(rad), color, int(thickness),filled=True)
        else:
            self.getDrawingLayer().circle((int(ctr[0]), int(ctr[1])), int(rad), color, int(thickness))
    
    
    def drawLine(self, pt1, pt2, color = (0, 0, 0), thickness = 1):
        """
        **SUMMARY**
        Draw a line on the image.
        
        
        **PARAMETERS**
        
        * *pt1* - the first point for the line (tuple).
        * *pt2* - the second point on the line (tuple).
        * *color* - a color tuple (default black).
        * *thickness* the thickness of the line in pixels.

        **RETURNS**

        .. Warning:: 
          This is an inline operation. Nothing is returned, but a circle is drawn on the images's 
          drawing layer. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> img.drawLine((0,0),(img.width,img.height),color=Color.RED,thickness=3)
        >>> img.show()
        
        **NOTES**

        .. Warning:: 
           Note that this function is depricated, try to use DrawingLayer.line() instead.

        **SEE ALSO**
        
        :py:meth:`drawText`
        :py:meth:`dl`
        :py:meth:`drawCircle`
        :py:meth:`drawRectangle`
        
        """
        pt1 = (int(pt1[0]), int(pt1[1]))
        pt2 = (int(pt2[0]), int(pt2[1]))
        self.getDrawingLayer().line(pt1, pt2, color, thickness)

    def size(self):
        """
        **SUMMARY**
        
        Returns a tuple that lists the width and height of the image.

        **RETURNS**
        
        The width and height as a tuple.

        
        """
        if self.width and self.height: 
            return cv.GetSize(self.getBitmap())
        else:
            return (0, 0)

    def isEmpty(self):
        """
        **SUMMARY**
        
        Checks if the image is empty by checking its width and height.

        **RETURNS**
        
        True if the image's size is (0, 0), False for any other size.
        
        """
        return self.size() == (0, 0)

    def split(self, cols, rows):
        """
        **SUMMARY**

        This method can be used to brak and image into a series of image chunks. 
        Given number of cols and rows, splits the image into a cols x rows 2d array 
        of cropped images
        
        **PARAMETERS**

        * *rows* - an integer number of rows.
        * *cols* - an integer number of cols.

        **RETURNS**

        A list of SimpleCV images.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> quadrant =img.split(2,2) 
        >>> for f in quadrant:
        >>>    f.show()
        >>>    time.sleep(1)
        

        **NOTES**
        
        TODO: This should return and ImageList

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
        **SUMMARY**

        Split the channels of an image into RGB (not the default BGR)
        single parameter is whether to return the channels as grey images (default)
        or to return them as tinted color image 

        **PARAMETERS**
        
        * *grayscale* - If this is true we return three grayscale images, one per channel. 
          if it is False return tinted images. 
          

        **RETURNS**
        
        A tuple of of 3 image objects.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> data = img.splitChannels()
        >>> for d in data:
        >>>    d.show()
        >>>    time.sleep(1)

        **SEE ALSO**

        :py:meth:`mergeChannels`
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
        **SUMMARY**

        Merge channels is the oposite of splitChannels. The image takes one image for each
        of the R,G,B channels and then recombines them into a single image. Optionally any of these
        channels can be None.

        **PARAMETERS**
        
        * *r* - The r or last channel  of the result SimpleCV Image.
        * *g* - The g or center channel of the result SimpleCV Image.
        * *b* - The b or first channel of the result SimpleCV Image.
          

        **RETURNS**
        
        A SimpleCV Image. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> [r,g,b] = img.splitChannels()
        >>> r = r.binarize()
        >>> g = g.binarize()
        >>> b = b.binarize()
        >>> result = img.mergeChannels(r,g,b)
        >>> result.show()


        **SEE ALSO**
        :py:meth:`splitChannels`

        """
        if( r is None and g is None and b is None ):
            logger.warning("ImageClass.mergeChannels - we need at least one valid channel")
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
        **SUMMARY**
        
        Apply a color correction curve in HSL space. This method can be used 
        to change values for each channel. The curves are :py:class:`ColorCurve` class objects.
        
        **PARAMETERS**
        
        * *hCurve* - the hue ColorCurve object.
        * *lCurve* - the lightnes / value ColorCurve object.
        * *sCurve* - the saturation ColorCurve object

        **RETURNS**

        A SimpleCV Image

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> hc = ColorCurve([[0,0], [100, 120], [180, 230], [255, 255]])
        >>> lc = ColorCurve([[0,0], [90, 120], [180, 230], [255, 255]])
        >>> sc = ColorCurve([[0,0], [70, 110], [180, 230], [240, 255]])
        >>> img2 = img.applyHLSCurve(hc,lc,sc)

        **SEE ALSO**

        :py:class:`ColorCurve`
        :py:meth:`applyRGBCurve`
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
        **SUMMARY**
        
        Apply a color correction curve in RGB space. This method can be used 
        to change values for each channel. The curves are :py:class:`ColorCurve` class objects.
        
        **PARAMETERS**
        
        * *rCurve* - the red ColorCurve object.
        * *gCurve* - the green ColorCurve object.
        * *bCurve* - the blue ColorCurve object.

        **RETURNS**

        A SimpleCV Image

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> rc = ColorCurve([[0,0], [100, 120], [180, 230], [255, 255]])
        >>> gc = ColorCurve([[0,0], [90, 120], [180, 230], [255, 255]])
        >>> bc = ColorCurve([[0,0], [70, 110], [180, 230], [240, 255]])
        >>> img2 = img.applyRGBCurve(rc,gc,bc)

        **SEE ALSO**

        :py:class:`ColorCurve`
        :py:meth:`applyHLSCurve`

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
        **SUMMARY**

        Intensity applied to all three color channels

        **PARAMETERS**
        
        * *curve* - a ColorCurve object.

        **RETURNS**

        A SimpleCV Image

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> rc = ColorCurve([[0,0], [100, 120], [180, 230], [255, 255]])
        >>> gc = ColorCurve([[0,0], [90, 120], [180, 230], [255, 255]])
        >>> bc = ColorCurve([[0,0], [70, 110], [180, 230], [240, 255]])
        >>> img2 = img.applyRGBCurve(rc,gc,bc)

        **SEE ALSO**

        :py:class:`ColorCurve`
        :py:meth:`applyHLSCurve`

        """
        return self.applyRGBCurve(curve, curve, curve)
      
      
    def colorDistance(self, color = Color.BLACK):
        """
        **SUMMARY**
      
        Returns an image representing the distance of each pixel from a given color
        tuple, scaled between 0 (the given color) and 255.  Pixels distant from the 
        given tuple will appear as brighter and pixels closest to the target color 
        will be darker.
    
    
        By default this will give image intensity (distance from pure black)

        **PARAMETERS**
      
        * *color*  - Color object or Color Tuple

        **RETURNS**
        
        A SimpleCV Image.
        
        **EXAMPLE** 
        
        >>> img = Image("logo")
        >>> img2 = img.colorDistance(color=Color.BLACK)
        >>> img2.show()

        
        **SEE ALSO**

        :py:meth:`binarize`
        :py:meth:`hueDistance`
        :py:meth:`findBlobsFromMask`
        """ 
        pixels = np.array(self.getNumpy()).reshape(-1, 3)   #reshape our matrix to 1xN
        distances = spsd.cdist(pixels, [color]) #calculate the distance each pixel is
        distances *= (255.0/distances.max()) #normalize to 0 - 255
        return Image(distances.reshape(self.width, self.height)) #return an Image
    
    def hueDistance(self, color = Color.BLACK, minsaturation = 20, minvalue = 20):
        """
        **SUMMARY**

        Returns an image representing the distance of each pixel from the given hue
        of a specific color.  The hue is "wrapped" at 180, so we have to take the shorter
        of the distances between them -- this gives a hue distance of max 90, which we'll 
        scale into a 0-255 grayscale image.
        
        The minsaturation and minvalue are optional parameters to weed out very weak hue
        signals in the picture, they will be pushed to max distance [255]

        
        **PARAMETERS**

        * *color* - Color object or Color Tuple.
        * *minsaturation*  - the minimum saturation value for color (from 0 to 255).
        * *minvalue*  - the minimum hue value for the color (from 0 to 255).
 
        **RETURNS**

        A simpleCV image.

        **EXAMPLE** 
        
        >>> img = Image("logo")
        >>> img2 = img.hueDistance(color=Color.BLACK)
        >>> img2.show()
        
        **SEE ALSO**

        :py:meth:`binarize`
        :py:meth:`hueDistance`
        :py:meth:`morphOpen`
        :py:meth:`morphClose`
        :py:meth:`morphGradient`
        :py:meth:`findBlobsFromMask`
        
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
        **SUMMARY**

        Apply a morphological erosion. An erosion has the effect of removing small bits of noise
        and smothing blobs. 

        This implementation uses the default openCV 3X3 square kernel 
        
        Erosion is effectively a local minima detector, the kernel moves over the image and
        takes the minimum value inside the kernel. 
        iterations - this parameters is the number of times to apply/reapply the operation
        
        * See: http://en.wikipedia.org/wiki/Erosion_(morphology).
        
        * See: http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-erode 
        
        * Example Use: A threshold/blob image has 'salt and pepper' noise. 
        
        * Example Code: /examples/MorphologyExample.py

        **PARAMETERS**
        
        * *iterations* - the number of times to run the erosion operation. 
        
        **RETURNS**

        A SimpleCV image. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> derp = img.binarize()
        >>> derp.erode(3).show()
        
        **SEE ALSO**
        :py:meth:`dilate`
        :py:meth:`binarize`
        :py:meth:`morphOpen`
        :py:meth:`morphClose`
        :py:meth:`morphGradient`
        :py:meth:`findBlobsFromMask`
        
        """
        retVal = self.getEmpty() 
        kern = cv.CreateStructuringElementEx(3, 3, 1, 1, cv.CV_SHAPE_RECT)
        cv.Erode(self.getBitmap(), retVal, kern, iterations)
        return Image(retVal, colorSpace=self._colorSpace)


    def dilate(self, iterations=1):
        """
        **SUMMARY**

        Apply a morphological dilation. An dilation has the effect of smoothing blobs while
        intensifying the amount of noise blobs. 
        This implementation uses the default openCV 3X3 square kernel 
        Erosion is effectively a local maxima detector, the kernel moves over the image and
        takes the maxima value inside the kernel. 

        * See: http://en.wikipedia.org/wiki/Dilation_(morphology)

        * See: http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-dilate

        * Example Use: A part's blob needs to be smoother 

        * Example Code: ./examples/MorphologyExample.py

        **PARAMETERS**
        
        * *iterations* - the number of times to run the dilation operation. 
        
        **RETURNS**

        A SimpleCV image. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> derp = img.binarize()
        >>> derp.dilate(3).show()
        
        **SEE ALSO**

        :py:meth:`erode`
        :py:meth:`binarize`
        :py:meth:`morphOpen`
        :py:meth:`morphClose`
        :py:meth:`morphGradient`
        :py:meth:`findBlobsFromMask`
        
        """
        retVal = self.getEmpty() 
        kern = cv.CreateStructuringElementEx(3, 3, 1, 1, cv.CV_SHAPE_RECT)
        cv.Dilate(self.getBitmap(), retVal, kern, iterations)
        return Image(retVal, colorSpace=self._colorSpace) 


    def morphOpen(self):
        """
        **SUMMARY**

        morphologyOpen applies a morphological open operation which is effectively
        an erosion operation followed by a morphological dilation. This operation
        helps to 'break apart' or 'open' binary regions which are close together. 


        * `Morphological opening on Wikipedia <http://en.wikipedia.org/wiki/Opening_(morphology)>`_

        * `OpenCV documentation <http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-morphologyex>`_       
      
        * Example Use: two part blobs are 'sticking' together.
        
        * Example Code: ./examples/MorphologyExample.py

        **RETURNS**

        A SimpleCV image. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> derp = img.binarize()
        >>> derp.morphOpen.show()
        
        **SEE ALSO**

        :py:meth:`erode`
        :py:meth:`dilate`
        :py:meth:`binarize`
        :py:meth:`morphClose`
        :py:meth:`morphGradient`
        :py:meth:`findBlobsFromMask`
        
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
        **SUMMARY**
        
        morphologyClose applies a morphological close operation which is effectively
        a dilation operation followed by a morphological erosion. This operation
        helps to 'bring together' or 'close' binary regions which are close together. 


        * See: `Closing <http://en.wikipedia.org/wiki/Closing_(morphology)>`_
       
        * See: `Morphology from OpenCV <http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-morphologyex>`_
        
        * Example Use: Use when a part, which should be one blob is really two blobs.   
        
        * Example Code: ./examples/MorphologyExample.py

        **RETURNS**

        A SimpleCV image. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> derp = img.binarize()
        >>> derp.morphClose.show()
        
        **SEE ALSO**

        :py:meth:`erode`
        :py:meth:`dilate`
        :py:meth:`binarize`
        :py:meth:`morphOpen`
        :py:meth:`morphGradient`
        :py:meth:`findBlobsFromMask`
        
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
        **SUMMARY**

        The morphological gradient is the difference betwen the morphological
        dilation and the morphological gradient. This operation extracts the 
        edges of a blobs in the image. 


        * `See Morph Gradient of Wikipedia <http://en.wikipedia.org/wiki/Morphological_Gradient>`_
     
        * `OpenCV documentation <http://opencv.willowgarage.com/documentation/cpp/image_filtering.html#cv-morphologyex>`_
        
        * Example Use: Use when you have blobs but you really just want to know the blob edges.
        
        * Example Code: ./examples/MorphologyExample.py


        **RETURNS**

        A SimpleCV image. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> derp = img.binarize()
        >>> derp.morphGradient.show()
        
        **SEE ALSO**

        :py:meth:`erode`
        :py:meth:`dilate`
        :py:meth:`binarize`
        :py:meth:`morphOpen`
        :py:meth:`morphClose`
        :py:meth:`findBlobsFromMask`
        
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
        **SUMMARY**

        Return a numpy array of the 1D histogram of intensity for pixels in the image
        Single parameter is how many "bins" to have.


        **PARAMETERS**

        * *numbins* - An interger number of bins in a histogram. 
        
        **RETURNS**

        A list of histogram bin values. 

        **EXAMPLE**
        
        >>> img = Image('lenna')
        >>> hist = img.histogram()

        **SEE ALSO**

        :py:meth:`hueHistogram`

        """
        gray = self._getGrayscaleBitmap()


        (hist, bin_edges) = np.histogram(np.asarray(cv.GetMat(gray)), bins=numbins)
        return hist.tolist()
        
    def hueHistogram(self, bins = 179):
        """
        **SUMMARY**
        
        Returns the histogram of the hue channel for the image


        **PARAMETERS**

        * *numbins* - An interger number of bins in a histogram. 
        
        **RETURNS**

        A list of histogram bin values. 

        **SEE ALSO**

        :py:meth:`histogram`

        """
        return np.histogram(self.toHSV().getNumpy()[:,:,2], bins = bins)[0]

    def huePeaks(self, bins = 179):
        """
        **SUMMARY**

        Takes the histogram of hues, and returns the peak hue values, which
        can be useful for determining what the "main colors" in a picture.
        
        The bins parameter can be used to lump hues together, by default it is 179
        (the full resolution in OpenCV's HSV format)
        
        Peak detection code taken from https://gist.github.com/1178136
        Converted from/based on a MATLAB script at http://billauer.co.il/peakdet.html
        
        Returns a list of tuples, each tuple contains the hue, and the fraction
        of the image that has it.

        **PARAMETERS**

        * *bins* - the integer number of bins, between 0 and 179.

        **RETURNS** 
        
        A list of (hue,fraction) tuples. 
        
        """
        #         keyword arguments:
        #         y_axis -- A list containg the signal over which to find peaks
        #         x_axis -- A x-axis whose values correspond to the 'y_axis' list and is used
        #             in the return to specify the postion of the peaks. If omitted the index
        #             of the y_axis is used. (default: None)
        #         lookahead -- (optional) distance to look ahead from a peak candidate to
        #             determine if it is the actual peak (default: 500) 
        #             '(sample / period) / f' where '4 >= f >= 1.25' might be a good value
        #         delta -- (optional) this specifies a minimum difference between a peak and
        #             the following points, before a peak may be considered a peak. Useful
        #             to hinder the algorithm from picking up false peaks towards to end of
        #             the signal. To work well delta should be set to 'delta >= RMSnoise * 5'.
        #             (default: 0)
        #                 Delta function causes a 20% decrease in speed, when omitted
        #                 Correctly used it can double the speed of the algorithm
        #         return --  Each cell of the lists contains a tupple of:
        #             (position, peak_value) 
        #             to get the average peak value do 'np.mean(maxtab, 0)[1]' on the results

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
        # TODO - this needs to be refactored
        if is_tuple(self.getMatrix()[tuple(reversed(coord))]):
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
        **SUMMARY**

        The maximum value of my image, and the other image, in each channel
        If other is a number, returns the maximum of that and the number

        **PARAMETERS**
        
        * *other* - Image or a number.

        **RETURNS**
 
        A SimpelCV image.

        """ 
        newbitmap = self.getEmpty() 
        if is_number(other):
            cv.MaxS(self.getBitmap(), other.getBitmap(), newbitmap)
        else:
            cv.Max(self.getBitmap(), other.getBitmap(), newbitmap)
        return Image(newbitmap, colorSpace=self._colorSpace)


    def min(self, other):
        """
        **SUMMARY**

        The minimum value of my image, and the other image, in each channel
        If other is a number, returns the minimum of that and the number

        **Parameter**

        * *other* - Image

        **Returns**

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


    def findBarcode(self):
        """
        **SUMMARY**
        This function requires zbar and the zbar python wrapper to be installed.

        To install please visit:
        http://zbar.sourceforge.net/

        On Ubuntu Linux 12.04 or greater:
        sudo apt-get install python-zbar
        
        **Returns**
        
        A :py:class:`FeatureSet` of :py:class:`Barcode` objects. If no barcodes are detected the method returns None.

        **EXAMPLE**

        >>> bc = cam.getImage()
        >>> barcodes = img.findBarcodes()
        >>> for b in barcodes:
        >>>     b.draw()

        **SEE ALSO**

        :py:class:`FeatureSet` 
        :py:class:`Barcode`

        """
        try:
          import zbar
        except:
          logger.warning('The zbar library is not installed, please install to read barcodes')
          return None

        #configure zbar
        scanner = zbar.ImageScanner()
        scanner.parse_config('enable')
        raw = self.getPIL().convert('L').tostring()
        width = self.width
        height = self.height

        # wrap image data
        image = zbar.Image(width, height, 'Y800', raw)

        # scan the image for barcodes
        scanner.scan(image)

        barcode = None
        # extract results
        for symbol in image:
            # do something useful with results
            barcode = symbol

        # clean up
        del(image)
        
        if barcode:
            f = Barcode(self, barcode)
            return FeatureSet([f])
            #~ return f
        else:
            return None


    #this function contains two functions -- the basic edge detection algorithm
    #and then a function to break the lines down given a threshold parameter
    def findLines(self, threshold=80, minlinelength=30, maxlinegap=10, cannyth1=50, cannyth2=100):
        """
        **SUMMARY**

        findLines will find line segments in your image and returns line feature 
        objects in a FeatureSet. This method uses the Hough (pronounced "HUFF") transform.

        See http://en.wikipedia.org/wiki/Hough_transform

        **PARAMETERS**
        
        * *threshold* - which determines the minimum "strength" of the line.
        * *minlinelength* - how many pixels long the line must be to be returned.
        * *maxlinegap* - how much gap is allowed between line segments to consider them the same line .
        * *cannyth1* - thresholds used in the edge detection step, refer to :py:meth:`_getEdgeMap` for details.
        * *cannyth2* - thresholds used in the edge detection step, refer to :py:meth:`_getEdgeMap` for details.
            
        **RETURNS**
        
        Returns a :py:class:`FeatureSet` of :py:class:`Line` objects. If no lines are found the method returns None.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> lines = img.findLines()
        >>> lines.draw()
        >>> img.show()
        
        **SEE ALSO**
        :py:class:`FeatureSet` 
        :py:class:`Line` 
        :py:meth:`edges`
        
        """
        em = self._getEdgeMap(cannyth1, cannyth2)
    
    
        lines = cv.HoughLines2(em, cv.CreateMemStorage(), cv.CV_HOUGH_PROBABILISTIC, 1.0, cv.CV_PI/180.0, threshold, minlinelength, maxlinegap)


        linesFS = FeatureSet()
        for l in lines:
            linesFS.append(Line(self, l))  
        return linesFS
    
    
    
    
    def findChessboard(self, dimensions = (8, 5), subpixel = True):
        """
        **SUMMARY**

        Given an image, finds a chessboard within that image.  Returns the Chessboard featureset.
        The Chessboard is typically used for calibration because of its evenly spaced corners.
        
        
        The single parameter is the dimensions of the chessboard, typical one can be found in \SimpleCV\tools\CalibGrid.png
   
        **PARAMETERS**

        * *dimensions* - A tuple of the size of the chessboard in width and height in grid objects.
        * *subpixel* - Boolean if True use sub-pixel accuracy, otherwise use regular pixel accuracy.

        **RETURNS** 
        
        A :py:class:`FeatureSet` of :py:class:`Chessboard` objects. If no chessboards are found None is returned.

        **EXAMPLE**
        
        >>> img = cam.getImage()
        >>> cb = img.findChessboard()
        >>> cb.draw()

        **SEE ALSO**
        
        :py:class:`FeatureSet` 
        :py:class:`Chessboard` 

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
        **SUMMARY**

        Finds an edge map Image using the Canny edge detection method.  Edges will be brighter than the surrounding area.

        The t1 parameter is roughly the "strength" of the edge required, and the value between t1 and t2 is used for edge linking.  
        
        For more information:

        * http://opencv.willowgarage.com/documentation/python/imgproc_feature_detection.html

        * http://en.wikipedia.org/wiki/Canny_edge_detector

        **PARAMETERS**

        * *t1* - Int - the lower Canny threshold.
        * *t2* - Int - the upper Canny threshold.
            
        **RETURNS** 

        A SimpleCV image where the edges are white on a black background.

        **EXAMPLE**

        >>> cam = Camera()
        >>> while True:
        >>>    cam.getImage().edges().show()
        

        **SEE ALSO**

        :py:meth:`findLines`

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
        **SUMMARY***

        This function rotates an image around a specific point by the given angle 
        By default in "fixed" mode, the returned Image is the same dimensions as the original Image, and the contents will be scaled to fit.  In "full" mode the
        contents retain the original size, and the Image object will scale
        by default, the point is the center of the image. 
        you can also specify a scaling parameter

        .. Note:
          that when fixed is set to false selecting a rotation point has no effect since the image is move to fit on the screen.

        **PARAMETERS**

        * *angle* - angle in degrees positive is clockwise, negative is counter clockwise 
        * *fixed* - if fixed is true,keep the original image dimensions, otherwise scale the image to fit the rotation 
        * *point* - the point about which we want to rotate, if none is defined we use the center.
        * *scale* - and optional floating point scale parameter. 
            
        **RETURNS**
        
        The rotated SimpleCV image. 

        **EXAMPLE**
        
        >>> img = Image('logo')
        >>> img2 = rotate( 73.00, point=(img.width/2,img.height/2))
        >>> img3 = rotate( 73.00, fixex=False, point=(img.width/2,img.height/2))
        >>> img4 = img2.sideBySide(img3)
        >>> img4.show()

        **SEE ALSO**

        :py:meth:`rotate90`

        """
        if( point[0] == -1 or point[1] == -1 ):
            point[0] = (self.width-1)/2
            point[1] = (self.height-1)/2


        if (fixed):
            retVal = self.getEmpty()
            cv.Zero(retVal)
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
        cv.Zero(retVal)

        cv.WarpAffine(self.getBitmap(), retVal, rotMat)
        #cv.AddS(retVal,(0,255,0),retVal)
        return Image(retVal, colorSpace=self._colorSpace) 


    def rotate90(self):
        """
        **SUMMARY**
        
        Does a fast 90 degree rotation to the right. Generally this method should be faster than img.rotate(90)

        .. Warning::
          Subsequent calls to this function *WILL NOT* keep rotating it to the right!!!
          This function just does a matrix transpose so following one transpose by another will 
          just yield the original image.  

        **RETURNS**
         
        The rotated SimpleCV Image.
        
        **EXAMPLE**
        
        >>> img = Image("logo")
        >>> img2 = img.rotate90()
        >>> img2.show()

        **SEE ALSO**
        
        :py:meth:`rotate`
         

        """
        retVal = cv.CreateImage((self.height, self.width), cv.IPL_DEPTH_8U, 3)
        cv.Transpose(self.getBitmap(), retVal)
        return(Image(retVal, colorSpace=self._colorSpace))
    
    
    def shear(self, cornerpoints):
        """
        **SUMMARY**

        Given a set of new corner points in clockwise order, return a shear-ed image
        that transforms the image contents.  The returned image is the same
        dimensions. 

        **PARAMETERS**

        * *cornerpoints* - a 2x4 tuple of points. The order is (top_left, top_right, bottom_left, bottom_right)

        **RETURNS**
        
        A simpleCV image. 

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> points = ((50,0),(img.width+50,0),(img.width,img.height),(0,img.height))
        >>> img.shear(points).show()

        **SEE ALSO**

        :py:meth:`transformAffine`
        :py:meth:`warp`
        :py:meth:`rotate`

        http://en.wikipedia.org/wiki/Transformation_matrix

        """
        src =  ((0, 0), (self.width-1, 0), (self.width-1, self.height-1))
        #set the original points
        aWarp = cv.CreateMat(2, 3, cv.CV_32FC1)
        #create the empty warp matrix
        cv.GetAffineTransform(src, cornerpoints, aWarp)


        return self.transformAffine(aWarp)


    def transformAffine(self, rotMatrix):
        """
        **SUMMARY**

        This helper function for shear performs an affine rotation using the supplied matrix. 
        The matrix can be a either an openCV mat or an np.ndarray type. 
        The matrix should be a 2x3

        **PARAMETERS**
        
        * *rotMatrix* - A 2x3 numpy array or CvMat of the affine transform. 
            
        **RETURNS**

        The rotated image. Note that the rotation is done in place, i.e. the image is not enlarged to fit the transofmation.
        
        **EXAMPLE**

        >>> img = Image("lenna")
        >>> points = ((50,0),(img.width+50,0),(img.width,img.height),(0,img.height))
        >>> src =  ((0, 0), (img.width-1, 0), (img.width-1, img.height-1))
        >>> result = cv.createMat(2,3,cv.CV_32FC1)
        >>> cv.GetAffineTransform(src,points,result)
        >>> img.transformAffine(result).show()


        **SEE ALSO**
 
        :py:meth:`shear`
        :py:meth`warp`
        :py:meth:`transformPerspective`
        :py:meth:`rotate`

        http://en.wikipedia.org/wiki/Transformation_matrix
        
        """
        retVal = self.getEmpty()
        if(type(rotMatrix) == np.ndarray ):
            rotMatrix = npArray2cvMat(rotMatrix)
        cv.WarpAffine(self.getBitmap(), retVal, rotMatrix)
        return Image(retVal, colorSpace=self._colorSpace) 


    def warp(self, cornerpoints):
        """
        **SUMMARY**
        
        This method performs and arbitrary perspective transform. 
        Given a new set of corner points in clockwise order frin top left, return an Image with 
        the images contents warped to the new coordinates.  The returned image
        will be the same size as the original image


        **PARAMETERS**
        
        * *cornerpoints* - A list of four tuples corresponding to the destination corners in the order of (top_left,top_right,bottom_left,bottom_right) 

        **RETURNS**

        A simpleCV Image with the warp applied. Note that this operation does not enlarge the image. 

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> points = ((30, 30), (img.width-10, 70), (img.width-1-40, img.height-1+30),(20,img.height+10))
        >>> img.warp(points).show()
        
        **SEE ALSO**

        :py:meth:`shear`
        :py:meth:`transformAffine`
        :py:meth:`transformPerspective`
        :py:meth:`rotate`

        http://en.wikipedia.org/wiki/Transformation_matrix
        
        """
        #original coordinates
        src = ((0, 0), (self.width-1, 0), (self.width-1, self.height-1), (0, self.height-1))    
        pWarp = cv.CreateMat(3, 3, cv.CV_32FC1) #create an empty 3x3 matrix
        cv.GetPerspectiveTransform(src, cornerpoints, pWarp) #figure out the warp matrix


        return self.transformPerspective(pWarp)


    def transformPerspective(self, rotMatrix):
        """
        **SUMMARY**
       
        This helper function for warp performs an affine rotation using the supplied matrix. 
        The matrix can be a either an openCV mat or an np.ndarray type. 
        The matrix should be a 3x3

       **PARAMETERS**
            * *rotMatrix* - Numpy Array or CvMat

        **RETURNS**

        The rotated image. Note that the rotation is done in place, i.e. the image is not enlarged to fit the transofmation.
        
        **EXAMPLE**

        >>> img = Image("lenna")
        >>> points = ((50,0),(img.width+50,0),(img.width,img.height),(0,img.height))
        >>> src = ((30, 30), (img.width-10, 70), (img.width-1-40, img.height-1+30),(20,img.height+10))
        >>> result = cv.createMat(3,3,cv.CV_32FC1)
        >>> cv.GetPerspectiveTransform(src,points,result)
        >>> img.transformPerspective(result).show()


        **SEE ALSO**
 
        :py:meth:`shear`
        :py:meth:`warp`
        :py:meth:`transformPerspective`
        :py:meth:`rotate`

        http://en.wikipedia.org/wiki/Transformation_matrix
        
        """
        retVal = self.getEmpty()
        if(type(rotMatrix) == np.ndarray ):
            rotMatrix = npArray2cvMat(rotMatrix)
        cv.WarpPerspective(self.getBitmap(), retVal, rotMatrix)
        return Image(retVal, colorSpace=self._colorSpace) 
  
  
    def getPixel(self, x, y):
        """
        **SUMMARY**

        This function returns the RGB value for a particular image pixel given a specific row and column.
        
        .. Warning::
          this function will always return pixels in RGB format even if the image is BGR format. 
        
        **PARAMETERS**
        
            * *x* - Int the x pixel coordinate.
            * *y* - Int the y pixel coordinate.

        **RETURNS**

        A color value that is a three element integer tuple.

        **EXAMPLE**
        
        >>> img = Image(logo)
        >>> color = img.getPixel(10,10)


        .. Warning::
          We suggest that this method be used sparingly. For repeated pixel access use python array notation. I.e. img[x][y].

        """
        c = None
        retVal = None
        if( x < 0 or x >= self.width ):
            logger.warning("getRGBPixel: X value is not valid.")
        elif( y < 0 or y >= self.height ):
            logger.warning("getRGBPixel: Y value is not valid.")
        else:
            c = cv.Get2D(self.getBitmap(), y, x)
            if( self._colorSpace == ColorSpace.BGR ): 
                retVal = (c[2],c[1],c[0])
            else:
                retVal = (c[0],c[1],c[2])
        
        return retVal
  
  
    def getGrayPixel(self, x, y):
        """
        **SUMMARY**

        This function returns the gray value for a particular image pixel given a specific row and column.
        
        
        .. Warning::
          This function will always return pixels in RGB format even if the image is BGR format. 
        
        **PARAMETERS**
        
        * *x* - Int the x pixel coordinate.
        * *y* - Int the y pixel coordinate.

        **RETURNS**

        A gray value integer between 0 and 255.

        **EXAMPLE**
        
        >>> img = Image(logo)
        >>> color = img.getGrayPixel(10,10)


        .. Warning::
          We suggest that this method be used sparingly. For repeated pixel access use python array notation. I.e. img[x][y].

        """
        retVal = None
        if( x < 0 or x >= self.width ):
            logger.warning("getGrayPixel: X value is not valid.") 
        elif( y < 0 or y >= self.height ):
            logger.warning("getGrayPixel: Y value is not valid.")
        else:
            retVal = cv.Get2D(self._getGrayscaleBitmap(), y, x)
            retVal = retVal[0]
        return retVal
      
      
    def getVertScanline(self, column):
        """
        **SUMMARY**
        
        This function returns a single column of RGB values from the image as a numpy array. This is handy if you 
        want to crawl the image looking for an edge. 

        **PARAMETERS**
        
        * *column* - the column number working from left=0 to right=img.width.

        **RETURNS**

        A numpy array of the pixel values. Ususally this is in BGR format. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> myColor = [0,0,0]
        >>> sl = img.getVertScanline(423)
        >>> sll = sl.tolist()
        >>> for p in sll:
        >>>    if( p == myColor ):
        >>>        # do something

        **SEE ALSO**

        :py:meth:`getHorzScanlineGray`
        :py:meth:`getHorzScanline`
        :py:meth:`getVertScanlineGray`
        :py:meth:`getVertScanline`

        """
        retVal = None
        if( column < 0 or column >= self.width ):
            logger.warning("getVertRGBScanline: column value is not valid.")
        else:
            retVal = cv.GetCol(self.getBitmap(), column)
            retVal = np.array(retVal)
            retVal = retVal[:, 0, :] 
        return retVal
  
  
    def getHorzScanline(self, row):
        """
        **SUMMARY**

        This function returns a single row of RGB values from the image.
        This is handy if you want to crawl the image looking for an edge. 

        **PARAMETERS**
        
        * *row* - the row number working from top=0 to bottom=img.height.

        **RETURNS**

        A a lumpy numpy array of the pixel values. Ususally this is in BGR format. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> myColor = [0,0,0]
        >>> sl = img.getHorzScanline(422)
        >>> sll = sl.tolist()
        >>> for p in sll:
        >>>    if( p == myColor ):
        >>>        # do something

        **SEE ALSO**

        :py:meth:`getHorzScanlineGray`
        :py:meth:`getVertScanlineGray`
        :py:meth:`getVertScanline`

        """
        retVal = None
        if( row < 0 or row >= self.height ):
            logger.warning("getHorzRGBScanline: row value is not valid.")
        else:
            retVal = cv.GetRow(self.getBitmap(), row)
            retVal = np.array(retVal)
            retVal = retVal[0, :, :]
        return retVal
  
  
    def getVertScanlineGray(self, column):
        """
        **SUMMARY**
        
        This function returns a single column of gray values from the image as a numpy array. This is handy if you 
        want to crawl the image looking for an edge. 

        **PARAMETERS**
        
        * *column* - the column number working from left=0 to right=img.width.

        **RETURNS**

        A a lumpy numpy array of the pixel values.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> myColor = [255]
        >>> sl = img.getVertScanlineGray(421)
        >>> sll = sl.tolist()
        >>> for p in sll:
        >>>    if( p == myColor ):
        >>>        # do something

        **SEE ALSO**

        :py:meth:`getHorzScanlineGray`
        :py:meth:`getHorzScanline`
        :py:meth:`getVertScanline`

        """
        retVal = None
        if( column < 0 or column >= self.width ):
            logger.warning("getHorzRGBScanline: row value is not valid.")
        else:
            retVal = cv.GetCol(self._getGrayscaleBitmap(), column )
            retVal = np.array(retVal)
            #retVal = retVal.transpose()
        return retVal
  
  
    def getHorzScanlineGray(self, row):
        """
        **SUMMARY**
        
        This function returns a single row of gray values from the image as a numpy array. This is handy if you 
        want to crawl the image looking for an edge. 

        **PARAMETERS**

        * *row* - the row number working from top=0 to bottom=img.height. 

        **RETURNS**

        A a lumpy numpy array of the pixel values. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> myColor = [255]
        >>> sl = img.getHorzScanlineGray(420)
        >>> sll = sl.tolist()
        >>> for p in sll:
        >>>    if( p == myColor ):
        >>>        # do something

        **SEE ALSO**

        :py:meth:`getHorzScanlineGray`
        :py:meth:`getHorzScanline`
        :py:meth:`getVertScanlineGray`
        :py:meth:`getVertScanline`

        """
        retVal = None
        if( row < 0 or row >= self.height ):
            logger.warning("getHorzRGBScanline: row value is not valid.")
        else:
            retVal = cv.GetRow(self._getGrayscaleBitmap(), row )
            retVal = np.array(retVal)
            retVal = retVal.transpose()
        return retVal


    def crop(self, x , y = None, w = None, h = None, centered=False):
        """
        **SUMMARY**
        Consider you want to crop a image with the following dimension :

        (x,y) 
            +--------------+
            |              |
            |              |h
            |              |
            +--------------+
                  w      (x1,y1)   

        Crop attempts to use the x and y position variables and the w and h width
        and height variables to crop the image. When centered is false, x and y
        define the top and left of the cropped rectangle. When centered is true
        the function uses x and y as the centroid of the cropped region.

        You can also pass a feature into crop and have it automatically return
        the cropped image within the bounding outside area of that feature
        
        Or parameters can be in the form of a
         - tuple or list : (x,y,w,h) or [x,y,w,h]
         - two points : (x,y),(x1,y1) or [(x,y),(x1,y1)]
           
        **PARAMETERS**

        * *x* - An integer or feature. 
              - If it is a feature we crop to the features dimensions. 
              - This can be either the top left corner of the image or the center cooridnate of the the crop region.
              - or in the form of tuple/list. i,e (x,y,w,h) or [x,y,w,h]
              - Otherwise in two point form. i,e [(x,y),(x1,y1)] or (x,y)
        * *y* - The y coordinate of the center, or top left corner  of the crop region.
              - Otherwise in two point form. i,e (x1,y1)
        * *w* - Int - the width of the cropped region in pixels.
        * *h* - Int - the height of the cropped region in pixels.
        * *centered*  - Boolean - if True we treat the crop region as being the center 
          coordinate and a width and height. If false we treat it as the top left corner of the crop region.

        **RETURNS**

        A SimpleCV Image cropped to the specified width and height.

        **EXAMPLE**
        
        >>> img = Image('lenna')
        >>> img.crop(50,40,128,128).show()
        >>> img.crop((50,40,128,128)).show() #roi
        >>> img.crop([50,40,128,128]) #roi
        >>> img.crop((50,40),(178,168)) # two point form
        >>> img.crop([(50,40),(178,168)]) # two point form
        **SEE ALSO**
        
        :py:meth:`embiggen`
        :py:meth:`regionSelect`
        """

        #If it's a feature extract what we need
        if(isinstance(x, Feature)):
            theFeature = x
            x = theFeature.points[0][0]
            y = theFeature.points[0][1]
            w = theFeature.width()
            h = theFeature.height()
        
        # x of the form [(x,y),(x1,y1)]        
        elif(isinstance(x, list) and isinstance(x[0],tuple) and isinstance(x[1],tuple) and y == None and w == None and h == None):
            if (len(x[0])==2 and len(x[1])==2):    
                x,y,w,h = x[0][0],x[0][1],x[1][0]-x[0][0],x[1][1]-x[0][1]
            else:
                logger.warning("x should be in the form [(x1,y1),(x2,y2)]") 
                return None
                 
        # x and y of the form (x,y),(x1,y2)     
        elif(isinstance(x, tuple) and isinstance(y, tuple) and w == None and h == None):
            if (len(x)==2 and len(y)==2):
                x,y,w,h = x[0],x[1],y[0]-x[0],y[1]-x[1]
            else:
                logger.warning("if x and y are tuple it should be in the form (x1,y1) and (x2,y2)") 
                return None        

        # x of the form (x,y,x1,y2) or [x,y,x1,y2]        
        elif(isinstance(x, tuple) or isinstance(x, list) and y == None and w == None and h == None):
            if (len(x)==4):
                x,y,w,h = x
            else:
                logger.warning("if x is a tuple or list it should be in the form (x,y,w,h) or [x,y,w,h]") 
                return None        
                    
                    
        if(y == None or w == None or h == None):
            print "Please provide an x, y, width, height to function"

        if( w <= 0 or h <= 0 ):
            logger.warning("Can't do a negative crop!")
            return None
        
        retVal = cv.CreateImage((int(w),int(h)), cv.IPL_DEPTH_8U, 3)
        if( x < 0 or y < 0 ):
            logger.warning("Crop will try to help you, but you have a negative crop position, your width and height may not be what you want them to be.")


        if( centered ):
            rectangle = (int(x-(w/2)), int(y-(h/2)), int(w), int(h))
        else:
            rectangle = (int(x), int(y), int(w), int(h))
    

        (topROI, bottomROI) = self._rectOverlapROIs((rectangle[2],rectangle[3]),(self.width,self.height),(rectangle[0],rectangle[1]))

        if( bottomROI is None ):
            logger.warning("Hi, your crop rectangle doesn't even overlap your image. I have no choice but to return None.")
            return None

        retVal = cv.CreateImage((bottomROI[2],bottomROI[3]), cv.IPL_DEPTH_8U, 3)
    
        cv.SetImageROI(self.getBitmap(), bottomROI)
        cv.Copy(self.getBitmap(), retVal)
        cv.ResetImageROI(self.getBitmap())
        return Image(retVal, colorSpace=self._colorSpace)
            
    def regionSelect(self, x1, y1, x2, y2 ):
        """
        **SUMMARY**

        Region select is similar to crop, but instead of taking a position and width
        and height values it simply takes to points on the image and returns the selected
        region. This is very helpful for creating interactive scripts that require
        the user to select a region.

        **PARAMETERS**

        * *x1* - Int - Point one x coordinate.
        * *y1* - Int  - Point one y coordinate.
        * *x2* - Int  - Point two x coordinate.
        * *y2* - Int  - Point two y coordinate.

        **RETURNS**

        A cropped SimpleCV Image.
        
        **EXAMPLE**

        >>> img = Image("lenna")
        >>> subreg = img.regionSelect(10,10,100,100) # often this comes from a mouse click
        >>> subreg.show()

        **SEE ALSO**
        
        :py:meth:`crop`

        """
        w = abs(x1-x2)
        h = abs(y1-y2)


        retVal = None
        if( w <= 0 or h <= 0 or w > self.width or h > self.height ):
            logger.warning("regionSelect: the given values will not fit in the image or are too small.")
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
        **SUMMARY**

        This is a slightly unsafe method that clears out the entire image state
        it is usually used in conjunction with the drawing blobs to fill in draw
        a single large blob in the image. 
        
        .. Warning: 
          Do not use this method unless you have a particularly compelling reason.
        
        """
        cv.SetZero(self._bitmap)
        self._clearBuffers()
    
    


    
    
    def drawText(self, text = "", x = None, y = None, color = Color.BLUE, fontsize = 16):
        """
        **SUMMARY**

        This function draws the string that is passed on the screen at the specified coordinates.

        The Default Color is blue but you can pass it various colors

        The text will default to the center of the screen if you don't pass it a value


        **PARAMETERS**

        * *text* - String - the text you want to write. ASCII only please.
        * *x* - Int - the x position in pixels.
        * *y* - Int - the y position in pixels. 
        * *color* - Color object or Color Tuple
        * *fontsize* - Int - the font size - roughly in points. 

        **RETURNS**
        
        Nothing. This is an in place function. Text is added to the Images drawing layer. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> img.writeText("xamox smells like cool ranch doritos.", 50,50,color=Color.BLACK,fontSize=48)
        >>> img.show()

        **SEE ALSO**

        :py:meth:`dl`
        :py:meth:`drawCircle`
        :py:meth:`drawRectangle`
 
        """
        if(x == None):
            x = (self.width / 2)
        if(y == None):
            y = (self.height / 2)
    
    
        self.getDrawingLayer().setFontSize(fontsize)
        self.getDrawingLayer().text(text, (x, y), color)
    
    
    def drawRectangle(self,x,y,w,h,color=Color.RED,width=1,alpha=255):
        """
        **SUMMARY**

        Draw a rectangle on the screen given the upper left corner of the rectangle
        and the width and height. 
        
        **PARAMETERS**

        * *x* - the x position.
        * *y* - the y position.
        * *w* - the width of the rectangle.
        * *h* - the height of the rectangle.
        * *color* - an RGB tuple indicating the desired color.
        * *width* - the width of the rectangle, a value less than or equal to zero means filled in completely.
        * *alpha* - the alpha value on the interval from 255 to 0, 255 is opaque, 0 is completely transparent. 

        **RETURNS**

        None - this operation is in place and adds the rectangle to the drawing layer. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> img.drawREctange( 50,50,100,123)
        >>> img.show()

        **SEE ALSO**

        :py:meth:`dl`
        :py:meth:`drawCircle`
        :py:meth:`drawRectangle`
        :py:meth:`applyLayers`
        :py:class:`DrawingLayer`

        """
        if( width < 1 ):
            self.getDrawingLayer().rectangle((x,y),(w,h),color,filled=True,alpha=alpha)
        else:
            self.getDrawingLayer().rectangle((x,y),(w,h),color,width,alpha=alpha)
            
    def drawRotatedRectangle(self,boundingbox,color=Color.RED,width=1):
        """
        **SUMMARY**

        Draw the minimum bouding rectangle. This rectangle is a series of four points.

        **TODO**

        **KAT FIX THIS**
        """

        cv.EllipseBox(self.getBitmap(),box=boundingbox,color=color,thicness=width)


    def show(self, type = 'window'):
        """
        **SUMMARY**

        This function automatically pops up a window and shows the current image.

        **PARAMETERS**

        * *type* - this string can have one of two values, either 'window', or 'browser'. Window opens 
          a display window, while browser opens the default web browser to show an image. 

        **RETURNS**

        This method returns the display object. In the case of the window this is a JpegStreamer
        object. In the case of a window a display object is returned. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> img.show()
        >>> img.show('browser')

        **SEE ALSO**

        :py:class:`JpegStreamer`
        :py:class:`Display`

        """

        if(type == 'browser'):
          import webbrowser
          js = JpegStreamer(8080)
          self.save(js)
          webbrowser.open("http://localhost:8080", 2)
          return js
        elif (type == 'window'):
          from SimpleCV.Display import Display
          if init_options_handler.on_notebook:
              d = Display(displaytype='notebook')
          else:
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
        **SUMMARY**

        Converts this image to a pygame surface. This is useful if you want
        to treat an image as a sprite to render onto an image. An example
        would be rendering blobs on to an image. 

        .. Warning:: 
          *THIS IS EXPERIMENTAL*. We are plannng to remove this functionality sometime in the near future.

        **RETURNS**

        The image as a pygame surface. 

        **SEE ALSO**


        :py:class:`DrawingLayer`
        :py:meth:`insertDrawingLayer`
        :py:meth:`addDrawingLayer`
        :py:meth:`dl`
        :py:meth:`toPygameSurface`
        :py:meth:`getDrawingLayer`
        :py:meth:`removeDrawingLayer`
        :py:meth:`clearLayers`
        :py:meth:`layers`
        :py:meth:`mergedLayers`
        :py:meth:`applyLayers`
        :py:meth:`drawText`
        :py:meth:`drawRectangle`
        :py:meth:`drawCircle`
        :py:meth:`blit`
          
        """
        return pg.image.fromstring(self.getPIL().tostring(),self.size(), "RGB") 
    
        
    def addDrawingLayer(self, layer = None):
        """
        **SUMMARY**

        Push a new drawing layer onto the back of the layer stack

        **PARAMETERS**
        
        * *layer* - The new drawing layer to add. 

        **RETURNS**
        
        The index of the new layer as an integer.
        
        **EXAMPLE**
        
        >>> img = Image("Lenna")
        >>> myLayer = DrawingLayer((img.width,img.height))
        >>> img.addDrawingLayer(myLayer)

        **SEE ALSO**

        :py:class:`DrawingLayer`
        :py:meth:`insertDrawinglayer`
        :py:meth:`addDrawinglayer`
        :py:meth:`dl`
        :py:meth:`toPygameSurface`
        :py:meth:`getDrawingLayer`
        :py:meth:`removeDrawingLayer`
        :py:meth:`clearLayers`
        :py:meth:`layers`
        :py:meth:`mergedLayers`
        :py:meth:`applyLayers`
        :py:meth:`drawText`
        :py:meth:`drawRectangle`
        :py:meth:`drawCircle`
        :py:meth:`blit`

        """

        if not isinstance(layer, DrawingLayer):
          return "Please pass a DrawingLayer object"
        
        if not layer:
            layer = DrawingLayer(self.size())
        self._mLayers.append(layer)
        return len(self._mLayers)-1
    
    
    def insertDrawingLayer(self, layer, index):
        """
        **SUMMARY**
        
        Insert a new layer into the layer stack at the specified index.

        **PARAMETERS**

        * *layer* - A drawing layer with crap you want to draw.
        * *index* - The index at which to insert the layer. 

        **RETURNS** 
        
        None - that's right - nothing.

        **EXAMPLE**
        
        >>> img = Image("Lenna")
        >>> myLayer1 = DrawingLayer((img.width,img.height))
        >>> myLayer2 = DrawingLayer((img.width,img.height))
        >>> #Draw on the layers
        >>> img.insertDrawingLayer(myLayer1,1) # on top
        >>> img.insertDrawingLayer(myLayer2,2) # on the bottom
        

        **SEE ALSO**

        :py:class:`DrawingLayer`
        :py:meth:`addDrawinglayer`
        :py:meth:`dl`
        :py:meth:`toPygameSurface`
        :py:meth:`getDrawingLayer`
        :py:meth:`removeDrawingLayer`
        :py:meth:`clearLayers`
        :py:meth:`layers`
        :py:meth:`mergedLayers`
        :py:meth:`applyLayers`
        :py:meth:`drawText`
        :py:meth:`drawRectangle`
        :py:meth:`drawCircle`
        :py:meth:`blit`

        """
        self._mLayers.insert(index, layer)
        return None    
  
  
    def removeDrawingLayer(self, index):
        """
        **SUMMARY**

        Remove a layer from the layer stack based on the layer's index.

        **PARAMETERS**
        
        * *index* - Int - the index of the layer to remove. 

        **RETURNS**
        
        This method returns the removed drawing layer.

        **SUMMARY**
        
        Insert a new layer into the layer stack at the specified index.

        **PARAMETERS**

        * *layer* - A drawing layer with crap you want to draw.
        * *index* - The index at which to insert the layer. 

        **RETURNS** 
        
        None - that's right - nothing.

        **EXAMPLE**
        
        >>> img = Image("Lenna")
        >>> myLayer1 = DrawingLayer((img.width,img.height))
        >>> myLayer2 = DrawingLayer((img.width,img.height))
        >>> #Draw on the layers
        >>> img.insertDrawingLayer(myLayer1,1) # on top
        >>> img.insertDrawingLayer(myLayer2,2) # on the bottom
        

        **SEE ALSO**

        :py:class:`DrawingLayer`
        :py:meth:`addDrawinglayer`
        :py:meth:`dl`
        :py:meth:`toPygameSurface`
        :py:meth:`getDrawingLayer`
        :py:meth:`removeDrawingLayer`
        :py:meth:`clearLayers`
        :py:meth:`layers`
        :py:meth:`mergedLayers`
        :py:meth:`applyLayers`
        :py:meth:`drawText`
        :py:meth:`drawRectangle`
        :py:meth:`drawCircle`
        :py:meth:`blit`

        """
        return self._mLayers.pop(index)
    
    
    def getDrawingLayer(self, index = -1):
        """
        **SUMMARY**

        Return a drawing layer based on the provided index.  If not provided, will
        default to the top layer.  If no layers exist, one will be created

        **PARAMETERS**
        
        * *index* - returns the drawing layer at the specified index. 
       
        **RETURNS**
        
        A drawing layer.

        **EXAMPLE**
       
        >>> img = Image("Lenna")
        >>> myLayer1 = DrawingLayer((img.width,img.height))
        >>> myLayer2 = DrawingLayer((img.width,img.height))
        >>> #Draw on the layers
        >>> img.insertDrawingLayer(myLayer1,1) # on top
        >>> img.insertDrawingLayer(myLayer2,2) # on the bottom
        >>> layer2 =img.getDrawingLayer(2) 

        **SEE ALSO**

        :py:class:`DrawingLayer`
        :py:meth:`addDrawinglayer`
        :py:meth:`dl`
        :py:meth:`toPygameSurface`
        :py:meth:`getDrawingLayer`
        :py:meth:`removeDrawingLayer`
        :py:meth:`clearLayers`
        :py:meth:`layers`
        :py:meth:`mergedLayers`
        :py:meth:`applyLayers`
        :py:meth:`drawText`
        :py:meth:`drawRectangle`
        :py:meth:`drawCircle`
        :py:meth:`blit`
 
        """
        if not len(self._mLayers):
            layer = DrawingLayer(self.size())
            self.addDrawingLayer(layer)
      
      
        return self._mLayers[index]
    
    
    def dl(self, index = -1):
        """
        **SUMMARY**

        Alias for :py:meth:`getDrawingLayer`

        """
        return self.getDrawingLayer(index)
  
  
    def clearLayers(self):
        """
        **SUMMARY**

        Remove all of the drawing layers. 

        **RETURNS**

        None.

        **EXAMPLE**
       
        >>> img = Image("Lenna")
        >>> myLayer1 = DrawingLayer((img.width,img.height))
        >>> myLayer2 = DrawingLayer((img.width,img.height))
        >>> img.insertDrawingLayer(myLayer1,1) # on top
        >>> img.insertDrawingLayer(myLayer2,2) # on the bottom
        >>> img.clearLayers()

        **SEE ALSO**

        :py:class:`DrawingLayer`
        :py:meth:`dl`
        :py:meth:`toPygameSurface`
        :py:meth:`getDrawingLayer`
        :py:meth:`removeDrawingLayer`
        :py:meth:`layers`
        :py:meth:`mergedLayers`
        :py:meth:`applyLayers`
        :py:meth:`drawText`
        :py:meth:`drawRectangle`
        :py:meth:`drawCircle`
        :py:meth:`blit`
         
        """
        for i in self._mLayers:
            self._mLayers.remove(i)
      
      
        return None

    def layers(self):
        """
        **SUMMARY**

        Return the array of DrawingLayer objects associated with the image.

        **RETURNS**
        
        A list of of drawing layers. 

        **SEE ALSO**

        :py:class:`DrawingLayer`
        :py:meth:`addDrawingLayer`
        :py:meth:`dl`
        :py:meth:`toPygameSurface`
        :py:meth:`getDrawingLayer`
        :py:meth:`removeDrawingLayer`
        :py:meth:`mergedLayers`
        :py:meth:`applyLayers`
        :py:meth:`drawText`
        :py:meth:`drawRectangle`
        :py:meth:`drawCircle`
        :py:meth:`blit`

        """
        return self._mLayers


        #render the image. 

    def _renderImage(self, layer):
        imgSurf = self.getPGSurface(self).copy()
        imgSurf.blit(layer._mSurface, (0, 0))
        return Image(imgSurf)
    
    def mergedLayers(self):
        """
        **SUMMARY**

        Return all DrawingLayer objects as a single DrawingLayer.
        
        **RETURNS**
        
        Returns a drawing layer with all of the drawing layers of this image merged into one.

        **EXAMPLE**
       
        >>> img = Image("Lenna")
        >>> myLayer1 = DrawingLayer((img.width,img.height))
        >>> myLayer2 = DrawingLayer((img.width,img.height))
        >>> img.insertDrawingLayer(myLayer1,1) # on top
        >>> img.insertDrawingLayer(myLayer2,2) # on the bottom
        >>> derp = img.mergedLayers()

        **SEE ALSO**

        :py:class:`DrawingLayer`
        :py:meth:`addDrawingLayer`
        :py:meth:`dl`
        :py:meth:`toPygameSurface`
        :py:meth:`getDrawingLayer`
        :py:meth:`removeDrawingLayer`
        :py:meth:`layers`
        :py:meth:`applyLayers`
        :py:meth:`drawText`
        :py:meth:`drawRectangle`
        :py:meth:`drawCircle`
        :py:meth:`blit`

        """
        final = DrawingLayer(self.size())
        for layers in self._mLayers: #compose all the layers
                layers.renderToOtherLayer(final)
        return final
        
    def applyLayers(self, indicies=-1):
        """
        **SUMMARY**
       
        Render all of the layers onto the current image and return the result.
        Indicies can be a list of integers specifying the layers to be used.

        **PARAMETERS**

        * *indicies* -  Indicies can be a list of integers specifying the layers to be used.

        **RETURNS**

        The image after applying the drawing layers. 

        **EXAMPLE**
       
        >>> img = Image("Lenna")
        >>> myLayer1 = DrawingLayer((img.width,img.height))
        >>> myLayer2 = DrawingLayer((img.width,img.height))
        >>> #Draw some stuff
        >>> img.insertDrawingLayer(myLayer1,1) # on top
        >>> img.insertDrawingLayer(myLayer2,2) # on the bottom
        >>> derp = img.applyLayers()
        
        **SEE ALSO**

        :py:class:`DrawingLayer`
        :py:meth:`dl`
        :py:meth:`toPygameSurface`
        :py:meth:`getDrawingLayer`
        :py:meth:`removeDrawingLayer`
        :py:meth:`layers`
        :py:meth:`drawText`
        :py:meth:`drawRectangle`
        :py:meth:`drawCircle`
        :py:meth:`blit`

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
        **SUMMARY**

        Adapative Scale is used in the Display to automatically
        adjust image size to match the display size. This method attempts to scale
        an image to the desired resolution while keeping the aspect ratio the same. 
        If fit is False we simply crop and center the image to the resolution.
        In general this method should look a lot better than arbitrary cropping and scaling. 
        
        **PARAMETERS**

        * *resolution* - The size of the returned image as a (width,height) tuple.
        * *fit* - If fit is true we try to fit the image while maintaining the aspect ratio.
          If fit is False we crop and center the image to fit the resolution. 

        **RETURNS**
        
        A SimpleCV Image. 
        
        **EXAMPLE**

        This is typically used in this instance:

        >>> d = Display((800,600))
        >>> i = Image((640, 480))
        >>> i.save(d)

        Where this would scale the image to match the display size of 800x600

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
            elif( self.width <= resolution[0] and self.height > resolution[1]): #height too big
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
        **SUMMARY**

        Blit aka bit blit - which in ye olden days was an acronym for bit-block transfer. In other words blit is
        when you want to smash two images together, or add one image to another. This method takes in a second 
        SimpleCV image, and then allows you to add to some point on the calling image. A general blit command
        will just copy all of the image. You can also copy the image with an alpha value to the source image
        is semi-transparent. A binary mask can be used to blit non-rectangular image onto the souce image.
        An alpha mask can be used to do and arbitrarily transparent image to this image. Both the mask and 
        alpha masks are SimpleCV Images. 

        **PARAMETERS**

        * *img* - an image to place ontop of this image.
        * *pos* - an (x,y) position tuple of the top left corner of img on this image. Note that these values 
          can be negative. 
        * *alpha* - a single floating point alpha value (0=see the bottom image, 1=see just img, 0.5 blend the two 50/50).
        * *mask* - a binary mask the same size as the input image. White areas are blitted, black areas are not blitted.
        * *alphaMask* - an alpha mask where each grayscale value maps how much of each image is shown.
        
        **RETURNS**
        
        A SimpleCV Image. The size will remain the same. 

        **EXAMPLE**
        
        >>> topImg = Image("top.png")
        >>> bottomImg = Image("bottom.png")
        >>> mask = Image("mask.png")
        >>> aMask = Image("alpphaMask.png")
        >>> bottomImg.blit(top,pos=(100,100)).show()
        >>> bottomImg.blit(top,alpha=0.5).show()
        >>> bottomImg.blit(top,pos=(100,100),mask=mask).show()
        >>> bottomImg.blit(top,pos=(-10,-10)alphaMask=aMask).show()
        
        **SEE ALSO**

        :py:meth:`createBinaryMask`
        :py:meth:`createAlphaMask`

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
                logger.warning("Image.blit: your mask and image don't match sizes, if the mask doesn't fit, you can not blit! Try using the scale function.")
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
                logger.warning("Image.blit: your mask and image don't match sizes, if the mask doesn't fit, you can not blit! Try using the scale function. ")
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
        **SUMMARY**

        Combine two images as a side by side images. Great for before and after images.

        **PARAMETERS**

        * *side* - what side of this image to place the other image on.
          choices are ('left'/'right'/'top'/'bottom'). 
               
        * *scale* - if true scale the smaller of the two sides to match the 
          edge touching the other image. If false we center the smaller
          of the two images on the edge touching the larger image. 

        **RETURNS**
        
        A new image that is a combination of the two images.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> img2 = Image("orson_welles.jpg")
        >>> img3 = img.sideBySide(img2)

        **TODO**

        Make this accept a list of images.

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
        **SUMMARY**

        Make the canvas larger but keep the image the same size. 

        **PARAMETERS**
        
        * *size* - width and heigt tuple of the new canvas. 

        * *color* - the color of the canvas 

        * *pos* - the position of the top left corner of image on the new canvas, 
          if none the image is centered.
          
        **RETURNS**
        
        The enlarged SimpleCV Image.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> img = img.embiggen((1024,1024),color=Color.BLUE)
        >>> img.show()

        """
        
        if( size == None or size[0] < self.width or size[1] < self.height ):
            logger.warning("image.embiggenCanvas: the size provided is invalid")
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
            logger.warning("image.embiggenCanvas: the position of the old image doesn't make sense, there is no overlap")
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
        **SUMMARY**

        Generate a binary mask of the image based on a range of rgb values.
        A binary mask is a black and white image where the white area is kept and the
        black area is removed. 

        This method is used by specifying two colors as the range between the minimum and maximum
        values that will be masked white.

        **PARAMETERS**

        * *color1* - The starting color range for the mask..
        * *color2* - The end of the color range for the mask. 

        **RETURNS**

        A binary (black/white) image mask as a SimpleCV Image.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> mask = img.createBinaryMask(color1=(0,128,128),color2=(255,255,255)
        >>> mask.show()

        **SEE ALSO**
        
        :py:meth:`createBinaryMask`
        :py:meth:`createAlphaMask`
        :py:meth:`blit`
        :py:meth:`threshold`

        """
        if( color1[0]-color2[0] == 0 or 
            color1[1]-color2[1] == 0 or
            color1[2]-color2[2] == 0 ):
            logger.warning("No color range selected, the result will be black, returning None instead.")
            return None
        if( color1[0] > 255 or color1[0] < 0 or
            color1[1] > 255 or color1[1] < 0 or
            color1[2] > 255 or color1[2] < 0 or
            color2[0] > 255 or color2[0] < 0 or
            color2[1] > 255 or color2[1] < 0 or
            color2[2] > 255 or color2[2] < 0 ):
            logger.warning("One of the tuple values falls outside of the range of 0 to 255")
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
        **SUMMARY**

        Apply a binary mask to the image. The white areas of the mask will be kept,
        and the black areas removed. The removed areas will be set to the color of 
        bg_color. 

        **PARAMETERS**

        * *mask* - the binary mask image. White areas are kept, black areas are removed.
        * *bg_color* - the color of the background on the mask.

        **RETURNS**
        
        A binary (black/white) image mask as a SimpleCV Image.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> mask = img.createBinaryMask(color1=(0,128,128),color2=(255,255,255)
        >>> result = img.applyBinaryMask(mask)
        >>> result.show()

        **SEE ALSO**
        
        :py:meth:`createBinaryMask`
        :py:meth:`createAlphaMask`
        :py:meth:`applyBinaryMask`
        :py:meth:`blit`
        :py:meth:`threshold`

        """
        newCanvas = cv.CreateImage((self.width,self.height), cv.IPL_DEPTH_8U, 3)
        cv.SetZero(newCanvas)
        newBG = cv.RGB(bg_color[0],bg_color[1],bg_color[2])
        cv.AddS(newCanvas,newBG,newCanvas)
        if( mask.width != self.width or mask.height != self.height ):
            logger.warning("Image.applyBinaryMask: your mask and image don't match sizes, if the mask doesn't fit, you can't apply it! Try using the scale function. ")
            return None
        cv.Copy(self.getBitmap(),newCanvas,mask.getBitmap());
        return Image(newCanvas,colorSpace=self._colorSpace);

    def createAlphaMask(self, hue=60, hue_lb=None,hue_ub=None):
        """
        **SUMMARY**

        Generate a grayscale or binary mask image based either on a hue or an RGB triplet that can be used
        like an alpha channel. In the resulting mask, the hue/rgb_color will be treated as transparent (black). 

        When a hue is used the mask is treated like an 8bit alpha channel.
        When an RGB triplet is used the result is a binary mask. 
        rgb_thresh is a distance measure between a given a pixel and the mask value that we will
        add to the mask. For example, if rgb_color=(0,255,0) and rgb_thresh=5 then any pixel 
        winthin five color values of the rgb_color will be added to the mask (e.g. (0,250,0),(5,255,0)....)

        Invert flips the mask values.


        **PARAMETERS**

        * *hue* - a hue used to generate the alpha mask.
        * *hue_lb* - the upper value  of a range of hue values to use.
        * *hue_ub* - the lower value  of a range of hue values to use.

        **RETURNS**

        A grayscale alpha mask as a SimpleCV Image. 

        >>> img = Image("lenna")
        >>> mask = img.createAlphaMask(hue_lb=50,hue_ub=70)
        >>> mask.show()

        **SEE ALSO**
        
        :py:meth:`createBinaryMask`
        :py:meth:`createAlphaMask`
        :py:meth:`applyBinaryMask`
        :py:meth:`blit`
        :py:meth:`threshold`

        """

        if( hue<0 or hue > 180 ):
            logger.warning("Invalid hue color, valid hue range is 0 to 180.")

        if( self._colorSpace != ColorSpace.HSV ):
            hsv = self.toHSV()
        else:
            hsv = self
        h = hsv.getEmpty(1)
        s = hsv.getEmpty(1)
        retVal = hsv.getEmpty(1)
        mask = hsv.getEmpty(1)
        cv.Split(hsv.getBitmap(),h,None,s,None)
        hlut = np.zeros((256,1),dtype=uint8) #thankfully we're not doing a LUT on saturation 
        if(hue_lb is not None and hue_ub is not None):
            hlut[hue_lb:hue_ub]=255
        else:
            hlut[hue] = 255
        cv.LUT(h,mask,cv.fromarray(hlut))
        cv.Copy(s,retVal,mask) #we'll save memory using hue
        return Image(retVal) 


    def applyPixelFunction(self, theFunc):
        """
        **SUMMARY**

        apply a function to every pixel and return the result
        The function must be of the form int (r,g,b)=func((r,g,b))

        **PARAMETERS** 
        
        * *theFunc* - a function pointer to a function of the form (r,g.b) = theFunc((r,g,b))
        
        **RETURNS**
        
        A simpleCV image after mapping the function to the image.

        **EXAMPLE**
        
        >>> def derp(pixels):
        >>>     return (int(b*.2),int(r*.3),int(g*.5))
        >>> 
        >>> img = Image("lenna")
        >>> img2 = img.applyPixelFunction(derp)

        """
        #there should be a way to do this faster using numpy vectorize
        #but I can get vectorize to work with the three channels together... have to split them
        #TODO: benchmark this against vectorize 
        pixels = np.array(self.getNumpy()).reshape(-1,3).tolist()
        result = np.array(map(theFunc,pixels),dtype=uint8).reshape(self.width,self.height,3) 
        return Image(result) 


    def integralImage(self,tilted=False):
        """
        **SUMMARY** 

        Calculate the integral image and return it as a numpy array.
        The integral image gives the sum of all of the pixels above and to the
        right of a given pixel location. It is useful for computing Haar cascades.
        The return type is a numpy array the same size of the image. The integral
        image requires 32Bit values which are not easily supported by the SimpleCV
        Image class.

        **PARAMETERS**
        
        * *tilted*  - if tilted is true we tilt the image 45 degrees and then calculate the results.

        **RETURNS**
        
        A numpy array of the values.

        **EXAMPLE**
        
        >>> img = Image("logo")
        >>> derp = img.integralImage()
        
        **SEE ALSO**
        
        http://en.wikipedia.org/wiki/Summed_area_table
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
        **SUMMARY**

        Convolution performs a shape change on an image.  It is similiar to
        something like a dilate.  You pass it a kernel in the form of a list, np.array, or cvMat

        **PARAMETERS**

        * *kernel* - The convolution kernel. As a cvArray, cvMat, or Numpy Array.
        * *center* - If true we use the center of the kernel.

        **RETURNS**

        The image after we apply the convolution.

        **EXAMPLE**
        
        >>> img = Image("sampleimages/simplecv.png")
        >>> kernel = [[1,0,0],[0,1,0],[0,0,1]]
        >>> conv = img.convolve()

        **SEE ALSO**
        
        http://en.wikipedia.org/wiki/Convolution

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
            logger.warning("Convolution uses numpy arrays or cv.mat type.")
            return None
        retVal = self.getEmpty(3)
        if(center is None):
            cv.Filter2D(self.getBitmap(),retVal,myKernel)
        else:
            cv.Filter2D(self.getBitmap(),retVal,myKernel,center)
        return Image(retVal)

    def findTemplate(self, template_image = None, threshold = 5, method = "SQR_DIFF_NORM"):
        """
        **SUMMARY**

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
        

        **PARAMETERS**

        * *template_image* - The template image. 
        * *threshold* - Int
        * *method* -

          * SQR_DIFF_NORM - Normalized square difference
          * SQR_DIFF      - Square difference
          * CCOEFF        -
          * CCOEFF_NORM   -
          * CCORR         - Cross correlation
          * CCORR_NORM    - Normalize cross correlation

        **EXAMPLE**
        
        >>> image = Image("/path/to/img.png")
        >>> pattern_image = image.crop(100,100,100,100)
        >>> found_patterns = image.findTemplate(pattern_image)
        >>> found_patterns.draw()
        >>> image.show()
        
        **RETURNS**

        This method returns a FeatureSet of TemplateMatch objects.
        
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
            logger.warning("ooops.. I don't know what template matching method you are looking for.")
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
            fs.append(TemplateMatch(self, template_image, (location[1],location[0]), matches[location[0], location[1]]))

        #cluster overlapping template matches 
        finalfs = FeatureSet()
        if( len(fs) > 0 ):
            finalfs.append(fs[0])
            for f in fs:
                match = False
                for f2 in finalfs:
                    if( f2._templateOverlaps(f) ): #if they overlap
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
        **SUMMARY**

        This function will return any text it can find using OCR on the
        image.

        Please note that it does not handle rotation well, so if you need
        it in your application try to rotate and/or crop the area so that
        the text would be the same way a document is read

        **RETURNS** 
        
        A String

        **EXAMPLE**
        
        >>> img = Imgae("somethingwithtext.png")
        >>> text = img.readText()
        >>> print text

        **NOTE**

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
        **SUMMARY**

        Perform the Hough Circle transform to extract _perfect_ circles from the image
        canny - the upper bound on a canny edge detector used to find circle edges.

        **PARAMETERS**
        
        * *thresh* - the threshold at which to count a circle. Small parts of a circle get
          added to the accumulator array used internally to the array. This value is the
          minimum threshold. Lower thresholds give more circles, higher thresholds give fewer circles.

        .. ::Warning: 
          If this threshold is too high, and no circles are found the underlying OpenCV
          routine fails and causes a segfault. 
        
        * *distance* - the minimum distance between each successive circle in pixels. 10 is a good
          starting value.

        **RETURNS**

        A feature set of Circle objects. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> circs = img.findCircles()
        >>> for c in circs:
        >>>    print c
        

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
        **SUMMARY**
        
        Attempts to perform automatic white balancing. 
        Gray World see: http://scien.stanford.edu/pages/labsite/2000/psych221/projects/00/trek/GWimages.html
        Robust AWB: http://scien.stanford.edu/pages/labsite/2010/psych221/projects/2010/JasonSu/robustawb.html
        http://scien.stanford.edu/pages/labsite/2010/psych221/projects/2010/JasonSu/Papers/Robust%20Automatic%20White%20Balance%20Algorithm%20using%20Gray%20Color%20Points%20in%20Images.pdf
        Simple AWB:
        http://www.ipol.im/pub/algo/lmps_simplest_color_balance/
        http://scien.stanford.edu/pages/labsite/2010/psych221/projects/2010/JasonSu/simplestcb.html



        **PARAMETERS**
        
        * *method* - The method to use for white balancing. Can be one of the following:

          * `Gray World <http://scien.stanford.edu/pages/labsite/2000/psych221/projects/00/trek/GWimages.html>`_

          * `Robust AWB <http://scien.stanford.edu/pages/labsite/2010/psych221/projects/2010/JasonSu/robustawb.html>`_

          * `Simple AWB <http://www.ipol.im/pub/algo/lmps_simplest_color_balance/>`_
         

        **RETURNS**
        
        A SimpleCV Image.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> img2 = img.whiteBalance()
                
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
        **SUMMARY**

        Apply LUT allows you to apply a LUT (look up table) to the pixels in a image. Each LUT is just 
        an array where each index in the array points to its value in the result image. For example 
        rLUT[0]=255 would change all pixels where the red channel is zero to the value 255.
        
        **PARAMETERS**

        * *rLUT* - a tuple or np.array of size (256x1) with dtype=uint8.
        * *gLUT* - a tuple or np.array of size (256x1) with dtype=uint8.
        * *bLUT* - a tuple or np.array of size (256x1) with dtype=uint8.

        .. warning::
          The dtype is very important. Will throw the following error without it:
          error: dst.size() == src.size() && dst.type() == CV_MAKETYPE(lut.depth(), src.channels())
        
        
        **RETURNS**

        The SimpleCV image remapped using the LUT.
        
        **EXAMPLE**

        This example saturates the red channel:
        
        >>> rlut = np.ones((256,1),dtype=uint8)*255
        >>> img=img.applyLUT(rLUT=rlut)
       

        NOTE:

        -==== BUG NOTE ====- 
        This method seems to error on the LUT map for some versions of OpenCV.
        I am trying to figure out why. -KAS
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
        .. _getRawKeypoints:
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
                 
                 All the flavour specified below are for OpenCV versions >= 2.4.0 :
                 
                 "MSER" - Maximally Stable Extremal Regions algorithm
                 
                 See: http://en.wikipedia.org/wiki/Maximally_stable_extremal_regions
                 
                 "Dense" - Dense Scale Invariant Feature Transform.
                 
                 See: http://www.vlfeat.org/api/dsift.html
                 
                 "ORB" - The Oriented FAST and Rotated BRIEF
                 
                 See: http://www.willowgarage.com/sites/default/files/orb_final.pdf
                 
                 "SIFT" - Scale-invariant feature transform
                 
                 See: http://en.wikipedia.org/wiki/Scale-invariant_feature_transform

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
        >>> img = Image("aerospace.jpg")
        >>> kp,d = img._getRawKeypoints() 

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
        try:
            import cv2
            ver = cv2.__version__
            new_version = 0
            #For OpenCV versions till 2.4.0,  cv2.__versions__ are of the form "$Rev: 4557 $" 
            if not ver.startswith('$Rev:'):
	        if int(ver.replace('.','0'))>=20400 :
                    new_version = 1
                if int(ver.replace('.','0'))>=20402 :     
                    new_version = 2
                    
        except:
            logger.warning("Can't run Keypoints without OpenCV >= 2.3.0")
            return
                    
        if( forceReset ):
            self._mKeyPoints = None
            self._mKPDescriptors = None
            
        if( self._mKeyPoints is None or self._mKPFlavor != flavor ):
            if ( new_version == 0):
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
            
                elif( flavor == "FAST" and not (int(ver.split(' ')[1])>=4557)) :
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
            
            
            elif( new_version == 2 and flavor in ["SURF", "FAST"] ): 
                if( flavor == "SURF" ):
                    surfer = cv2.SURF(hessianThreshold=thresh,extended=highQuality,upright=1)
                    #mask = self.getGrayNumpy()                    
                    #mask.fill(255) 
                    self._mKeyPoints,self._mKPDescriptors = surfer.detect(self.getGrayNumpy(),None,useProvidedKeypoints = False)
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
            
            elif( new_version >=1  and flavor in ["ORB", "SIFT", "SURF"] ):
               FeatureDetector = cv2.FeatureDetector_create(flavor)
               DescriptorExtractor = cv2.DescriptorExtractor_create(flavor)
               self._mKeyPoints = FeatureDetector.detect(self.getGrayNumpy())
               self._mKeyPoints,self._mKPDescriptors = DescriptorExtractor.compute(self.getGrayNumpy(),self._mKeyPoints)
               if( len(self._mKPDescriptors) == 0 ):
                    return None, None     
               self._mKPFlavor = flavor
	       del FeatureDetector

            elif( new_version >= 1 and flavor in ["FAST", "STAR", "MSER", "Dense"] ):
               FeatureDetector = cv2.FeatureDetector_create(flavor)
               self._mKeyPoints = FeatureDetector.detect(self.getGrayNumpy())
               self._mKPDescriptors = None
               self._mKPFlavor = flavor
               del FeatureDetector   
               
	    else:
                logger.warning("ImageClass.Keypoints: I don't know the method you want to use")
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
        >>> kpt,td = img1._getRawKeypoints() # t is template
        >>> kps,sd = img2._getRawKeypoints() # s is source
        >>> idx,dist = img1._getFLANNMatches(sd,td)
        >>> j = idx[42]
        >>> print kps[j] # matches kp 42
        >>> print dist[i] # the match quality.

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
        try:
            import cv2
        except:
            logger.warning("Can't run FLANN Matches without OpenCV >= 2.3.0")
            return
        FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
        flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 4)
        flann = cv2.flann_Index(sd, flann_params)
        idx, dist = flann.knnSearch(td, 1, params = {}) # bug: need to provide empty dict
        del flann
        return idx,dist

    def drawKeypointMatches(self,template,thresh=500.00,minDist=0.15,width=1):
        """
        **SUMMARY**

        Draw keypoints draws a side by side representation of two images, calculates
        keypoints for both images, determines the keypoint correspondences, and then draws
        the correspondences. This method is helpful for debugging keypoint calculations
        and also looks really cool :) .  The parameters mirror the parameters used 
        for findKeypointMatches to assist with debugging 

        **PARAMETERS**

        * *template* - A template image. 
        * *quality* - The feature quality metric. This can be any value between about 300 and 500. Higher
          values should return fewer, but higher quality features. 
        * *minDist* - The value below which the feature correspondence is considered a match. This 
          is the distance between two feature vectors. Good values are between 0.05 and 0.3
        * *width* - The width of the drawn line.

        **RETURNS**

        A side by side image of the template and source image with each feature correspondence 
        draw in a different color. 

        **EXAMPLE**

        >>> img = cam.getImage()
        >>> template = Image("myTemplate.png")
        >>> result = img.drawKeypointMatches(self,template,300.00,0.4):

        **NOTES**

        If you would prefer to work with the raw keypoints and descriptors each image keeps
        a local cache of the raw values. These are named:
        
        self._mKeyPoints # A tuple of keypoint objects
        See: http://opencv.itseez.com/modules/features2d/doc/common_interfaces_of_feature_detectors.html#keypoint-keypoint
        self._mKPDescriptors # The descriptor as a floating point numpy array
        self._mKPFlavor = "NONE" # The flavor of the keypoints as a string. 

        **SEE ALSO**

        :py:meth:`drawKeypointMatches`
        :py:meth:`findKeypoints`
        :py:meth:`findKeypointMatch`

        """
        if template == None:
          return None
          
        resultImg = template.sideBySide(self,scale=False)
        hdif = (self.height-template.height)/2
        skp,sd = self._getRawKeypoints(thresh)
        tkp,td = template._getRawKeypoints(thresh)
        if( td == None or sd == None ):
            logger.warning("We didn't get any descriptors. Image might be too uniform or blurry." )
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
        **SUMMARY**

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

        .. Warning::
          This method is only capable of finding one instance of the template in an image. 
          If more than one instance is visible the homography calculation and the method will 
          fail.

        **PARAMETERS**

        * *template* - A template image. 
        * *quality* - The feature quality metric. This can be any value between about 300 and 500. Higher
          values should return fewer, but higher quality features. 
        * *minDist* - The value below which the feature correspondence is considered a match. This 
          is the distance between two feature vectors. Good values are between 0.05 and 0.3
        * *minMatch* - The percentage of features which must have matches to proceed with homography calculation.
          A value of 0.4 means 40% of features must match. Higher values mean better matches
          are used. Good values are between about 0.3 and 0.7

 
        **RETURNS** 

        If a homography (match) is found this method returns a feature set with a single 
        KeypointMatch feature. If no match is found None is returned.
         
        **EXAMPLE**
        
        >>> template = Image("template.png")
        >>> img = camera.getImage()
        >>> fs = img.findKeypointMatch(template)
        >>> if( fs is not None ):
        >>>      fs[0].draw()
        >>>      img.show()
        
        **NOTES**

        If you would prefer to work with the raw keypoints and descriptors each image keeps
        a local cache of the raw values. These are named:
        
        | self._mKeyPoints # A Tuple of keypoint objects
        | self._mKPDescriptors # The descriptor as a floating point numpy array
        | self._mKPFlavor = "NONE" # The flavor of the keypoints as a string. 
        | `See Documentation <http://opencv.itseez.com/modules/features2d/doc/common_interfaces_of_feature_detectors.html#keypoint-keypoint>`_

        **SEE ALSO**
        
        :py:meth:`_getRawKeypoints` 
        :py:meth:`_getFLANNMatches`
        :py:meth:`drawKeypointMatches`
        :py:meth:`findKeypoints`

        """
        
        try:
            import cv2
        except:
            logger.warning("Can't Match Keypoints without OpenCV >= 2.3.0")
            return
            
        if template == None:
          return None
        
        skp,sd = self._getRawKeypoints(quality)
        tkp,td = template._getRawKeypoints(quality)
        if( skp == None or tkp == None ):
            logger.warning("I didn't get any keypoints. Image might be too uniform or blurry." )
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
            pt0i = (float(abs(pt0p[0][0]+xo)),float(abs(pt0p[0][1]+yo))) 
            pt1i = (float(abs(pt1p[0][0]+xo)),float(abs(pt1p[0][1]+yo)))
            pt2i = (float(abs(pt2p[0][0]+xo)),float(abs(pt2p[0][1]+yo)))
            pt3i = (float(abs(pt3p[0][0]+xo)),float(abs(pt3p[0][1]+yo)))
            #print "--------------------------"
            #print str(pt0)+"--->"+str(pt0p)+"--->"+str(pt0i)
            #print str(pt1)+"--->"+str(pt1p)+"--->"+str(pt1i)
            #print str(pt2)+"--->"+str(pt2p)+"--->"+str(pt2i)
            #print str(pt3)+"--->"+str(pt3p)+"--->"+str(pt3i)

            #construct the feature set and return it. 
            fs = FeatureSet()
            fs.append(KeypointMatch(self,template,(pt0i,pt1i,pt2i,pt3i),homography))
            return fs
        else:
            return None 


    def findKeypoints(self,min_quality=300.00,flavor="SURF",highQuality=False ): 
        """
        **SUMMARY**

        This method finds keypoints in an image and returns them as a feature set.
        Keypoints are unique regions in an image that demonstrate some degree of 
        invariance to changes in camera pose and illumination. They are helpful
        for calculating homographies between camera views, object rotations, and
        multiple view overlaps.

        We support four keypoint detectors and only one form of keypoint descriptors.
        Only the surf flavor of keypoint returns feature and descriptors at this time.
       
        **PARAMETERS**
        
        * *min_quality* - The minimum quality metric for SURF descriptors. Good values
          range between about 300.00 and 600.00
        
        * *flavor* - a string indicating the method to use to extract features.
          A good primer on how feature/keypoint extractiors can be found in
          `feature detection on wikipedia <http://en.wikipedia.org/wiki/Feature_detection_(computer_vision)>`_ 
          and 
          `this tutorial. <http://www.cg.tu-berlin.de/fileadmin/fg144/Courses/07WS/compPhoto/Feature_Detection.pdf>`_

        
          * "SURF" - extract the SURF features and descriptors. If you don't know
            what to use, use this. 

            See: http://en.wikipedia.org/wiki/SURF        

          * "STAR" - The STAR feature extraction algorithm

            See: http://pr.willowgarage.com/wiki/Star_Detector

          * "FAST" - The FAST keypoint extraction algorithm

            See: http://en.wikipedia.org/wiki/Corner_detection#AST_based_feature_detectors
          
          All the flavour specified below are for OpenCV versions >= 2.4.0 :
          
          * "MSER" - Maximally Stable Extremal Regions algorithm
            
            See: http://en.wikipedia.org/wiki/Maximally_stable_extremal_regions
          
          * "Dense" - 
          
          * "ORB" - The Oriented FAST and Rotated BRIEF
            
            See: http://www.willowgarage.com/sites/default/files/orb_final.pdf
            
          * "SIFT" - Scale-invariant feature transform
           
            See: http://en.wikipedia.org/wiki/Scale-invariant_feature_transform      
        
        * *highQuality* - The SURF descriptor comes in two forms, a vector of 64 descriptor 
          values and a vector of 128 descriptor values. The latter are "high" 
          quality descriptors. 
                      
        **RETURNS**

        A feature set of KeypointFeatures. These KeypointFeatures let's you draw each 
        feature, crop the features, get the feature descriptors, etc. 

        **EXAMPLE**

        >>> img = Image("aerospace.jpg")
        >>> fs = img.findKeypoints(flavor="SURF",min_quality=500,highQuality=True)
        >>> fs = fs.sortArea()
        >>> fs[-1].draw()
        >>> img.draw()

        **NOTES**

        If you would prefer to work with the raw keypoints and descriptors each image keeps
        a local cache of the raw values. These are named:

        :py:meth:`_getRawKeypoints` 
        :py:meth:`_getFLANNMatches`
        :py:meth:`drawKeypointMatches`
        :py:meth:`findKeypoints`

        """
        try:
            import cv2                    
        except:
            logger.warning("Can't use Keypoints without OpenCV >= 2.3.0")
            return None

        fs = FeatureSet()
        kp = []
        d = []
        if highQuality:
            kp,d = self._getRawKeypoints(thresh=min_quality,forceReset=True,flavor=flavor,highQuality=1)
        else:
            kp,d = self._getRawKeypoints(thresh=min_quality,forceReset=True,flavor=flavor,highQuality=0)

        if( flavor in ["ORB", "SIFT", "SURF"]  and kp!=None and d !=None ):
            for i in range(0,len(kp)):
                fs.append(KeyPoint(self,kp[i],d[i],flavor))
        elif(flavor in ["FAST", "STAR", "MSER", "Dense"] and kp!=None ):
            for i in range(0,len(kp)):
                fs.append(KeyPoint(self,kp[i],None,flavor))
        else:
            logger.warning("ImageClass.Keypoints: I don't know the method you want to use")
            return None

        return fs

    def findMotion(self, previous_frame, window=11, method='BM', aggregate=True):
        """
        **SUMMARY**

        findMotion performs an optical flow calculation. This method attempts to find 
        motion between two subsequent frames of an image. You provide it 
        with the previous frame image and it returns a feature set of motion
        fetures that are vectors in the direction of motion.

        **PARAMETERS**

        * *previous_frame* - The last frame as an Image. 
        * *window* - The block size for the algorithm. For the the HS and LK methods 
          this is the regular sample grid at which we return motion samples.
          For the block matching method this is the matching window size.
        * *method* - The algorithm to use as a string. 
          Your choices are:

          * 'BM' - default block matching robust but slow - if you are unsure use this.

          * 'LK' - `Lucas-Kanade method <http://en.wikipedia.org/wiki/Lucas%E2%80%93Kanade_method>`_ 

          * 'HS' - `Horn-Schunck method <http://en.wikipedia.org/wiki/Horn%E2%80%93Schunck_method>`_

        * *aggregate* - If aggregate is true, each of our motion features is the average of
          motion around the sample grid defined by window. If aggregate is false
          we just return the the value as sampled at the window grid interval. For 
          block matching this flag is ignored.

        **RETURNS**

        A featureset of motion objects. 

        **EXAMPLES**
        
        >>> cam = Camera()
        >>> img1 = cam.getImage()
        >>> img2 = cam.getImage()
        >>> motion = img2.findMotion(img1)
        >>> motion.draw()
        >>> img2.show()

        **SEE ALSO**
        
        :py:class:`Motion`
        :py:class:`FeatureSet`

        """
        try:
            import cv2
            ver = cv2.__version__
            #For OpenCV versions till 2.4.0,  cv2.__versions__ are of the form "$Rev: 4557 $" 
            if not ver.startswith('$Rev:') :
	        if int(ver.replace('.','0'))>=20400 :
              	    FLAG_VER = 1
            	    if (window > 9):
            		window = 9
            else :
                FLAG_VER = 0    			
        except :
            FLAG_VER = 0
            
        if( self.width != previous_frame.width or self.height != previous_frame.height):
            logger.warning("ImageClass.getMotion: To find motion the current and previous frames must match")
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
            # For versions with OpenCV 2.4.0 and below.
            if ( FLAG_VER==0):
            	block = (window,window) # block size
            	shift = (int(window*1.2),int(window*1.2)) # how far to shift the block
            	spread = (window*2,window*2) # the search windows.
            	wv = (self.width - block[0]) / shift[0] # the result image size
            	hv = (self.height - block[1]) / shift[1]
            	xf = cv.CreateMat(hv, wv, cv.CV_32FC1)
            	yf = cv.CreateMat(hv, wv, cv.CV_32FC1)
            	cv.CalcOpticalFlowBM(previous_frame._getGrayscaleBitmap(),self._getGrayscaleBitmap(),block,shift,spread,0,xf,yf)
            
            #For versions with OpenCV 2.4.0 and above.
            elif ( FLAG_VER==1) :
	        block = (window,window) # block size
                shift = (int(window*0.2),int(window*0.2)) # how far to shift the block
                spread = (window,window) # the search windows.
	        wv = self.width-block[0]+shift[0]
	        hv = self.height-block[1]+shift[1]
	        xf = cv.CreateImage((wv,hv), cv.IPL_DEPTH_32F, 1)
                yf = cv.CreateImage((wv,hv), cv.IPL_DEPTH_32F, 1)
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
            logger.warning("ImageClass.findMotion: I don't know what algorithm you want to use. Valid method choices are Block Matching -> \"BM\" Horn-Schunck -> \"HS\" and Lucas-Kanade->\"LK\" ") 
            return None
	
        max_mag = math.sqrt(max_mag) # do the normalization
        for f in fs:
            f.normalizeTo(max_mag)

        return fs


    
    def _generatePalette(self,bins,hue):
        """
        **SUMMARY**

        This is the main entry point for palette generation. A palette, for our purposes,
        is a list of the main colors in an image. Creating a palette with 10 bins, tries 
        to cluster the colors in rgb space into ten distinct groups. In hue space we only
        look at the hue channel. All of the relevant palette data is cached in the image 
        class. 

        **PARAMETERS**

        bins - an integer number of bins into which to divide the colors in the image.
        hue  - if hue is true we do only cluster on the image hue values. 

        **RETURNS**

        Nothing, but creates the image's cached values for: 
        
        self._mDoHuePalette
        self._mPaletteBins
        self._mPalette 
        self._mPaletteMembers 
        self._mPalettePercentages


        **EXAMPLE**
        
        >>> img._generatePalette(bins=42)

        **NOTES**

        The hue calculations should be siginificantly faster than the generic RGB calculation as 
        it works in a one dimensional space. Sometimes the underlying scipy method freaks out 
        about k-means initialization with the following warning:
        
        UserWarning: One of the clusters is empty. Re-run kmean with a different initialization.

        This shouldn't be a real problem. 
        
        **SEE ALSO**

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
        **SUMMARY**

        This method returns the colors in the palette of the image. A palette is the 
        set of the most common colors in an image. This method is helpful for segmentation.

        **PARAMETERS**

        * *bins* - an integer number of bins into which to divide the colors in the image.
        * *hue*  - if hue is true we do only cluster on the image hue values. 

        **RETURNS**

        A numpy array of the BGR color tuples. 

        **EXAMPLE**
        
        >>> p = img.getPalette(bins=42)
        >>> print p[2]
       
        **NOTES**
       
        The hue calculations should be siginificantly faster than the generic RGB calculation as 
        it works in a one dimensional space. Sometimes the underlying scipy method freaks out 
        about k-means initialization with the following warning:
        
        .. Warning::
          One of the clusters is empty. Re-run kmean with a different initialization.
          This shouldn't be a real problem. 
        
        **SEE ALSO**
               
        :py:meth:`rePalette`
        :py:meth:`drawPaletteColors`
        :py:meth:`palettize`
        :py:meth:`getPalette`
        :py:meth:`binarizeFromPalette`
        :py:meth:`findBlobsFromPalette`
        
        """
        self._generatePalette(bins,hue)
        return self._mPalette


    def rePalette(self,palette,hue=False):
        """
        **SUMMARY**
        
        rePalette takes in the palette from another image and attempts to apply it to this image.
        This is helpful if you want to speed up the palette computation for a series of images (like those in a
        video stream.

        **PARAMETERS**
        
        * *palette* - The pre-computed palette from another image.
        * *hue* - Boolean Hue - if hue is True we use a hue palette, otherwise we use a BGR palette.

        **RETURNS**

        A SimpleCV Image.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> img2 = Image("logo")
        >>> p = img.getPalette()
        >>> result = img2.rePalette(p)
        >>> result.show()

        **SEE ALSO**
               
        :py:meth:`rePalette`
        :py:meth:`drawPaletteColors`
        :py:meth:`palettize`
        :py:meth:`getPalette`
        :py:meth:`binarizeFromPalette`
        :py:meth:`findBlobsFromPalette`
        
        """
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
        **SUMMARY**

        This method returns the visual representation (swatches) of the palette in an image. The palette 
        is orientated either horizontally or vertically, and each color is given an area 
        proportional to the number of pixels that have that color in the image. The palette 
        is arranged as it is returned from the clustering algorithm. When size is left
        to its default value, the palette size will match the size of the 
        orientation, and then be 10% of the other dimension. E.g. if our image is 640X480 the horizontal
        palette will be (640x48) likewise the vertical palette will be (480x64)
        
        If a Hue palette is used this method will return a grayscale palette.
        
        **PARAMETERS**

        * *bins* - an integer number of bins into which to divide the colors in the image.
        * *hue* - if hue is true we do only cluster on the image hue values. 
        * *size* - The size of the generated palette as a (width,height) tuple, if left default we select 
          a size based on the image so it can be nicely displayed with the 
          image. 
        * *horizontal* - If true we orientate our palette horizontally, otherwise vertically. 

        **RETURNS**

        A palette swatch image. 

        **EXAMPLE**
        
        >>> p = img1.drawPaletteColors()
        >>> img2 = img1.sideBySide(p,side="bottom")
        >>> img2.show()

        **NOTES**

        The hue calculations should be siginificantly faster than the generic RGB calculation as 
        it works in a one dimensional space. Sometimes the underlying scipy method freaks out 
        about k-means initialization with the following warning:
        
        .. Warning::
          One of the clusters is empty. Re-run kmean with a different initialization.
          This shouldn't be a real problem. 

        **SEE ALSO**
               
        :py:meth:`rePalette`
        :py:meth:`drawPaletteColors`
        :py:meth:`palettize`
        :py:meth:`getPalette`
        :py:meth:`binarizeFromPalette`
        :py:meth:`findBlobsFromPalette`
        
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
                    cv.AddS(pal,float(self._mPalette[i]),pal)
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
                    cv.AddS(pal,float(self._mPalette[i]),pal)
                    cv.ResetImageROI(pal)
                    idxL = idxH
                retVal = Image(pal)
                 
        return retVal 

    def palettize(self,bins=10,hue=False):
        """
        **SUMMARY**

        This method analyzes an image and determines the most common colors using a k-means algorithm.
        The method then goes through and replaces each pixel with the centroid of the clutsters found
        by k-means. This reduces the number of colors in an image to the number of bins. This can be particularly
        handy for doing segementation based on color.

        **PARAMETERS**

        * *bins* - an integer number of bins into which to divide the colors in the image.
        * *hue* - if hue is true we do only cluster on the image hue values. 
        

        **RETURNS**

        An image matching the original where each color is replaced with its palette value.  

        **EXAMPLE**
        
        >>> img2 = img1.palettize()
        >>> img2.show()

        **NOTES**

        The hue calculations should be siginificantly faster than the generic RGB calculation as 
        it works in a one dimensional space. Sometimes the underlying scipy method freaks out 
        about k-means initialization with the following warning:
        
        .. Warning:: 
          UserWarning: One of the clusters is empty. Re-run kmean with a different initialization.
          This shouldn't be a real problem. 

        **SEE ALSO**
               
        :py:meth:`rePalette`
        :py:meth:`drawPaletteColors`
        :py:meth:`palettize`
        :py:meth:`getPalette`
        :py:meth:`binarizeFromPalette`
        :py:meth:`findBlobsFromPalette`        

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


    def findBlobsFromPalette(self, palette_selection, dilate = 0, minsize=5, maxsize=0,appx_level=3):
        """
        **SUMMARY**

        This method attempts to use palettization to do segmentation and behaves similar to the 
        findBlobs blob in that it returs a feature set of blob objects. Once a palette has been 
        extracted using getPalette() we can then select colors from that palette to be labeled 
        white within our blobs. 

        **PARAMETERS**
        
        * *palette_selection* - color triplets selected from our palette that will serve turned into blobs
          These values can either be a 3xN numpy array, or a list of RGB triplets.                            
        * *dilate* - the optional number of dilation operations to perform on the binary image
          prior to performing blob extraction.
        * *minsize* - the minimum blob size in pixels
        * *maxsize* - the maximim blob size in pixels.
        * *appx_level* - The blob approximation level - an integer for the maximum distance between the true edge and the 
          approximation edge - lower numbers yield better approximation. 

        **RETURNS**

        If the method executes successfully a FeatureSet of Blobs is returned from the image. If the method 
        fails a value of None is returned. 

       **EXAMPLE**

        >>> img = Image("lenna")
        >>> p = img.getPalette()
        >>> blobs = img.findBlobsFromPalette( (p[0],p[1],[6]) )
        >>> blobs.draw()
        >>> img.show()

        **SEE ALSO**
               
        :py:meth:`rePalette`
        :py:meth:`drawPaletteColors`
        :py:meth:`palettize`
        :py:meth:`getPalette`
        :py:meth:`binarizeFromPalette`
        :py:meth:`findBlobsFromPalette`        
               
        """

        #we get the palette from find palete 
        #ASSUME: GET PALLETE WAS CALLED!
        bwimg = self.binarizeFromPalette(palette_selection)
        if( dilate > 0 ):
            bwimg =bwimg.dilate(dilate)
        
        if (maxsize == 0):  
            maxsize = self.width * self.height 
        #create a single channel image, thresholded to parameters
    
        blobmaker = BlobMaker()
        blobs = blobmaker.extractFromBinary(bwimg,
            self, minsize = minsize, maxsize = maxsize,appx_level=appx_level)
    
        if not len(blobs):
            return None
        return blobs


    def binarizeFromPalette(self, palette_selection):
        """
        **SUMMARY**

        This method uses the color palette to generate a binary (black and white) image. Palaette selection
        is a list of color tuples retrieved from img.getPalette(). The provided values will be drawn white
        while other values will be black. 

        **PARAMETERS**

        palette_selection - color triplets selected from our palette that will serve turned into blobs
        These values can either be a 3xN numpy array, or a list of RGB triplets.

        **RETURNS**

        This method returns a black and white images, where colors that are close to the colors
        in palette_selection are set to white

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> p = img.getPalette()
        >>> b = img.binarizeFromPalette( (p[0],p[1],[6]) )
        >>> b.show()

        **SEE ALSO**
               
        :py:meth:`rePalette`
        :py:meth:`drawPaletteColors`
        :py:meth:`palettize`
        :py:meth:`getPalette`
        :py:meth:`binarizeFromPalette`
        :py:meth:`findBlobsFromPalette`        
               
        """

        #we get the palette from find palete 
        #ASSUME: GET PALLETE WAS CALLED!
        if( self._mPalette == None ):
            logger.warning("Image.binarizeFromPalette: No palette exists, call getPalette())")
            return None
        retVal = None
        img = self.palettize(self._mPaletteBins, hue=self._mDoHuePalette)
        if( not self._mDoHuePalette ):
            npimg = img.getNumpy()
            white = np.array([255,255,255])
            black = np.array([0,0,0])

            for p in palette_selection:
                npimg = np.where(npimg != p,npimg,white)
            
            npimg = np.where(npimg != white,black,white)
            retVal = Image(npimg)
        else:
            npimg = img.getNumpy()[:,:,1]
            white = np.array([255])
            black = np.array([0])

            for p in palette_selection:
                npimg = np.where(npimg != p,npimg,white)
            
            npimg = np.where(npimg != white,black,white)
            retVal = Image(npimg)

        return retVal

    def skeletonize(self, radius = 5):
        """
        **SUMMARY**

        Skeletonization is the process of taking in a set of blobs (here blobs are white
        on a black background) and finding a squigly line that would be the back bone of
        the blobs were they some sort of vertebrate animal. Another way of thinking about 
        skeletonization is that it finds a series of lines that approximates a blob's shape.

        A good summary can be found here:

        http://www.inf.u-szeged.hu/~palagyi/skel/skel.html

        **PARAMETERS**
        
        * *radius* - an intenger that defines how roughly how wide a blob must be to be added 
          to the skeleton, lower values give more skeleton lines, higher values give
          fewer skeleton lines. 
        
        **EXAMPLE**
       
        >>> cam = Camera()
        >>> while True:
        >>>     img = cam.getImage()
        >>>     b = img.binarize().invert()
        >>>     s = img.skeletonize()
        >>>     r = b-s
        >>>     r.show()

        
        **NOTES**

        This code was a suggested improvement by Alex Wiltchko, check out his awesome blog here:

        http://alexbw.posterous.com/

        """
        img = self.toGray().getNumpy()[:,:,0]
        distance_img = ndimage.distance_transform_edt(img)
        morph_laplace_img = ndimage.morphological_laplace(distance_img, (radius, radius))
        skeleton = morph_laplace_img < morph_laplace_img.min()/2
        retVal = np.zeros([self.width,self.height])
        retVal[skeleton] = 255
        return Image(retVal)

    def smartThreshold(self, mask=None, rect=None):
        """
        **SUMMARY**

        smartThreshold uses a method called grabCut, also called graph cut, to 
        automagically generate a grayscale mask image. The dumb version of threshold
        just uses color, smartThreshold looks at
        both color and edges to find a blob. To work smartThreshold needs either a 
        rectangle that bounds the object you want to find, or a mask. If you use
        a rectangle make sure it holds the complete object. In the case of a mask, it
        need not be a normal binary mask, it can have the normal white foreground and black
        background, but also a light and dark gray values that correspond to areas 
        that are more likely to be foreground and more likely to be background. These
        values can be found in the color class as Color.BACKGROUND, Color.FOREGROUND, 
        Color.MAYBE_BACKGROUND, and Color.MAYBE_FOREGROUND. 

        **PARAMETERS**

        * *mask* - A grayscale mask the same size as the image using the 4 mask color values
        * *rect* - A rectangle tuple of the form (x_position,y_position,width,height)

        **RETURNS** 

        A grayscale image with the foreground / background values assigned to:

        * BACKGROUND = (0,0,0)

        * MAYBE_BACKGROUND = (64,64,64)

        * MAYBE_FOREGROUND =  (192,192,192)

        * FOREGROUND = (255,255,255)
        
        **EXAMPLE**

        >>> img = Image("RatTop.png")
        >>> mask = Image((img.width,img.height))
        >>> mask.dl().circle((100,100),80,color=Color.MAYBE_BACKGROUND,filled=True)
        >>> mask.dl().circle((100,100),60,color=Color.MAYBE_FOREGROUND,filled=True)
        >>> mask.dl().circle((100,100),40,color=Color.FOREGROUND,filled=True)
        >>> mask = mask.applyLayers()
        >>> new_mask = img.smartThreshold(mask=mask)
        >>> new_mask.show()

        **NOTES**

        http://en.wikipedia.org/wiki/Graph_cuts_in_computer_vision

        **SEE ALSO**

        :py:meth:`smartFindBlobs`

        """
        try:
            import cv2
        except:
            logger.warning("Can't Do GrabCut without OpenCV >= 2.3.0")
            return
        retVal = []
        if( mask is not None ):
            bmp = mask._getGrayscaleBitmap()
            # translate the human readable images to something opencv wants using a lut
            LUT = np.zeros((256,1),dtype=uint8)
            LUT[255]=1
            LUT[64]=2
            LUT[192]=3
            cv.LUT(bmp,bmp,cv.fromarray(LUT))
            mask_in = np.array(cv.GetMat(bmp)) 
            # get our image in a flavor grab cut likes
            npimg = np.array(cv.GetMat(self.getBitmap())) 
            # require by opencv
            tmp1 = np.zeros((1, 13 * 5))
            tmp2 = np.zeros((1, 13 * 5))
            # do the algorithm
            cv2.grabCut(npimg,mask_in,None,tmp1,tmp2,10,mode=cv2.GC_INIT_WITH_MASK)
            # generate the output image
            output = cv.CreateImageHeader((mask_in.shape[1],mask_in.shape[0]),cv.IPL_DEPTH_8U,1)
            cv.SetData(output,mask_in.tostring(),mask_in.dtype.itemsize*mask_in.shape[1])
            # remap the color space
            LUT = np.zeros((256,1),dtype=uint8)
            LUT[1]=255
            LUT[2]=64
            LUT[3]=192
            cv.LUT(output,output,cv.fromarray(LUT))
            # and create the return value
            mask._graybitmap = None # don't ask me why... but this gets corrupted
            retVal = Image(output)

        elif ( rect is not None ):
            npimg = np.array(cv.GetMat(self.getBitmap())) 
            tmp1 = np.zeros((1, 13 * 5))
            tmp2 = np.zeros((1, 13 * 5))
            mask = np.zeros((self.height,self.width),dtype='uint8')
            cv2.grabCut(npimg,mask,rect,tmp1,tmp2,10,mode=cv2.GC_INIT_WITH_RECT)
            bmp = cv.CreateImageHeader((mask.shape[1],mask.shape[0]),cv.IPL_DEPTH_8U,1)
            cv.SetData(bmp,mask.tostring(),mask.dtype.itemsize*mask.shape[1])
            LUT = np.zeros((256,1),dtype=uint8)
            LUT[1]=255
            LUT[2]=64
            LUT[3]=192
            cv.LUT(bmp,bmp,cv.fromarray(LUT))
            retVal = Image(bmp)
        else:
            logger.warning( "ImageClass.findBlobsSmart requires either a mask or a selection rectangle. Failure to provide one of these causes your bytes to splinter and bit shrapnel to hit your pipeline making it asplode in a ball of fire. Okay... not really")
        return retVal
            
    def smartFindBlobs(self,mask=None,rect=None,thresh_level=2,appx_level=3):
        """
        **SUMMARY**

        smartFindBlobs uses a method called grabCut, also called graph cut, to 
        automagically determine the boundary of a blob in the image. The dumb find
        blobs just uses color threshold to find the boundary, smartFindBlobs looks at
        both color and edges to find a blob. To work smartFindBlobs needs either a 
        rectangle that bounds the object you want to find, or a mask. If you use
        a rectangle make sure it holds the complete object. In the case of a mask, it
        need not be a normal binary mask, it can have the normal white foreground and black
        background, but also a light and dark gray values that correspond to areas 
        that are more likely to be foreground and more likely to be background. These
        values can be found in the color class as Color.BACKGROUND, Color.FOREGROUND, 
        Color.MAYBE_BACKGROUND, and Color.MAYBE_FOREGROUND. 

        **PARAMETERS**

        * *mask* - A grayscale mask the same size as the image using the 4 mask color values
        * *rect* - A rectangle tuple of the form (x_position,y_position,width,height)
        * *thresh_level* - This represents what grab cut values to use in the mask after the
          graph cut algorithm is run, 
        
          * 1  - means use the foreground, maybe_foreground, and maybe_background values
          * 2  - means use the foreground and maybe_foreground values.
          * 3+ - means use just the foreground

        * *appx_level* - The blob approximation level - an integer for the maximum distance between the true edge and the 
          approximation edge - lower numbers yield better approximation. 


        **RETURNS**

        A featureset of blobs. If everything went smoothly only a couple of blobs should
        be present. 
        
        **EXAMPLE**
        
        >>> img = Image("RatTop.png")
        >>> mask = Image((img.width,img.height))
        >>> mask.dl().circle((100,100),80,color=Color.MAYBE_BACKGROUND,filled=True
        >>> mask.dl().circle((100,100),60,color=Color.MAYBE_FOREGROUND,filled=True)
        >>> mask.dl().circle((100,100),40,color=Color.FOREGROUND,filled=True)
        >>> mask = mask.applyLayers()
        >>> blobs = img.smartFindBlobs(mask=mask)
        >>> blobs.draw()
        >>> blobs.show()

        **NOTES**

        http://en.wikipedia.org/wiki/Graph_cuts_in_computer_vision

        **SEE ALSO**

        :py:meth:`smartThreshold`

        """
        result = self.smartThreshold(mask, rect)
        binary = None
        retVal = None

        if result:
          if( thresh_level ==  1 ):
              result = result.threshold(192)
          elif( thresh_level == 2):
              result = result.threshold(128)
          elif( thresh_level > 2 ):
              result = result.threshold(1)
          bm = BlobMaker()
          retVal = bm.extractFromBinary(result,self,appx_level)
        
        return retVal

    def threshold(self, value):
        """
        **SUMMARY**

        We roll old school with this vanilla threshold function. It takes your image
        converts it to grayscale, and applies a threshold. Values above the threshold 
        are white, values below the threshold are black (note this is in contrast to 
        binarize... which is a stupid function that drives me up a wall). The resulting
        black and white image is returned.
        
        **PARAMETERS**

        * *value* - the threshold, goes between 0 and 255.

        **RETURNS**

        A black and white SimpleCV image.
        
        **EXAMPLE**

        >>> img = Image("purplemonkeydishwasher.png")
        >>> result = img.threshold(42)
       
        **NOTES**

        THRESHOLD RULES BINARIZE DROOLS!
        
        **SEE ALSO**

        :py:meth:`binarize`

        """
        gray = self._getGrayscaleBitmap()
        result = self.getEmpty(1)
        cv.Threshold(gray, result, value, 255, cv.CV_THRESH_BINARY)
        retVal = Image(result)
        return retVal


    def floodFill(self,points,tolerance=None,color=Color.WHITE,lower=None,upper=None,fixed_range=True):
        """
        **SUMMARY**

        FloodFill works just like ye olde paint bucket tool in your favorite image manipulation
        program. You select a point (or a list of points), a color, and a tolerance, and floodFill will start at that
        point, looking for pixels within the tolerance from your intial pixel. If the pixel is in
        tolerance, we will convert it to your color, otherwise the method will leave the pixel alone.
        The method accepts both single values, and triplet tuples for the tolerance values. If you 
        require more control over your tolerance you can use the upper and lower values. The fixed
        range parameter let's you toggle between setting the tolerance with repect to the seed pixel,
        and using a tolerance that is relative to the adjacent pixels. If fixed_range is true the
        method will set its tolerance with respect to the seed pixel, otherwise the tolerance will
        be with repsect to adjacent pixels. 

        **PARAMETERS**

        * *points* - A tuple, list of tuples, or np.array of seed points for flood fill
        * *tolerance* - The color tolerance as a single value or a triplet.
        * *color* - The color to replace the floodFill pixels with
        * *lower* - If tolerance does not provide enough control you can optionally set the upper and lower values
          around the seed pixel. This value can be a single value or a triplet. This will override
          the tolerance variable.
        * *upper* - If tolerance does not provide enough control you can optionally set the upper and lower values
          around the seed pixel. This value can be a single value or a triplet. This will override
          the tolerance variable.
        * *fixed_range* - If fixed_range is true we use the seed_pixel +/- tolerance
          If fixed_range is false, the tolerance is +/- tolerance of the values of 
          the adjacent pixels to the pixel under test.

        **RETURNS**
        
        An Image where the values similar to the seed pixel have been replaced by the input color. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> img2 = img.floodFill(((10,10),(54,32)),tolerance=(10,10,10),color=Color.RED)
        >>> img2.show()

        **SEE ALSO**

        :py:meth:`floodFillToMask`
        :py:meth:`findFloodFillBlobs`
        
        """
        if( isinstance(points,tuple) ):
            points = np.array(points)
        # first we guess what the user wants to do
        # if we get and int/float convert it to a tuple
        if( upper is None and lower is None and tolerance is None ):
            upper = (0,0,0)
            lower = (0,0,0)

        if( tolerance is not None and
            (isinstance(tolerance,float) or isinstance(tolerance,int))):
            tolerance = (int(tolerance),int(tolerance),int(tolerance))
            
        if( lower is not None and
            (isinstance(lower,float) or isinstance(lower, int)) ):
            lower = (int(lower),int(lower),int(lower))
        elif( lower is None ):
            lower = tolerance 
  
        if( upper is not None and
            (isinstance(upper,float) or isinstance(upper, int)) ):
            upper = (int(upper),int(upper),int(upper))
        elif( upper is None ):
            upper = tolerance 
    
        if( isinstance(points,tuple) ):
            points = np.array(points)

        flags = 8
        if( fixed_range ):
            flags = flags+cv.CV_FLOODFILL_FIXED_RANGE
            
        bmp = self.getEmpty()
        cv.Copy(self.getBitmap(),bmp)
    
        if( len(points.shape) != 1 ):
            for p in points:
                cv.FloodFill(bmp,tuple(p),color,lower,upper,flags)
        else:
            cv.FloodFill(bmp,tuple(points),color,lower,upper,flags)

        retVal = Image(bmp)
            
        return retVal

    def floodFillToMask(self, points,tolerance=None,color=Color.WHITE,lower=None,upper=None,fixed_range=True,mask=None):
        """
        **SUMMARY**

        floodFillToMask works sorta paint bucket tool in your favorite image manipulation
        program. You select a point (or a list of points), a color, and a tolerance, and floodFill will start at that
        point, looking for pixels within the tolerance from your intial pixel. If the pixel is in
        tolerance, we will convert it to your color, otherwise the method will leave the pixel alone.
        Unlike regular floodFill, floodFillToMask, will return a binary mask of your flood fill
        operation. This is handy if you want to extract blobs from an area, or create a 
        selection from a region. The method takes in an optional mask. Non-zero values of the mask
        act to block the flood fill operations. This is handy if you want to use an edge image
        to "stop" the flood fill operation within a particular region.

        The method accepts both single values, and triplet tuples for the tolerance values. If you 
        require more control over your tolerance you can use the upper and lower values. The fixed
        range parameter let's you toggle between setting the tolerance with repect to the seed pixel,
        and using a tolerance that is relative to the adjacent pixels. If fixed_range is true the
        method will set its tolerance with respect to the seed pixel, otherwise the tolerance will
        be with repsect to adjacent pixels. 

        **PARAMETERS**

        * *points* - A tuple, list of tuples, or np.array of seed points for flood fill
        * *tolerance* - The color tolerance as a single value or a triplet.
        * *color* - The color to replace the floodFill pixels with
        * *lower* - If tolerance does not provide enough control you can optionally set the upper and lower values
          around the seed pixel. This value can be a single value or a triplet. This will override
          the tolerance variable.
        * *upper* - If tolerance does not provide enough control you can optionally set the upper and lower values
          around the seed pixel. This value can be a single value or a triplet. This will override
          the tolerance variable.
        * *fixed_range* - If fixed_range is true we use the seed_pixel +/- tolerance
          If fixed_range is false, the tolerance is +/- tolerance of the values of 
          the adjacent pixels to the pixel under test.
        * *mask* - An optional mask image that can be used to control the flood fill operation. 
          the output of this function will include the mask data in the input mask. 
        
        **RETURNS**

        An Image where the values similar to the seed pixel have been replaced by the input color. 

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> mask = img.edges()
        >>> mask= img.floodFillToMask(((10,10),(54,32)),tolerance=(10,10,10),mask=mask)
        >>> mask.show

        **SEE ALSO**

        :py:meth:`floodFill`
        :py:meth:`findFloodFillBlobs`
        
        """
        mask_flag = 255 # flag weirdness
        if( isinstance(points,tuple) ):
            points = np.array(points)
        # first we guess what the user wants to do
        # if we get and int/float convert it to a tuple
        if( upper is None and lower is None and tolerance is None ):
            upper = (0,0,0)
            lower = (0,0,0)

        if( tolerance is not None and
            (isinstance(tolerance,float) or isinstance(tolerance,int))):
            tolerance = (int(tolerance),int(tolerance),int(tolerance))
            
        if( lower is not None and
            (isinstance(lower,float) or isinstance(lower, int)) ):
            lower = (int(lower),int(lower),int(lower))
        elif( lower is None ):
            lower = tolerance 
  
        if( upper is not None and
            (isinstance(upper,float) or isinstance(upper, int)) ):
            upper = (int(upper),int(upper),int(upper))
        elif( upper is None ):
            upper = tolerance 
    
        if( isinstance(points,tuple) ):
            points = np.array(points)
            
        flags = (mask_flag << 8 )+8
        if( fixed_range ):
            flags = flags + cv.CV_FLOODFILL_FIXED_RANGE

        localMask = None
        #opencv wants a mask that is slightly larger 
        if( mask is None ):
            localMask  = cv.CreateImage((self.width+2,self.height+2), cv.IPL_DEPTH_8U, 1)
            cv.Zero(localMask)
        else:
            localMask = mask.embiggen(size=(self.width+2,self.height+2))._getGrayscaleBitmap()

        bmp = self.getEmpty()
        cv.Copy(self.getBitmap(),bmp)
        if( len(points.shape) != 1 ):
            for p in points:
                cv.FloodFill(bmp,tuple(p),color,lower,upper,flags,localMask)
        else:
            cv.FloodFill(bmp,tuple(points),color,lower,upper,flags,localMask)

        retVal = Image(localMask)
        retVal = retVal.crop(1,1,self.width,self.height)
        return retVal

    def findBlobsFromMask(self, mask,threshold=128, minsize=10, maxsize=0,appx_level=3 ):
        """
        **SUMMARY**

        This method acts like findBlobs, but it lets you specifiy blobs directly by
        providing a mask image. The mask image must match the size of this image, and 
        the mask should have values > threshold where you want the blobs selected. This 
        method can be used with binarize, dialte, erode, floodFill, edges etc to 
        get really nice segmentation. 
        
        **PARAMETERS**

        * *mask* - The mask image, areas lighter than threshold will be counted as blobs.
          Mask should be the same size as this image. 
        * *threshold* - A single threshold value used when we binarize the mask. 
        * *minsize* - The minimum size of the returned blobs.
        * *maxsize*  - The maximum size of the returned blobs, if none is specified we peg 
          this to the image size. 
        * *appx_level* - The blob approximation level - an integer for the maximum distance between the true edge and the 
          approximation edge - lower numbers yield better approximation. 


        **RETURNS**

        A featureset of blobs. If no blobs are found None is returned. 

        **EXAMPLE**
        
        >>> img = Image("Foo.png")
        >>> mask = img.binarize().dilate(2)
        >>> blobs = img.findBlobsFromMask(mask)
        >>> blobs.show()
        
        **SEE ALSO**

        :py:meth:`findBlobs`
        :py:meth:`binarize`
        :py:meth:`threshold`
        :py:meth:`dilate`
        :py:meth:`erode`
        """
        if (maxsize == 0):  
            maxsize = self.width * self.height
        #create a single channel image, thresholded to parameters
        if( mask.width != self.width or mask.height != self.height ):
            logger.warning("ImageClass.findBlobsFromMask - your mask does not match the size of your image")
            print "FML"
            return None

        blobmaker = BlobMaker()
        gray = mask._getGrayscaleBitmap()
        result = mask.getEmpty(1)
        cv.Threshold(gray, result, threshold, 255, cv.CV_THRESH_BINARY)
        blobs = blobmaker.extractFromBinary(Image(result), self, minsize = minsize, maxsize = maxsize,appx_level=appx_level)
    
        if not len(blobs):
            return None
            
        return FeatureSet(blobs).sortArea()


    def findFloodFillBlobs(self,points,tolerance=None,lower=None,upper=None,
                           fixed_range=True,minsize=30,maxsize=-1):
        """

        **SUMMARY**

        This method lets you use a flood fill operation and pipe the results to findBlobs. You provide
        the points to seed floodFill and the rest is taken care of. 
        
        floodFill works just like ye olde paint bucket tool in your favorite image manipulation
        program. You select a point (or a list of points), a color, and a tolerance, and floodFill will start at that
        point, looking for pixels within the tolerance from your intial pixel. If the pixel is in
        tolerance, we will convert it to your color, otherwise the method will leave the pixel alone.
        The method accepts both single values, and triplet tuples for the tolerance values. If you 
        require more control over your tolerance you can use the upper and lower values. The fixed
        range parameter let's you toggle between setting the tolerance with repect to the seed pixel,
        and using a tolerance that is relative to the adjacent pixels. If fixed_range is true the
        method will set its tolerance with respect to the seed pixel, otherwise the tolerance will
        be with repsect to adjacent pixels. 

        **PARAMETERS**

        * *points* - A tuple, list of tuples, or np.array of seed points for flood fill.        
        * *tolerance* - The color tolerance as a single value or a triplet.
        * *color* - The color to replace the floodFill pixels with        
        * *lower* - If tolerance does not provide enough control you can optionally set the upper and lower values
          around the seed pixel. This value can be a single value or a triplet. This will override
          the tolerance variable.
        * *upper* - If tolerance does not provide enough control you can optionally set the upper and lower values
          around the seed pixel. This value can be a single value or a triplet. This will override
          the tolerance variable.
        * *fixed_range* - If fixed_range is true we use the seed_pixel +/- tolerance
          If fixed_range is false, the tolerance is +/- tolerance of the values of 
          the adjacent pixels to the pixel under test.
        * *minsize* - The minimum size of the returned blobs.
        * *maxsize* - The maximum size of the returned blobs, if none is specified we peg 
          this to the image size. 

        **RETURNS**        

        A featureset of blobs. If no blobs are found None is returned. 
        
        An Image where the values similar to the seed pixel have been replaced by the input color. 

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> blerbs = img.findFloodFillBlobs(((10,10),(20,20),(30,30)),tolerance=30)
        >>> blerbs.show()

        **SEE ALSO**

        :py:meth:`findBlobs`
        :py:meth:`floodFill`
        
        """
        mask = self.floodFillToMask(points,tolerance,color=Color.WHITE,lower=lower,upper=upper,fixed_range=fixed_range)
        return self.findBlobsFromMask(mask,minsize,maxsize)

    def _doDFT(self, grayscale=False):
        """
        **SUMMARY**

        This private method peforms the discrete Fourier transform on an input image.
        The transform can be applied to a single channel gray image or to each channel of the
        image. Each channel generates a 64F 2 channel IPL image corresponding to the real 
        and imaginary components of the DFT. A list of these IPL images are then cached 
        in the private member variable _DFT. 

        
        **PARAMETERS**

        * *grayscale* - If grayscale is True we first covert the image to grayscale, otherwise
          we perform the operation on each channel. 
        
        **RETURNS**

        nothing - but creates a locally cached list of IPL imgaes corresponding to the real
        and imaginary components of each channel. 
        
        **EXAMPLE**

        >>> img = Image('logo.png')
        >>> img._doDFT()
        >>> img._DFT[0] # get the b channel Re/Im components

        **NOTES**

        http://en.wikipedia.org/wiki/Discrete_Fourier_transform
        http://math.stackexchange.com/questions/1002/fourier-transform-for-dummies

        **TO DO**

        This method really needs to convert the image to an optimal DFT size. 
        http://opencv.itseez.com/modules/core/doc/operations_on_arrays.html#getoptimaldftsize

        """
        if( grayscale and (len(self._DFT) == 0 or len(self._DFT) == 3)):
            self._DFT = []
            img = self._getGrayscaleBitmap()
            width, height = cv.GetSize(img)
            src = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 2)
            dst = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 2)
            data = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 1)
            blank = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 1)
            cv.ConvertScale(img,data,1.0)
            cv.Zero(blank)
            cv.Merge(data,blank,None,None,src)
            cv.Merge(data,blank,None,None,dst)
            cv.DFT(src, dst, cv.CV_DXT_FORWARD)
            self._DFT.append(dst)
        elif( not grayscale and (len(self._DFT) < 2 )):
            self._DFT = []
            r = self.getEmpty(1)
            g = self.getEmpty(1)
            b = self.getEmpty(1)
            cv.Split(self.getBitmap(),b,g,r,None)
            chans = [b,g,r]
            width = self.width
            height = self.height
            data = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 1)
            blank = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 1)
            src = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 2)
            for c in chans:                
                dst = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 2)
                cv.ConvertScale(c,data,1.0)
                cv.Zero(blank)
                cv.Merge(data,blank,None,None,src)
                cv.Merge(data,blank,None,None,dst)
                cv.DFT(src, dst, cv.CV_DXT_FORWARD)
                self._DFT.append(dst)

    def _getDFTClone(self,grayscale=False):
        """
        **SUMMARY**
        
        This method works just like _doDFT but returns a deep copy
        of the resulting array which can be used in destructive operations.

        **PARAMETERS**

        * *grayscale* - If grayscale is True we first covert the image to grayscale, otherwise
          we perform the operation on each channel. 

        **RETURNS**
        
        A deep copy of the cached DFT real/imaginary image list. 
        
        **EXAMPLE**
        
        >>> img = Image('logo.png')
        >>> myDFT = img._getDFTClone()
        >>> SomeCVFunc(myDFT[0])

        **NOTES**

        http://en.wikipedia.org/wiki/Discrete_Fourier_transform
        http://math.stackexchange.com/questions/1002/fourier-transform-for-dummies

        **SEE ALSO**

        ImageClass._doDFT()

        """
        # this is needs to be switched to the optimal 
        # DFT size for faster processing. 
        self._doDFT(grayscale)
        retVal = []
        if(grayscale):
            gs = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_64F,2)
            cv.Copy(self._DFT[0],gs)
            retVal.append(gs)
        else:
            for img in self._DFT:
                temp = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_64F,2)
                cv.Copy(img,temp)
                retVal.append(temp)
        return retVal

    def rawDFTImage(self,grayscale=False):
        """
        **SUMMARY**
        
        This method returns the **RAW** DFT transform of an image as a list of IPL Images.
        Each result image is a two channel 64f image where the first channel is the real
        component and the second channel is teh imaginary component. If the operation 
        is performed on an RGB image and grayscale is False the result is a list of 
        these images of the form [b,g,r].

        **PARAMETERS**

        * *grayscale* - If grayscale is True we first covert the image to grayscale, otherwise
          we perform the operation on each channel. 

        **RETURNS**
        
        A list of the DFT images (see above). Note that this is a shallow copy operation.
        
        **EXAMPLE**

        >>> img = Image('logo.png')
        >>> myDFT = img.rawDFTImage()
        >>> for c in myDFT:
        >>>    #do some operation on the DFT

        **NOTES**

        http://en.wikipedia.org/wiki/Discrete_Fourier_transform
        http://math.stackexchange.com/questions/1002/fourier-transform-for-dummies

        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`
        
        """
        self._doDFT(grayscale)
        return self._DFT 

    def getDFTLogMagnitude(self,grayscale=False):
        """
        **SUMMARY**

        This method returns the log value of the magnitude image of the DFT transform. This 
        method is helpful for examining and comparing the results of DFT transforms. The log
        component helps to "squish" the large floating point values into an image that can 
        be rendered easily. 

        In the image the low frequency components are in the corners of the image and the high 
        frequency components are in the center of the image. 

        **PARAMETERS**

        * *grayscale* - if grayscale is True we perform the magnitude operation of the grayscale
          image otherwise we perform the operation on each channel. 
        
        **RETURNS**
  
        Returns a SimpleCV image corresponding to the log magnitude of the input image.
        
        **EXAMPLE**
        
        >>> img = Image("RedDog2.jpg")
        >>> img.getDFTLogMagnitude().show()
        >>> lpf = img.lowPassFilter(img.width/10.img.height/10)
        >>> lpf.getDFTLogMagnitude().show()
        
        **NOTES**

        * http://en.wikipedia.org/wiki/Discrete_Fourier_transform
        * http://math.stackexchange.com/questions/1002/fourier-transform-for-dummies

        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`


        """
        dft = self._getDFTClone(grayscale)
        chans = []
        if( grayscale ):
            chans = [self.getEmpty(1)]
        else:
            chans = [self.getEmpty(1),self.getEmpty(1),self.getEmpty(1)]
        data = cv.CreateImage((self.width, self.height), cv.IPL_DEPTH_64F, 1)
        blank = cv.CreateImage((self.width, self.height), cv.IPL_DEPTH_64F, 1) 
        
        for i in range(0,len(chans)):
            cv.Split(dft[i],data,blank,None,None)
            cv.Pow( data, data, 2.0)
            cv.Pow( blank, blank, 2.0)
            cv.Add( data, blank, data, None)
            cv.Pow( data, data, 0.5 )
            cv.AddS( data, cv.ScalarAll(1.0), data, None ) # 1 + Mag
            cv.Log( data, data ) # log(1 + Mag
            min, max, pt1, pt2 = cv.MinMaxLoc(data)
            cv.Scale(data, data, 1.0/(max-min), 1.0*(-min)/(max-min))
            cv.Mul(data,data,data,255.0)
            cv.Convert(data,chans[i])

        retVal = None
        if( grayscale ):
            retVal = Image(chans[0])
        else:
            retVal = self.getEmpty()
            cv.Merge(chans[0],chans[1],chans[2],None,retVal)
            retVal = Image(retVal)
        return retVal

    def _boundsFromPercentage(self, floatVal, bound):
        return np.clip(int(floatVal*bound),0,bound)

    def applyDFTFilter(self,flt,grayscale=False):
        """
        **SUMMARY**

        This function allows you to apply an arbitrary filter to the DFT of an image. 
        This filter takes in a gray scale image, whiter values are kept and black values
        are rejected. In the DFT image, the lower frequency values are in the corners
        of the image, while the higher frequency components are in the center. For example,
        a low pass filter has white squares in the corners and is black everywhere else. 

        **PARAMETERS**

        * *grayscale* - if this value is True we perfrom the operation on the DFT of the gray
          version of the image and the result is gray image. If grayscale is true
          we perform the operation on each channel and the recombine them to create 
          the result.
        
        * *flt* - A grayscale filter image. The size of the filter must match the size of
          the image. 

        **RETURNS**

        A SimpleCV image after applying the filter. 

        **EXAMPLE**

        >>>  filter = Image("MyFilter.png")
        >>>  myImage = Image("MyImage.png")
        >>>  result = myImage.applyDFTFilter(filter)
        >>>  result.show()

        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`

        **TODO**

        Make this function support a separate filter image for each channel.
        """
        if( flt.width != self.width and 
            flt.height != self.height ):
            logger.warning("Image.applyDFTFilter - Your filter must match the size of the image")
        dft = []
        if( grayscale ):
            dft = self._getDFTClone(grayscale)
            flt = flt._getGrayscaleBitmap()
            flt64f = cv.CreateImage((flt.width,flt.height),cv.IPL_DEPTH_64F,1)
            cv.ConvertScale(flt,flt64f,1.0)
            finalFilt = cv.CreateImage((flt.width,flt.height),cv.IPL_DEPTH_64F,2)
            cv.Merge(flt64f,flt64f,None,None,finalFilt)
            for d in dft:
                cv.MulSpectrums(d,finalFilt,d,0)
        else: #break down the filter and then do each channel 
            dft = self._getDFTClone(grayscale)
            flt = flt.getBitmap()
            b = cv.CreateImage((flt.width,flt.height),cv.IPL_DEPTH_8U,1)
            g = cv.CreateImage((flt.width,flt.height),cv.IPL_DEPTH_8U,1)
            r = cv.CreateImage((flt.width,flt.height),cv.IPL_DEPTH_8U,1)
            cv.Split(flt,b,g,r,None)
            chans = [b,g,r]
            for c in range(0,len(chans)):
                flt64f = cv.CreateImage((chans[c].width,chans[c].height),cv.IPL_DEPTH_64F,1)
                cv.ConvertScale(chans[c],flt64f,1.0)
                finalFilt = cv.CreateImage((chans[c].width,chans[c].height),cv.IPL_DEPTH_64F,2)
                cv.Merge(flt64f,flt64f,None,None,finalFilt)
                cv.MulSpectrums(dft[c],finalFilt,dft[c],0)

        return self._inverseDFT(dft)

    def _boundsFromPercentage(self, floatVal, bound):
        return np.clip(int(floatVal*(bound/2.00)),0,(bound/2))

    def highPassFilter(self, xCutoff,yCutoff=None,grayscale=False):
        """
        **SUMMARY**

        This method applies a high pass DFT filter. This filter enhances 
        the high frequencies and removes the low frequency signals. This has
        the effect of enhancing edges. The frequencies are defined as going between
        0.00 and 1.00 and where 0 is the lowest frequency in the image and 1.0 is
        the highest possible frequencies. Each of the frequencies are defined 
        with respect to the horizontal and vertical signal. This filter 
        isn't perfect and has a harsh cutoff that causes ringing artifacts.

        **PARAMETERS**

        * *xCutoff* - The horizontal frequency at which we perform the cutoff. A separate 
          frequency can be used for the b,g, and r signals by providing a 
          list of values. The frequency is defined between zero to one, 
          where zero is constant component and 1 is the highest possible 
          frequency in the image. 

        * *yCutoff* - The cutoff frequencies in the y direction. If none are provided
          we use the same values as provided for x. 

        * *grayscale* - if this value is True we perfrom the operation on the DFT of the gray
          version of the image and the result is gray image. If grayscale is true
          we perform the operation on each channel and the recombine them to create 
          the result.
                 
        **RETURNS**
        
        A SimpleCV Image after applying the filter. 

        **EXAMPLE**
        
        >>> img = Image("SimpleCV/sampleimages/RedDog2.jpg")
        >>> img.getDFTLogMagnitude().show()
        >>> lpf = img.lowPassFilter([0.2,0.1,0.2])
        >>> lpf.show()
        >>> lpf.getDFTLogMagnitude().show()

        **NOTES**

        This filter is far from perfect and will generate a lot of ringing artifacts.
        * See: http://en.wikipedia.org/wiki/Ringing_(signal)
        * See: http://en.wikipedia.org/wiki/High-pass_filter#Image

        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`
        
        """
        if( isinstance(xCutoff,float) ):    
            xCutoff = [xCutoff,xCutoff,xCutoff]
        if( isinstance(yCutoff,float) ):
            yCutoff = [yCutoff,yCutoff,yCutoff]   
        if(yCutoff is None):
            yCutoff = [xCutoff[0],xCutoff[1],xCutoff[2]] 

        for i in range(0,len(xCutoff)):
            xCutoff[i] = self._boundsFromPercentage(xCutoff[i],self.width)
            yCutoff[i] = self._boundsFromPercentage(yCutoff[i],self.height)

        filter = None
        h  = self.height
        w  = self.width

        if( grayscale ):
            filter = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)            
            cv.Zero(filter)
            cv.AddS(filter,255,filter) # make everything white
            #now make all of the corners black
            cv.Rectangle(filter,(0,0),(xCutoff[0],yCutoff[0]),(0,0,0),thickness=-1) #TL
            cv.Rectangle(filter,(0,h-yCutoff[0]),(xCutoff[0],h),(0,0,0),thickness=-1) #BL
            cv.Rectangle(filter,(w-xCutoff[0],0),(w,yCutoff[0]),(0,0,0),thickness=-1) #TR
            cv.Rectangle(filter,(w-xCutoff[0],h-yCutoff[0]),(w,h),(0,0,0),thickness=-1) #BR       

        else:
            #I need to looking into CVMERGE/SPLIT... I would really need to know
            # how much memory we're allocating here
            filterB = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)
            filterG = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)
            filterR = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)
            cv.Zero(filterB)
            cv.Zero(filterG)
            cv.Zero(filterR)
            cv.AddS(filterB,255,filterB) # make everything white
            cv.AddS(filterG,255,filterG) # make everything whit
            cv.AddS(filterR,255,filterR) # make everything white
            #now make all of the corners black
            temp = [filterB,filterG,filterR]
            i = 0
            for f in temp:
                cv.Rectangle(f,(0,0),(xCutoff[i],yCutoff[i]),0,thickness=-1)
                cv.Rectangle(f,(0,h-yCutoff[i]),(xCutoff[i],h),0,thickness=-1)
                cv.Rectangle(f,(w-xCutoff[i],0),(w,yCutoff[i]),0,thickness=-1)
                cv.Rectangle(f,(w-xCutoff[i],h-yCutoff[i]),(w,h),0,thickness=-1)         
                i = i+1

            filter = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,3)
            cv.Merge(filterB,filterG,filterR,None,filter)

        scvFilt = Image(filter)
        retVal = self.applyDFTFilter(scvFilt,grayscale)
        return retVal

    def lowPassFilter(self, xCutoff,yCutoff=None,grayscale=False):
        """
        **SUMMARY**

        This method applies a low pass DFT filter. This filter enhances 
        the low frequencies and removes the high frequency signals. This has
        the effect of reducing noise. The frequencies are defined as going between
        0.00 and 1.00 and where 0 is the lowest frequency in the image and 1.0 is
        the highest possible frequencies. Each of the frequencies are defined 
        with respect to the horizontal and vertical signal. This filter 
        isn't perfect and has a harsh cutoff that causes ringing artifacts.

        **PARAMETERS**

        * *xCutoff* - The horizontal frequency at which we perform the cutoff. A separate 
          frequency can be used for the b,g, and r signals by providing a 
          list of values. The frequency is defined between zero to one, 
          where zero is constant component and 1 is the highest possible 
          frequency in the image. 

        * *yCutoff* - The cutoff frequencies in the y direction. If none are provided
          we use the same values as provided for x. 

        * *grayscale* - if this value is True we perfrom the operation on the DFT of the gray
          version of the image and the result is gray image. If grayscale is true
          we perform the operation on each channel and the recombine them to create 
          the result.
                 
        **RETURNS**

        A SimpleCV Image after applying the filter. 

        **EXAMPLE**
        
        >>> img = Image("SimpleCV/sampleimages/RedDog2.jpg")
        >>> img.getDFTLogMagnitude().show()
        >>> lpf = img.highPassFilter([0.2,0.2,0.05])
        >>> lpf.show()
        >>> lpf.getDFTLogMagnitude().show()

        **NOTES**
        
        This filter is far from perfect and will generate a lot of ringing artifacts.
        See: http://en.wikipedia.org/wiki/Ringing_(signal)
        See: http://en.wikipedia.org/wiki/Low-pass_filter
        
        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`
        
        """
        if( isinstance(xCutoff,float) ):    
            xCutoff = [xCutoff,xCutoff,xCutoff]
        if( isinstance(yCutoff,float) ):
            yCutoff = [yCutoff,yCutoff,yCutoff]   
        if(yCutoff is None):
            yCutoff = [xCutoff[0],xCutoff[1],xCutoff[2]] 

        for i in range(0,len(xCutoff)):
            xCutoff[i] = self._boundsFromPercentage(xCutoff[i],self.width)
            yCutoff[i] = self._boundsFromPercentage(yCutoff[i],self.height)

        filter = None
        h  = self.height
        w  = self.width

        if( grayscale ):
            filter = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)            
            cv.Zero(filter)
            #now make all of the corners black
            
            cv.Rectangle(filter,(0,0),(xCutoff[0],yCutoff[0]),255,thickness=-1) #TL
            cv.Rectangle(filter,(0,h-yCutoff[0]),(xCutoff[0],h),255,thickness=-1) #BL
            cv.Rectangle(filter,(w-xCutoff[0],0),(w,yCutoff[0]),255,thickness=-1) #TR
            cv.Rectangle(filter,(w-xCutoff[0],h-yCutoff[0]),(w,h),255,thickness=-1) #BR       

        else:
            #I need to looking into CVMERGE/SPLIT... I would really need to know
            # how much memory we're allocating here
            filterB = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)
            filterG = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)
            filterR = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)
            cv.Zero(filterB)
            cv.Zero(filterG)
            cv.Zero(filterR)
            #now make all of the corners black
            temp = [filterB,filterG,filterR]
            i = 0
            for f in temp:
                cv.Rectangle(f,(0,0),(xCutoff[i],yCutoff[i]),255,thickness=-1)
                cv.Rectangle(f,(0,h-yCutoff[i]),(xCutoff[i],h),255,thickness=-1)
                cv.Rectangle(f,(w-xCutoff[i],0),(w,yCutoff[i]),255,thickness=-1)
                cv.Rectangle(f,(w-xCutoff[i],h-yCutoff[i]),(w,h),255,thickness=-1)         
                i = i+1

            filter = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,3)
            cv.Merge(filterB,filterG,filterR,None,filter)

        scvFilt = Image(filter)
        retVal = self.applyDFTFilter(scvFilt,grayscale)
        return retVal


    #FUCK! need to decide BGR or RGB 
    # ((rx_begin,ry_begin)(gx_begin,gy_begin)(bx_begin,by_begin))
    # or (x,y)
    def bandPassFilter(self, xCutoffLow, xCutoffHigh, yCutoffLow=None, yCutoffHigh=None,grayscale=False):
        """
        **SUMMARY**

        This method applies a simple band pass DFT filter. This filter enhances 
        the a range of frequencies and removes all of the other frequencies. This allows
        a user to precisely select a set of signals to display . The frequencies are 
        defined as going between
        0.00 and 1.00 and where 0 is the lowest frequency in the image and 1.0 is
        the highest possible frequencies. Each of the frequencies are defined 
        with respect to the horizontal and vertical signal. This filter 
        isn't perfect and has a harsh cutoff that causes ringing artifacts.

        **PARAMETERS**

        * *xCutoffLow*  - The horizontal frequency at which we perform the cutoff of the low 
          frequency signals. A separate 
          frequency can be used for the b,g, and r signals by providing a 
          list of values. The frequency is defined between zero to one, 
          where zero is constant component and 1 is the highest possible 
          frequency in the image. 

        * *xCutoffHigh* - The horizontal frequency at which we perform the cutoff of the high 
          frequency signals. Our filter passes signals between xCutoffLow and 
          xCutoffHigh. A separate frequency can be used for the b, g, and r 
          channels by providing a 
          list of values. The frequency is defined between zero to one, 
          where zero is constant component and 1 is the highest possible 
          frequency in the image. 

        * *yCutoffLow* - The low frequency cutoff in the y direction. If none 
          are provided we use the same values as provided for x. 

        * *yCutoffHigh* - The high frequency cutoff in the y direction. If none 
          are provided we use the same values as provided for x. 

        * *grayscale* - if this value is True we perfrom the operation on the DFT of the gray
          version of the image and the result is gray image. If grayscale is true
          we perform the operation on each channel and the recombine them to create 
          the result.
                 
        **RETURNS**

        A SimpleCV Image after applying the filter. 

        **EXAMPLE**
        
        >>> img = Image("SimpleCV/sampleimages/RedDog2.jpg")
        >>> img.getDFTLogMagnitude().show()
        >>> lpf = img.bandPassFilter([0.2,0.2,0.05],[0.3,0.3,0.2])
        >>> lpf.show()
        >>> lpf.getDFTLogMagnitude().show()

        **NOTES**

        This filter is far from perfect and will generate a lot of ringing artifacts.
        
        See: http://en.wikipedia.org/wiki/Ringing_(signal)

        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`
        
        """

        if( isinstance(xCutoffLow,float) ):    
            xCutoffLow = [xCutoffLow,xCutoffLow,xCutoffLow]
        if( isinstance(yCutoffLow,float) ):
            yCutoffLow = [yCutoffLow,yCutoffLow,yCutoffLow]   
        if( isinstance(xCutoffHigh,float) ):    
            xCutoffHigh = [xCutoffHigh,xCutoffHigh,xCutoffHigh]
        if( isinstance(yCutoffHigh,float) ):
            yCutoffHigh = [yCutoffHigh,yCutoffHigh,yCutoffHigh]   

        if(yCutoffLow is None):
            yCutoffLow = [xCutoffLow[0],xCutoffLow[1],xCutoffLow[2]] 
        if(yCutoffHigh is None):
            yCutoffHigh = [xCutoffHigh[0],xCutoffHigh[1],xCutoffHigh[2]]

        for i in range(0,len(xCutoffLow)):
            xCutoffLow[i] = self._boundsFromPercentage(xCutoffLow[i],self.width)
            xCutoffHigh[i] = self._boundsFromPercentage(xCutoffHigh[i],self.width)
            yCutoffHigh[i] = self._boundsFromPercentage(yCutoffHigh[i],self.height)  
            yCutoffLow[i] = self._boundsFromPercentage(yCutoffLow[i],self.height)
  
        filter = None
        h  = self.height
        w  = self.width
        if( grayscale ):
            filter = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)            
            cv.Zero(filter)
            #now make all of the corners black
            cv.Rectangle(filter,(0,0),(xCutoffHigh[0],yCutoffHigh[0]),255,thickness=-1) #TL
            cv.Rectangle(filter,(0,h-yCutoffHigh[0]),(xCutoffHigh[0],h),255,thickness=-1) #BL
            cv.Rectangle(filter,(w-xCutoffHigh[0],0),(w,yCutoffHigh[0]),255,thickness=-1) #TR
            cv.Rectangle(filter,(w-xCutoffHigh[0],h-yCutoffHigh[0]),(w,h),255,thickness=-1) #BR       
            cv.Rectangle(filter,(0,0),(xCutoffLow[0],yCutoffLow[0]),0,thickness=-1) #TL
            cv.Rectangle(filter,(0,h-yCutoffLow[0]),(xCutoffLow[0],h),0,thickness=-1) #BL
            cv.Rectangle(filter,(w-xCutoffLow[0],0),(w,yCutoffLow[0]),0,thickness=-1) #TR
            cv.Rectangle(filter,(w-xCutoffLow[0],h-yCutoffLow[0]),(w,h),0,thickness=-1) #BR       


        else:
            #I need to looking into CVMERGE/SPLIT... I would really need to know
            # how much memory we're allocating here
            filterB = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)
            filterG = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)
            filterR = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,1)
            cv.Zero(filterB)
            cv.Zero(filterG)
            cv.Zero(filterR)
            #now make all of the corners black
            temp = [filterB,filterG,filterR]
            i = 0
            for f in temp:
                cv.Rectangle(f,(0,0),(xCutoffHigh[i],yCutoffHigh[i]),255,thickness=-1) #TL
                cv.Rectangle(f,(0,h-yCutoffHigh[i]),(xCutoffHigh[i],h),255,thickness=-1) #BL
                cv.Rectangle(f,(w-xCutoffHigh[i],0),(w,yCutoffHigh[i]),255,thickness=-1) #TR
                cv.Rectangle(f,(w-xCutoffHigh[i],h-yCutoffHigh[i]),(w,h),255,thickness=-1) #BR       
                cv.Rectangle(f,(0,0),(xCutoffLow[i],yCutoffLow[i]),0,thickness=-1) #TL
                cv.Rectangle(f,(0,h-yCutoffLow[i]),(xCutoffLow[i],h),0,thickness=-1) #BL
                cv.Rectangle(f,(w-xCutoffLow[i],0),(w,yCutoffLow[i]),0,thickness=-1) #TR
                cv.Rectangle(f,(w-xCutoffLow[i],h-yCutoffLow[i]),(w,h),0,thickness=-1) #BR       
                i = i+1

            filter = cv.CreateImage((self.width,self.height),cv.IPL_DEPTH_8U,3)
            cv.Merge(filterB,filterG,filterR,None,filter)

        scvFilt = Image(filter)
        retVal = self.applyDFTFilter(scvFilt,grayscale)
        return retVal





    def _inverseDFT(self,input):
        """
        **SUMMARY**
        **PARAMETERS**
        **RETURNS**
        **EXAMPLE**
        NOTES:
        SEE ALSO:
        """
        # a destructive IDFT operation for internal calls
        w = input[0].width
        h = input[0].height
        if( len(input) == 1 ):
            cv.DFT(input[0], input[0], cv.CV_DXT_INV_SCALE)
            result = cv.CreateImage((w,h), cv.IPL_DEPTH_8U, 1)
            data = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
            blank = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
            cv.Split(input[0],data,blank,None,None)
            min, max, pt1, pt2 = cv.MinMaxLoc(data)
            denom = max-min
            if(denom == 0):
                denom = 1
            cv.Scale(data, data, 1.0/(denom), 1.0*(-min)/(denom))
            cv.Mul(data,data,data,255.0)
            cv.Convert(data,result)
            retVal = Image(result)
        else: # DO RGB separately
            results = []
            data = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
            blank = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
            for i in range(0,len(input)):
                cv.DFT(input[i], input[i], cv.CV_DXT_INV_SCALE)
                result = cv.CreateImage((w,h), cv.IPL_DEPTH_8U, 1)
                cv.Split( input[i],data,blank,None,None)
                min, max, pt1, pt2 = cv.MinMaxLoc(data)
                denom = max-min
                if(denom == 0):
                    denom = 1
                cv.Scale(data, data, 1.0/(denom), 1.0*(-min)/(denom))
                cv.Mul(data,data,data,255.0) # this may not be right
                cv.Convert(data,result)
                results.append(result)
                      
            retVal = cv.CreateImage((w,h),cv.IPL_DEPTH_8U,3)
            cv.Merge(results[0],results[1],results[2],None,retVal)
            retVal = Image(retVal)
        del input
        return retVal

    def InverseDFT(self, raw_dft_image):
        """
        **SUMMARY**

        This method provides a way of performing an inverse discrete Fourier transform 
        on a real/imaginary image pair and obtaining the result as a SimpleCV image. This
        method is helpful if you wish to perform custom filter development. 

        **PARAMETERS**

        * *raw_dft_image* - A list object with either one or three IPL images. Each image should 
          have a 64f depth and contain two channels (the real and the imaginary).
        
        **RETURNS**

        A simpleCV image.

        **EXAMPLE**
        
        Note that this is an example, I don't recommend doing this unless you know what 
        you are doing. 
        
        >>> raw = img.getRawDFT()
        >>> cv.SomeOperation(raw)
        >>> result = img.InverseDFT(raw)
        >>> result.show()

        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`

        """
        input  = []
        w = raw_dft_image[0].width
        h = raw_dft_image[0].height
        if(len(raw_dft_image) == 1):
            gs = cv.CreateImage((w,h),cv.IPL_DEPTH_64F,2)
            cv.Copy(self._DFT[0],gs)
            input.append(gs)
        else:
            for img in raw_dft_image:
                temp = cv.CreateImage((w,h),cv.IPL_DEPTH_64F,2)
                cv.Copy(img,temp)
                input.append(img)
            
        if( len(input) == 1 ):
            cv.DFT(input[0], input[0], cv.CV_DXT_INV_SCALE)
            result = cv.CreateImage((w,h), cv.IPL_DEPTH_8U, 1)
            data = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
            blank = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
            cv.Split(input[0],data,blank,None,None)
            min, max, pt1, pt2 = cv.MinMaxLoc(data)
            denom = max-min
            if(denom == 0):
                denom = 1
            cv.Scale(data, data, 1.0/(denom), 1.0*(-min)/(denom))
            cv.Mul(data,data,data,255.0)
            cv.Convert(data,result)
            retVal = Image(result)
        else: # DO RGB separately
            results = []
            data = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
            blank = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
            for i in range(0,len(raw_dft_image)):
                cv.DFT(input[i], input[i], cv.CV_DXT_INV_SCALE)
                result = cv.CreateImage((w,h), cv.IPL_DEPTH_8U, 1)
                cv.Split( input[i],data,blank,None,None)
                min, max, pt1, pt2 = cv.MinMaxLoc(data)
                denom = max-min
                if(denom == 0):
                    denom = 1
                cv.Scale(data, data, 1.0/(denom), 1.0*(-min)/(denom))
                cv.Mul(data,data,data,255.0) # this may not be right
                cv.Convert(data,result)
                results.append(result)
                      
            retVal = cv.CreateImage((w,h),cv.IPL_DEPTH_8U,3)
            cv.Merge(results[0],results[1],results[2],None,retVal)
            retVal = Image(retVal)

        return retVal
        
    def applyButterworthFilter(self,dia=400,order=2,highpass=False,grayscale=False):
        """
        **SUMMARY**

        Creates a butterworth filter of 64x64 pixels, resizes it to fit
        image, applies DFT on image using the filter.
        Returns image with DFT applied on it
        
        **PARAMETERS**

        * *dia* - int Diameter of Butterworth low pass filter
        * *order* - int Order of butterworth lowpass filter
        * *highpass*: BOOL True: highpass filterm False: lowpass filter
        * *grayscale*: BOOL
    
        **EXAMPLE**
    
        >>> im = Image("lenna")
        >>> img = applyButterworth(im, dia=400,order=2,highpass=True,grayscale=False)
       
        Output image: http://i.imgur.com/5LS3e.png
    
        >>> img = applyButterworth(im, dia=400,order=2,highpass=False,grayscale=False)
        
        Output img: http://i.imgur.com/QlCAY.png
    
        >>> im = Image("grayscale_lenn.png") #take image from here: http://i.imgur.com/O0gZn.png
        >>> img = applyButterworth(im, dia=400,order=2,highpass=True,grayscale=True)
        
        Output img: http://i.imgur.com/BYYnp.png
    
        >>> img = applyButterworth(im, dia=400,order=2,highpass=False,grayscale=True)
        
        Output img: http://i.imgur.com/BYYnp.png

        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`
        
        """
        w,h = self.size()
        flt = cv.CreateImage((64,64),cv.IPL_DEPTH_8U,1)
        dia = int(dia/((w/64.0+h/64.0)/2.0))
        if highpass:
            for i in range(64):
                for j in range(64):
                    d = sqrt((j-32)**2+(i-32)**2)
                    flt[i,j] = 255-(255/(1+(d/dia)**(order*2)))
        else:
            for i in range(64):
                for j in range(64):
                    d = sqrt((j-32)**2+(i-32)**2)
                    flt[i,j] = 255/(1+(d/dia)**(order*2))
    
        flt = Image(flt)
        flt_re = flt.resize(w,h)
        img = self.applyDFTFilter(flt_re,grayscale)
        return img
    
    def applyGaussianFilter(self, dia=400, highpass=False, grayscale=False):
        """
        **SUMMARY**

        Creates a gaussian filter of 64x64 pixels, resizes it to fit
        image, applies DFT on image using the filter.
        Returns image with DFT applied on it
        
        **PARAMETERS**

        * *dia* -  int - diameter of Gaussian filter
        * *highpass*: BOOL True: highpass filter False: lowpass filter
        * *grayscale*: BOOL
    
        **EXAMPLE**
    
        >>> im = Image("lenna")
        >>> img = applyGaussianfilter(im, dia=400,highpass=True,grayscale=False)
   
        Output image: http://i.imgur.com/DttJv.png
    
        >>> img = applyGaussianfilter(im, dia=400,highpass=False,grayscale=False)
        
        Output img: http://i.imgur.com/PWn4o.png
    
        >>> im = Image("grayscale_lenn.png") #take image from here: http://i.imgur.com/O0gZn.png
        >>> img = applyGaussianfilter(im, dia=400,highpass=True,grayscale=True)
        
        Output img: http://i.imgur.com/9hX5J.png
    
        >>> img = applyGaussianfilter(im, dia=400,highpass=False,grayscale=True)
        
        Output img: http://i.imgur.com/MXI5T.png
        
        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`

        """
        w,h = self.size()
        flt = cv.CreateImage((64,64),cv.IPL_DEPTH_8U,1)
        dia = int(dia/((w/64.0+h/64.0)/2.0))
        if highpass:
            for i in range(64):
                for j in range(64):
                    d = sqrt((j-32)**2+(i-32)**2)
                    val = 255-(255.0*math.exp(-(d**2)/((dia**2)*2)))
                    flt[i,j]=val
        else:
            for i in range(64):
                for j in range(64):
                    d = sqrt((j-32)**2+(i-32)**2)
                    val = 255.0*math.exp(-(d**2)/((dia**2)*2))
                    flt[i,j]=val        
                
        flt = Image(flt)
        flt_re = flt.resize(w,h)
        img = self.applyDFTFilter(flt_re,grayscale)
        return img
        
    def applyUnsharpMask(self,boost=1,dia=400,grayscale=False):
        """
        **SUMMARY**

        This method applies unsharp mask or highboost filtering
        on image depending upon the boost value provided.
        DFT is applied on image using gaussian lowpass filter.
        A mask is created subtracting the DFT image from the original
        iamge. And then mask is added in the image to sharpen it.
        unsharp masking => image + mask
        highboost filtering => image + (boost)*mask
        
        **PARAMETERS**
    
        * *boost* - int  boost = 1 => unsharp masking, boost > 1 => highboost filtering
        * *dia* - int Diameter of Gaussian low pass filter
        * *grayscale* - BOOL
    
        **EXAMPLE**

        Gaussian Filters:
        
        >>> im = Image("lenna")
        >>> img = applyUnsharpMask(im,2,grayscale=False) #highboost filtering
        
        output image: http://i.imgur.com/A1pZf.png
        
        >>> img = applyUnsharpMask(im,1,grayscale=False) #unsharp masking
        
        output image: http://i.imgur.com/smCdL.png
        
        >>> im = Image("grayscale_lenn.png") #take image from here: http://i.imgur.com/O0gZn.png
        >>> img = applyUnsharpMask(im,2,grayscale=True) #highboost filtering
        
        output image: http://i.imgur.com/VtGzl.png
        
        >>> img = applyUnsharpMask(im,1,grayscale=True) #unsharp masking
        
        output image: http://i.imgur.com/bywny.png
        
        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`

        """
        if boost < 0:
            print "boost >= 1"
            return None
    
        lpIm = self.applyGaussianFilter(dia=dia,grayscale=grayscale,highpass=False)
        im = Image(self.getBitmap())
        mask = im - lpIm
        img = im
        for i in range(boost):
            img = img + mask
        return img

    def listHaarFeatures(self):
        '''
        This is used to list the built in features available for HaarCascade feature
        detection.  Just run this function as:

        >>> img.listHaarFeatures()

        Then use one of the file names returned as the input to the findHaarFeature()
        function.  So you should get a list, more than likely you will see face.xml,
        to use it then just

        >>> img.findHaarFeatures('face.xml')
        '''
        
        features_directory = os.path.join(LAUNCH_PATH, 'Features','HaarCascades')
        features = os.listdir(features_directory)
        print features

    def _CopyAvg(self, src, dst,roi, levels, levels_f, mode):
        '''
        Take the value in an ROI, calculate the average / peak hue
        and then set the output image roi to the value. 
        '''

        if( mode ): # get the peak hue for an area
            h = src[roi[0]:roi[0]+roi[2],roi[1]:roi[1]+roi[3]].hueHistogram()
            myHue = np.argmax(h)
            C = (float(myHue),float(255),float(255),float(0))
            cv.SetImageROI(dst,roi)
            cv.AddS(dst,c,dst)
            cv.ResetImageROI(dst)
        else: # get the average value for an area optionally set levels
            cv.SetImageROI(src.getBitmap(),roi)
            cv.SetImageROI(dst,roi)
            avg = cv.Avg(src.getBitmap())
            avg = (float(avg[0]),float(avg[1]),float(avg[2]),0)
            if(levels is not None):
                avg = (int(avg[0]/levels)*levels_f,int(avg[1]/levels)*levels_f,int(avg[2]/levels)*levels_f,0)                   
            cv.AddS(dst,avg,dst)
            cv.ResetImageROI(src.getBitmap())
            cv.ResetImageROI(dst)

    def pixelize(self, block_size = 10, region = None, levels=None, doHue=False):
        """
        **SUMMARY**

        Pixelation blur, like the kind used to hide naughty bits on your favorite tv show. 

        **PARAMETERS**

        * *block_size* - the blur block size in pixels, an integer is an square blur, a tuple is rectangular.
        * *region* - do the blur in a region in format (x_position,y_position,width,height)
        * *levels* - the number of levels per color channel. This makes the image look like an 8-bit video game.
        * *doHue* - If this value is true we calculate the peak hue for the area, not the 
          average color for the area. 
        
        **RETURNS**
        
        Returns the image with the pixelation blur applied. 

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> result = img.pixelize( 16, (200,180,250,250), levels=4)
        >>> img.show()

        """

        if( isinstance(block_size, int) ):
            block_size = (block_size,block_size)

        
        retVal = self.getEmpty()
        

        levels_f = 0.00
        if( levels is not None ):
            levels = 255/int(levels)
            if(levels <= 1 ):
                levels = 2
            levels_f = float(levels)

        if( region is not None ):
            cv.Copy(self.getBitmap(), retVal)
            cv.SetImageROI(retVal,region)
            cv.Zero(retVal)
            cv.ResetImageROI(retVal)
            xs = region[0]
            ys = region[1]
            w = region[2]
            h = region[3]
        else:
            xs = 0
            ys = 0
            w = self.width
            h = self.height

        #if( region is None ):
        hc = w / block_size[0] #number of horizontal blocks
        vc = h / block_size[1] #number of vertical blocks
        #when we fit in the blocks, we're going to spread the round off
        #over the edges 0->x_0, 0->y_0  and x_0+hc*block_size
        x_lhs = int(np.ceil(float(w%block_size[0])/2.0)) # this is the starting point
        y_lhs = int(np.ceil(float(h%block_size[1])/2.0))
        x_rhs = int(np.floor(float(w%block_size[0])/2.0)) # this is the starting point
        y_rhs = int(np.floor(float(h%block_size[1])/2.0))
        x_0 = xs+x_lhs
        y_0 = ys+y_lhs
        x_f = (x_0+(block_size[0]*hc)) #this would be the end point
        y_f = (y_0+(block_size[1]*vc))

        for i in range(0,hc):
            for j in range(0,vc):
                xt = x_0+(block_size[0]*i)
                yt = y_0+(block_size[1]*j)
                roi = (xt,yt,block_size[0],block_size[1])
                self._CopyAvg(self,retVal,roi,levels,levels_f,doHue)


        if( x_lhs > 0 ): # add a left strip
            xt = xs 
            wt = x_lhs 
            ht = block_size[1]
            for j in range(0,vc):
                yt = y_0+(j*block_size[1])
                roi = (xt,yt,wt,ht)
                self._CopyAvg(self,retVal,roi,levels,levels_f,doHue)
                

        if( x_rhs > 0 ): # add a right strip
            xt = (x_0+(block_size[0]*hc))
            wt = x_rhs 
            ht = block_size[1]
            for j in range(0,vc):
                yt = y_0+(j*block_size[1])
                roi = (xt,yt,wt,ht)
                self._CopyAvg(self,retVal,roi,levels,levels_f,doHue)

        if( y_lhs > 0 ): # add a left strip
            yt = ys
            ht = y_lhs 
            wt = block_size[0]
            for i in range(0,hc):
                xt = x_0+(i*block_size[0])
                roi = (xt,yt,wt,ht)
                self._CopyAvg(self,retVal,roi,levels,levels_f,doHue)
                
        if( y_rhs > 0 ): # add a right strip
            yt = (y_0+(block_size[1]*vc)) 
            ht = y_rhs
            wt = block_size[0]
            for i in range(0,hc):
                xt = x_0+(i*block_size[0])
                roi = (xt,yt,wt,ht)
                self._CopyAvg(self,retVal,roi,levels,levels_f,doHue)

        #now the corner cases
        if(x_lhs > 0 and y_lhs > 0 ):
            roi = (xs,ys,x_lhs,y_lhs)
            self._CopyAvg(self,retVal,roi,levels,levels_f,doHue)

        if(x_rhs > 0 and y_rhs > 0 ):
            roi = (x_f,y_f,x_rhs,y_rhs)
            self._CopyAvg(self,retVal,roi,levels,levels_f,doHue)

        if(x_lhs > 0 and y_rhs > 0 ):
            roi = (xs,y_f,x_lhs,y_rhs)
            self._CopyAvg(self,retVal,roi,levels,levels_f,doHue)

        if(x_rhs > 0 and y_lhs > 0 ):
            roi = (x_f,ys,x_rhs,y_lhs)
            self._CopyAvg(self,retVal,roi,levels,levels_f,doHue)
            
        if(doHue):
            cv.CvtColor(retVal,retVal,cv.CV_HSV2BGR)


        return Image(retVal)

    def anonymize(self, block_size=10, features=None, transform=None):
        """
        **SUMMARY**

        Anonymize, for additional privacy to images.

        **PARAMETERS**

        * *features* - A list with the Haar like feature cascades that should be matched.
        * *block_size* - The size of the blocks for the pixelize function.
        * *transform* - A function, to be applied to the regions matched instead of pixelize.
        * This function must take two arguments: the image and the region it'll be applied to,
        * as in region = (x, y, width, height).

        **RETURNS**

        Returns the image with matching regions pixelated.

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> anonymous = img.anonymize()
        >>> anonymous.show()

        >>> def my_function(img, region):
        >>>     x, y, width, height = region
        >>>     img = img.crop(x, y, width, height)
        >>>     return img
        >>>
        >>>img = Image("lenna")
        >>>transformed = img.anonymize(transform = my_function)

        """

        regions = []

        if features is None:
            regions.append(self.findHaarFeatures("face"))
            regions.append(self.findHaarFeatures("profile"))
        else:
            for feature in features:
                regions.append(self.findHaarFeatures(feature))

        found = [f for f in regions if f is not None]

        img = self.copy()

        if found:
            for feature_set in found:
                for region in feature_set:
                    rect = (region.topLeftCorner()[0], region.topLeftCorner()[1],
                            region.width(), region.height())
                    if transform is None:
                        img = img.pixelize(block_size=block_size, region=rect)
                    else:
                        img = transform(img, rect)

        return img
                    
    def edgeIntersections(self, pt0, pt1, width=1, canny1=0, canny2=100):
        """
        **SUMMARY** 
        
        Find the outermost intersection of a line segment and the edge image and return
        a list of the intersection points. If no intersections are found the method returns
        an empty list. 
        
        **PARAMETERS**
        
        * *pt0* - an (x,y) tuple of one point on the intersection line.
        * *pt1* - an (x,y) tuple of the second point on the intersection line.
        * *width* - the width of the line to use. This approach works better when
                    for cases where the edges on an object are not always closed 
                    and may have holes.
        * *canny1* - the lower bound of the Canny edge detector parameters.
        * *canny2* - the upper bound of the Canny edge detector parameters.

        **RETURNS**
        
        A list of two (x,y) tuples or an empty list.

        **EXAMPLE**

        >>> img = Image("SimpleCV")
        >>> a = (25,100)
        >>> b = (225,110)
        >>> pts = img.edgeIntersections(a,b,width=3)
        >>> e = img.edges(0,100)
        >>> e.drawLine(a,b,color=Color.RED)
        >>> e.drawCircle(pts[0],10,color=Color.GREEN)
        >>> e.drawCircle(pts[1],10,color=Color.GREEN)
        >>> e.show()

        img = Image("SimpleCV")
        a = (25,100)
        b = (225,100)
        pts = img.edgeIntersections(a,b,width=3)
        e = img.edges(0,100)
        e.drawLine(a,b,color=Color.RED)
        e.drawCircle(pts[0],10,color=Color.GREEN)
        e.drawCircle(pts[1],10,color=Color.GREEN)
        e.show()


        """
        w = abs(pt0[0]-pt1[0])
        h = abs(pt0[1]-pt1[1])
        x = np.min([pt0[0],pt1[0]])
        y = np.min([pt0[1],pt1[1]])
        if( w <= 0 ):
            w = width
            x = np.clip(x-(width/2),0,x-(width/2))
        if( h <= 0 ):
            h = width 
            y = np.clip(y-(width/2),0,y-(width/2))
        #got some corner cases to catch here
        p0p = np.array([(pt0[0]-x,pt0[1]-y)])
        p1p = np.array([(pt1[0]-x,pt1[1]-y)])
        edges = self.crop(x,y,w,h)._getEdgeMap(canny1, canny2)
        line = cv.CreateImage((w,h),cv.IPL_DEPTH_8U,1)
        cv.Zero(line)
        cv.Line(line,((pt0[0]-x),(pt0[1]-y)),((pt1[0]-x),(pt1[1]-y)),cv.Scalar(255.00),width,8)
        cv.Mul(line,edges,line)
        intersections = uint8(np.array(cv.GetMat(line)).transpose())
        (xs,ys) = np.where(intersections==255)
        points = zip(xs,ys)
        if(len(points)==0):
            return [None,None]
        A = np.argmin(spsd.cdist(p0p,points,'cityblock'))
        B = np.argmin(spsd.cdist(p1p,points,'cityblock'))
        ptA = (int(xs[A]+x),int(ys[A]+y))
        ptB = (int(xs[B]+x),int(ys[B]+y))
        # we might actually want this to be list of all the points
        return [ptA, ptB]          


    def fitContour(self, initial_curve, window=(11,11), params=(0.1,0.1,0.1),doAppx=True,appx_level=1):
        """
        **SUMMARY** 
        
        This method tries to fit a list of points to lines in the image. The list of points 
        is a list of (x,y) tuples that are near (i.e. within the window size) of the line
        you want to fit in the image. This method uses a binary such as the result of calling
        edges. 

        This method is based on active contours. Please see this reference:
        http://en.wikipedia.org/wiki/Active_contour_model

        **PARAMETERS**
        
        * *initial_curve* - region of the form [(x0,y0),(x1,y1)...] that are the initial conditions to fit. 
        * *window* - the search region around each initial point to look for a solution.
        * *params* - The alpha, beta, and gamma parameters for the active contours 
          algorithm as a list [alpha,beta,gamma]. 
        * *doAppx* - post process the snake into a polynomial approximation. Basically
          this flag will clean up the output of the contour algorithm. 
        * *appx_level* - how much to approximate the snake, higher numbers mean more approximation. 

        **DISCUSSION**
        
        THIS SECTION IS QUOTED FROM: http://users.ecs.soton.ac.uk/msn/book/new_demo/Snakes/
        There are three components to the Energy Function:

        * Continuity
        * Curvature
        * Image (Gradient)
        Each Weighted by Specified Parameter:
        
        Total Energy = Alpha*Continuity + Beta*Curvature + Gamma*Image

        Choose different values dependent on Feature to extract:
        
        * Set alpha high if there is a deceptive Image Gradient
        * Set beta  high if smooth edged Feature, low if sharp edges
        * Set gamma high if contrast between Background and Feature is low


        **RETURNS**
        
        A list of (x,y) tuples that approximate the curve. If you do not use
        approximation the list should be the same length as the input list length.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> edges = img.edges(t1=120,t2=155)
        >>> guess = [(311,284),(313,270),(320,259),(330,253),(347,245)]
        >>> result = edges.fitContour(guess)
        >>> img.drawPoints(guess,color=Color.RED)
        >>> img.drawPoints(result,color=Color.GREEN)
        >>> img.show()

        """
        alpha = [params[0]]
        beta= [params[1]]
        gamma = [params[2]]
        if( window[0]%2 == 0 ):
            window = (window[0]+1,window[1])
            logger.warn("Yo dawg, just a heads up, snakeFitPoints wants an odd window size. I fixed it for you, but you may want to take a look at your code.")
        if( window[1]%2 == 0 ):
            window = (window[0],window[1]+1)
            logger.warn("Yo dawg, just a heads up, snakeFitPoints wants an odd window size. I fixed it for you, but you may want to take a look at your code.")
        raw = cv.SnakeImage(self._getGrayscaleBitmap(),initial_curve,alpha,beta,gamma,window,(cv.CV_TERMCRIT_ITER,10,0.01))
        if( doAppx ):
            try:
                import cv2
            except:
                logger.warning("Can't Do snakeFitPoints without OpenCV >= 2.3.0")
                return
            appx = cv2.approxPolyDP(np.array([raw],'float32'),appx_level,True)      
            retVal = []
            for p in appx:
                retVal.append((int(p[0][0]),int(p[0][1])))
        else:
            retVal = raw

        return retVal

    def fitLines(self,guesses,window=10,threshold=128):
        """
        **SUMMARY**
        
        Fit lines in a binary/gray image using an initial guess and the least squares method.
        The lines are returned as a line feature set. 

        **PARAMETERS**

        * *guesses* - A list of tuples of the form ((x0,y0),(x1,y1)) where each of the lines
          is an approximate guess.
        * *window* - A window around the guess to search.
        * *threshold* - the threshold above which we count a pixel as a line 

        **RETURNS**

        A feature set of line features, one per guess. 

        **EXAMPLE**
        

        >>> img = Image("lsq.png")
        >>> guesses = [((313,150),(312,332)),((62,172),(252,52)),((102,372),(182,182)),((372,62),(572,162)),((542,362),(462,182)),((232,412),(462,423))]
        >>> l = img.fitLines(guesses,window=10) 
        >>> l.draw(color=Color.RED,width=3)
        >>> for g in guesses:
        >>>    img.drawLine(g[0],g[1],color=Color.YELLOW)
            
        >>> img.show()
        """
   
        retVal = FeatureSet()
        i =0 
        for g in guesses:
            # Guess the size of the crop region from the line guess and the window. 
            ymin = np.min([g[0][1],g[1][1]])
            ymax = np.max([g[0][1],g[1][1]])
            xmin = np.min([g[0][0],g[1][0]])
            xmax = np.max([g[0][0],g[1][0]])

            xminW = np.clip(xmin-window,0,self.width)
            xmaxW = np.clip(xmax+window,0,self.width)
            yminW = np.clip(ymin-window,0,self.height)
            ymaxW = np.clip(ymax+window,0,self.height)            
            temp = self.crop(xminW,yminW,xmaxW-xminW,ymaxW-yminW)
            temp = temp.getGrayNumpy()
            
            # pick the lines above our threshold
            x,y = np.where(temp>threshold)
            pts = zip(x,y)
            gpv = np.array([float(g[0][0]-xminW),float(g[0][1]-yminW)])
            gpw = np.array([float(g[1][0]-xminW),float(g[1][1]-yminW)])
            def lineSegmentToPoint(p):
                w = gpw
                v = gpv
                #print w,v
                p = np.array([float(p[0]),float(p[1])])
                l2 = np.sum((w-v)**2)
                t = float(np.dot((p-v),(w-v))) / float(l2)
                if( t < 0.00 ):
                    return np.sqrt(np.sum((p-v)**2))
                elif(t > 1.0):
                    return np.sqrt(np.sum((p-w)**2))
                else:
                    project = v + (t*(w-v))
                    return np.sqrt(np.sum((p-project)**2))
            # http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment

            distances = np.array(map(lineSegmentToPoint,pts))
            closepoints = np.where(distances<window)[0]
            
            pts = np.array(pts)

            if( len(closepoints) < 3 ):
                    continue

            good_pts = pts[closepoints]
            good_pts = good_pts.astype(float)


            x = good_pts[:,0]
            y = good_pts[:,1]
            # do the shift from our crop
            # generate the line values 
            x = x + xminW
            y = y + yminW

            ymin = np.min(y)
            ymax = np.max(y)
            xmax = np.max(x)
            xmin = np.min(x)

            if( (xmax-xmin) > (ymax-ymin) ):
                # do the least squares
                A = np.vstack([x,np.ones(len(x))]).T
                m,c = nla.lstsq(A,y)[0]
                y0 = int(m*xmin+c)
                y1 = int(m*xmax+c)
                retVal.append(Line(self,((xmin,y0),(xmax,y1))))
            else:
                # do the least squares
                A = np.vstack([y,np.ones(len(y))]).T
                m,c = nla.lstsq(A,x)[0]
                x0 = int(ymin*m+c)
                x1 = int(ymax*m+c)
                retVal.append(Line(self,((x0,ymin),(x1,ymax))))

        return retVal

    def fitLinePoints(self,guesses,window=(11,11), samples=20,params=(0.1,0.1,0.1)):
        """
        **DESCRIPTION**

        This method uses the snakes / active contour approach in an attempt to
        fit a series of points to a line that may or may not be exactly linear. 

        **PARAMETERS**
        
        * *guesses* - A set of lines that we wish to fit to. The lines are specified 
          as a list of tuples of (x,y) tuples. E.g. [((x0,y0),(x1,y1))....]
        * *window* - The search window in pixels for the active contours approach.
        * *samples* - The number of points to sample along the input line, 
          these are the initial conditions for active contours method. 
        * *params* - the alpha, beta, and gamma values for the active contours routine.

        **RETURNS**

        A list of fitted contour points. Each contour is a list of (x,y) tuples. 

        **EXAMPLE**
        
        >>> img = Image("lsq.png")
        >>> guesses = [((313,150),(312,332)),((62,172),(252,52)),((102,372),(182,182)),((372,62),(572,162)),((542,362),(462,182)),((232,412),(462,423))]
        >>> r = img.fitLinePoints(guesses) 
        >>> for rr in r:
        >>>    img.drawLine(rr[0],rr[1],color=Color.RED,width=3)
        >>> for g in guesses:
        >>>    img.drawLine(g[0],g[1],color=Color.YELLOW)
            
        >>> img.show()
        
        """
        pts = []
        for g in guesses:
            #generate the approximation
            bestGuess = []
            dx = float(g[1][0]-g[0][0])
            dy = float(g[1][1]-g[0][1])
            l = np.sqrt((dx*dx)+(dy*dy))
            if( l <= 0 ):
                logger.warning("Can't Do snakeFitPoints without OpenCV >= 2.3.0")
                return 

            dx = dx/l 
            dy = dy/l
            for i in range(-1,samples+1):
                t = i*(l/samples)
                bestGuess.append((int(g[0][0]+(t*dx)),int(g[0][1]+(t*dy))))
            # do the snake fitting 
            appx = self.fitContour(bestGuess,window=window,params=params,doAppx=False)
            pts.append(appx)

        return pts
        


    def drawPoints(self, pts, color=Color.RED, sz=3, width=-1):
        """
        **DESCRIPTION**

        A quick and dirty points rendering routine.

        **PARAMETERS**
        
        * *pts* - pts a list of (x,y) points. 
        * *color* - a color for our points.
        * *sz* - the circle radius for our points.
        * *width* - if -1 fill the point, otherwise the size of point border

        **RETURNS**

        None - This is an inplace operation. 

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> img.drawPoints([(10,10),(30,30)])
        >>> img.show()
        """
        for p in pts:
           self.drawCircle(p,sz,color,width)
        return None
        
    def sobel(self, xorder=1, yorder=1, doGray=True, aperture=5, aperature=None):
        """
        **DESCRIPTION**

        Sobel operator for edge detection

        **PARAMETERS**
        
        * *xorder* - int - Order of the derivative x.
        * *yorder* - int - Order of the derivative y.
        * *doGray* - Bool - grayscale or not.
        * *aperture* - int - Size of the extended Sobel kernel. It must be 1, 3, 5, or 7.

        **RETURNS**

        Image with sobel opeartor applied on it

        **EXAMPLE**

        >>> img = Image("lenna")
        >>> s = img.sobel()
        >>> s.show()
        """
        aperture = aperature if aperature else aperture
        retVal = None
        try:
            import cv2
        except:
            logger.warning("Can't do Sobel without OpenCV >= 2.3.0")
            return None

        if( aperture != 1 and aperture != 3 and aperture != 5 and aperture != 7 ):
            logger.warning("Bad Sobel Aperture, values are [1,3,5,7].")
            return None

        if( doGray ):
            dst = cv2.Sobel(self.getGrayNumpy(),cv2.cv.CV_32F,xorder,yorder,ksize=aperture)
            minv = np.min(dst)
            maxv = np.max(dst)
            cscale = 255/(maxv-minv)
            shift =  -1*(minv)

            t = np.zeros(self.size(),dtype='uint8')
            t = cv2.convertScaleAbs(dst,t,cscale,shift/255.0)
            retVal = Image(t)
            
        else:
            layers = self.splitChannels(grayscale=False)
            sobel_layers = []
            for layer in layers:
                dst = cv2.Sobel(layer.getGrayNumpy(),cv2.cv.CV_32F,xorder,yorder,ksize=aperture)
            
                minv = np.min(dst)
                maxv = np.max(dst)
                cscale = 255/(maxv-minv)
                shift =  -1*(minv)

                t = np.zeros(self.size(),dtype='uint8')
                t = cv2.convertScaleAbs(dst,t,cscale,shift/255.0)
                sobel_layers.append(Image(t))
            b,g,r = sobel_layers
            
            retVal = self.mergeChannels(b,g,r)
        return retVal
        
    def track(self, method="CAMShift", ts=None, img=None, bb=None, num_frames=3):
        """
        **DESCRIPTION**

        Tracking the object surrounded by the bounding box in the given
        image or TrackSet.

        **PARAMETERS**
        
        * *method* - str - The Tracking Algorithm to be applied
                          * "CAMShift"
        * *ts* - TrackSet - SimpleCV.Features.TrackSet.
        * *img* - Image - Image to be tracked.
                - list - List of Images to be tracked.
        * *bb* - tuple - Bounding Box tuple (x, y, w, h)
        * *num_frames* - int - Number of previous frames to be used for 
                               Forward Backward Error

        **RETURNS**

        SimpleCV.Features.TrackSet
        
        Returns a TrackSet with all the necessary attributes.

        **HOW TO**

        >>> ts = img.track("camshift", img1, bb)
        # Here TrackSet is returned. img, bb, new bb, and other 
        # necessary attributes will be included in the trackset.
        # After getting the trackset you need not provide the bounding box
        # or image. You provide TrackSet as parameter to track().
        # Bounding box and image will be taken from the trackset.
        # So. now
        >>> ts = new_img.track("camshift",ts, num_frames = 4)
        
        # The new Tracking feature will be appended to the give trackset
        # and that will be returned.
        # So, to use it in loop
        ==========================================================
        
        img = cam.getImage()
        bb = (img.width/4,img.height/4,img.width/4,img.height/4)
        ts = img.track( img=img, bb=bb)
        while (True):
            img = cam.getImage()
            ts = img.track(ts)
        
        ==========================================================
        ts = []
        while (some_condition_here):
            img = cam.getImage()
            ts = img.track("camshift",ts,img0,bb)
            # now here in first loop iteration since ts is empty,
            # img0 and bb will be considered.
            # New tracking object will be created and added in ts (TrackSet)
            # After first iteration, ts is not empty and hence the previous
            # image frames and bounding box will be taken from ts and img0
            # and bb will be ignored.
        ==========================================================
        # Instead of loop, give a list of images to be tracked.

        ts = []
        imgs = [img1, img2, img3, ..., imgN]
        ts = img0.track("camshift", ts, imgs, bb)
        ts.drawPath()
        ts[-1].image.show()
        ==========================================================
        """
        if not ts and not img:
            print "Inavlid. Must provide FeatureSet or Image"
            return None
        
        if not ts and not bb:
            print "Inavlid. Must provide Bounding Box with Image"
            return None
            
        if not ts:
            ts = TrackSet()
        else:
            img = ts[-1].image
            bb = ts[-1].bb
        try:
            import cv2
        except ImportError:
            print "Tracking is available for OpenCV >= 2.3"
            return None
            
        if type(img) == list:
            ts = self.track(method, ts, img[0], bb, num_frames)
            for i in img:
                ts = i.track(method, ts, num_frames=num_frames)
            return ts
        
        if method.lower() == "camshift":
            hsv = self.toHSV().getNumpyCv2()
            mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
            x0, y0, w, h = bb
            x1 = x0 + w -1
            y1 = y0 + h -1
            hsv_roi = hsv[y0:y1, x0:x1]
            mask_roi = mask[y0:y1, x0:x1]
            hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
            cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX);
            hist_flat = hist.reshape(-1)
            imgs = [hsv]
            if len(ts) > num_frames and num_frames > 1:
                for feat in ts[-num_frames:]:
                    imgs.append(feat.image.toHSV().getNumpyCv2())
            else:
                imgs.append(img.toHSV().getNumpyCv2())
                    
            prob = cv2.calcBackProject(imgs, [0], hist_flat, [0, 180], 1)
            prob &= mask
            term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
            new_ellipse, track_window = cv2.CamShift(prob, bb, term_crit)
            ts.append(CAMShift(self, track_window, new_ellipse))
            return ts

    def __getstate__(self):
        return dict( size = self.size(), colorspace = self._colorSpace, image = self.applyLayers().getBitmap().tostring() )
        
    def __setstate__(self, mydict):        
        self._bitmap = cv.CreateImageHeader(mydict['size'], cv.IPL_DEPTH_8U, 3)
        cv.SetData(self._bitmap, mydict['image'])
        self._colorSpace = mydict['colorspace']

    def area(self):
      '''
      Returns the area of the Image.
      '''

      return self.width * self.height

    def _get_header_anim(self):
        """ Animation header. To replace the getheader()[0] """
        bb = "GIF89a"
        bb += int_to_bin(self.size()[0])
        bb += int_to_bin(self.size()[1])
        bb += "\x87\x00\x00"
        return bb


Image.greyscale = Image.grayscale


from SimpleCV.Features import FeatureSet, Feature, Barcode, Corner, HaarFeature, Line, Chessboard, TemplateMatch, BlobMaker, Circle, KeyPoint, Motion, KeypointMatch, CAMShift, TrackSet
from SimpleCV.Stream import JpegStreamer
from SimpleCV.Font import *
from SimpleCV.DrawingLayer import *
