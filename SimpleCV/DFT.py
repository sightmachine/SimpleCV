from SimpleCV.base import np, warnings
from SimpleCV.ImageClass import Image

class DFT:
    """
    **SUMMARY**

    The DFT class is the refactored class to crate DFT filters which can
    be used to filter images by applying Digital Fourier Transform. This
    is a factory class to create various DFT filters.

    **PARAMETERS**

    Any of the following parameters can be supplied to create 
    a simple DFT object.

    * *width*        - width of the filter
    * *height*       - height of the filter
    * *channels*     - number of channels of the filter
    * *size*         - size of the filter (width, height)
    * *_numpy*       - numpy array of the filter
    * *_image*       - SimpleCV.Image of the filter
    * *_dia*         - diameter of the filter 
                      (applicable for gaussian, butterworth, notch)
    * *_type*        - Type of the filter 
    * *_order*       - order of the butterworth filter 
    * *_freqpass*    - frequency of the filter (lowpass, highpass, bandpass)
    * *_xCutoffLow*  - Lower horizontal cut off frequency for lowpassfilter
    * *_yCutoffLow*  - Lower vertical cut off frequency for lowpassfilter
    * *_xCutoffHigh* - Upper horizontal cut off frequency for highpassfilter
    * *_yCutoffHigh* - Upper vertical cut off frequency for highassfilter
    


    **EXAMPLE**

    >>> gauss = DFT.createGaussianFilter(dia=40, size=(512,512))
    
    >>> dft = DFT()
    >>> butterworth = dft.createButterworthFilter(dia=300, order=2, size=(300, 300))

    """
    width = 0
    height = 0
    channels = 1
    _numpy = None
    _image = None
    _dia = 0
    _type = ""
    _order = 0
    _freqpass = ""
    _xCutoffLow = 0
    _yCutoffLow = 0
    _xCutoffHigh = 0
    _yCutoffHigh = 0

    def __init__(self, **kwargs):
        for key in kwargs:
            if key == 'width':
                self.width = kwargs[key]
            elif key == 'height':
                self.height = kwargs[key]
            elif key == 'channels':
                self.channels = kwargs[key]
            elif key == 'size':
                self.width, self.height = kwargs[key]
            elif key == 'numpyarray':
                self._numpy = kwargs[key]
            elif key == 'image':
                self._image = kwargs[key]
            elif key == 'dia':
                self._dia = kwargs[key]
            elif key == 'type':
                self._type = kwargs[key]
            elif key == 'order':
                self._order = kwargs[key]
            elif key == 'frequency':
                self._freqpass = kwargs[key]
            elif key == 'xCutoffLow':
                self._xCutoffLow = kwargs[key]
            elif key == 'yCutoffLow':
                self._yCutoffLow = kwargs[key]
            elif key == 'xCutoffHigh':
                self._xCutoffHigh = kwargs[key]
            elif key == 'yCutoffHigh':
                self._yCutoffHigh = kwargs[key]

    def __repr__(self):
        return "<SimpleCV.DFT Object: %s %s filter of size:(%d, %d) and channels: %d>" %(self._type, self._freqpass, self.width, self.height, self.channels)

    def __add__(self, flt):
        if not isinstance(flt, type(self)):
            warnings.warn("Provide SimpleCV.DFT object")
            return None
        if self.size() != flt.size():
            warnings.warn("Both SimpleCV.DFT object must have the same size")
            return None
        flt_numpy = self._numpy + flt._numpy
        flt_image = Image(flt_numpy)
        retVal = DFT(numpyarray=flt_numpy, image=flt_image, size=flt_image.size())
        return retVal

    def __invert__(self, flt):
        return self.invert()

    def _updateParams(self, flt):
        self.channels = flt.channels
        self._dia = flt._dia
        self._type = flt._type
        self._order = flt._order
        self._freqpass = flt._freqpass
        self._xCutoffLow = flt._xCutoffLow
        self._yCutoffLow = flt._yCutoffLow
        self._xCutoffHigh = flt._xCutoffHigh
        self._yCutoffHigh = flt._yCutoffHigh

    def invert(self):
        """
        **SUMMARY**

        Invert the filter. All values will be subtracted from 255.

        **RETURNS**

        Inverted Filter

        **EXAMPLE**

        >>> flt = DFT.createGaussianFilter()
        >>> invertflt = flt.invert()
        """

        flt = self._numpy
        flt = 255 - flt
        img = Image(flt)
        invertedfilter = DFT(numpyarray=flt, image=img,
                             size=self.size(), type=self._type)
        invertedfilter._updateParams(self)
        return invertedfilter

    @classmethod
    def createGaussianFilter(self, dia=400, size=(64, 64), highpass=False):
        """
        **SUMMARY**

        Creates a gaussian filter of given size.

        **PARAMETERS**

        * *dia*       -  int - diameter of Gaussian filter
                      - list - provide a list of three diameters to create
                               a 3 channel filter
        * *size*      - size of the filter (width, height)
        * *highpass*: -  bool 
                         True: highpass filter 
                         False: lowpass filter

        **RETURNS**

        DFT filter.

        **EXAMPLE**

        >>> gauss = DFT.createGaussianfilter(200, (512, 512),
                                            highpass=True)
        >>> gauss = DFT.createGaussianfilter([100, 120, 140], (512, 512),
                                             highpass=False)
        >>> img = Image('lenna')
        >>> gauss.applyFilter(img).show()
        """
        if isinstance(dia, list):
            if len(dia) != 3 and len(dia) != 1:
                warnings.warn("diameter list must be of size 1 or 3")
                return None
            stackedfilter = DFT()
            for d in dia:
                stackedfilter = stackedfilter._stackFilters(self.createGaussianFilter(d, size, highpass))
            image = Image(stackedfilter._numpy)
            retVal = DFT(numpyarray=stackedfilter._numpy, image=image,
                         dia=dia, channels = len(dia), size=size,
                         type="Gaussian", frequency=stackedfilter._freqpass)
            return retVal

        freqpass = "lowpass"
        sz_x, sz_y = size
        x0 = sz_x/2
        y0 = sz_y/2
        X, Y = np.meshgrid(np.arange(sz_x), np.arange(sz_y))
        D = np.sqrt((X-x0)**2+(Y-y0)**2)
        flt = 255*np.exp(-0.5*(D/dia)**2) 
        if highpass:
            flt = 255 - flt
            freqpass = "highpass"
        img = Image(flt)
        retVal = DFT(size=size, numpyarray=flt, image=img, dia=dia,
                     type="Gaussian", frequency=freqpass)
        return retVal

    @classmethod
    def createButterworthFilter(self, dia=400, size=(64, 64), order=2, highpass=False):
        """
        **SUMMARY**

        Creates a butterworth filter of given size and order.

        **PARAMETERS**

        * *dia*       - int - diameter of Gaussian filter
                      - list - provide a list of three diameters to create
                               a 3 channel filter
        * *size*      - size of the filter (width, height)
        * *order*     - order of the filter
        * *highpass*: -  bool 
                         True: highpass filter 
                         False: lowpass filter

        **RETURNS**

        DFT filter.

        **EXAMPLE**

        >>> flt = DFT.createButterworthfilter(100, (512, 512), order=3,
                                             highpass=True)
        >>> flt = DFT.createButterworthfilter([100, 120, 140], (512, 512),
                                             order=3, highpass=False)
        >>> img = Image('lenna')
        >>> flt.applyFilter(img).show()
        """
        if isinstance(dia, list):
            if len(dia) != 3 and len(dia) != 1:
                warnings.warn("diameter list must be of size 1 or 3")
                return None
            stackedfilter = DFT()
            for d in dia:
                stackedfilter = stackedfilter._stackFilters(self.createButterworthFilter(d, size, order, highpass))
            image = Image(stackedfilter._numpy)
            retVal = DFT(numpyarray=stackedfilter._numpy, image=image,
                         dia=dia, channels = len(dia), size=size,
                         type=stackedfilter._type, order=order,
                         frequency=stackedfilter._freqpass)
            return retVal
        freqpass = "lowpass"
        sz_x, sz_y = size
        x0 = sz_x/2
        y0 = sz_y/2
        X, Y = np.meshgrid(np.arange(sz_x), np.arange(sz_y))
        D = np.sqrt((X-x0)**2+(Y-y0)**2)
        flt = 255/(1.0 + (D/dia)**(order*2))
        if highpass:
            frequency = "highpass"
            flt = 255 - flt
        img = Image(flt)
        retVal = DFT(size=size, numpyarray=flt, image=img, dia=dia,
                     type="Butterworth", frequency=freqpass)
        return retVal

    @classmethod    
    def createLowpassFilter(self, xCutoff, yCutoff=None, size=(64, 64)):
        """
        **SUMMARY**

        Creates a lowpass filter of given size and order.

        **PARAMETERS**

        * *xCutoff*       - int - horizontal cut off frequency
                          - list - provide a list of three cut off frequencies
                                   to create a 3 channel filter
        * *yCutoff*       - int - vertical cut off frequency
                          - list - provide a list of three cut off frequencies
                                   to create a 3 channel filter
        * *size*      - size of the filter (width, height)

        **RETURNS**

        DFT filter.

        **EXAMPLE**

        >>> flt = DFT.createLowpassFilter(xCutoff=75, size=(320, 280))

        >>> flt = DFT.createLowpassFilter(xCutoff=[75], size=(320, 280))

        >>> flt = DFT.createLowpassFilter(xCutoff=[75, 100, 120],
                                          size=(320, 280))

        >>> flt = DFT.createLowpassFilter(xCutoff=75, yCutoff=35,
                                          size=(320, 280))

        >>> flt = DFT.createLowpassFilter(xCutoff=[75], yCutoff=[35],
                                          size=(320, 280))

        >>> flt = DFT.createLowpassFilter(xCutoff=[75, 100, 125], yCutoff=35,
                                          size=(320, 280))
        >>> # yCutoff will be [35, 35, 35]

        >>> flt = DFT.createLowpassFilter(xCutoff=[75, 113, 124],
                                          yCutoff=[35, 45, 90],
                                          size=(320, 280))
        
        >>> img = Image('lenna')
        >>> flt.applyFilter(img).show()
        """
        if isinstance(xCutoff, list):
            if len(xCutoff) != 3 and len(xCutoff) != 1:
                warnings.warn("xCutoff list must be of size 3 or 1")
                return None
            if isinstance(yCutoff, list):
                if len(yCutoff) != 3 and len(yCutoff) != 1:
                    warnings.warn("yCutoff list must be of size 3 or 1")
                    return None
                if len(yCutoff) == 1:
                    yCutoff = [yCutoff[0]]*len(xCutoff)
            else:
                yCutoff = [yCutoff]*len(xCutoff)
            stackedfilter = DFT()
            for xfreq, yfreq in zip(xCutoff, yCutoff):
                stackedfilter = stackedfilter._stackFilters(self.createLowpassFilter(xfreq, yfreq, size))
            image = Image(stackedfilter._numpy)
            retVal = DFT(numpyarray=stackedfilter._numpy, image=image,
                         xCutoffLow=xCutoff, yCutoffLow=yCutoff,
                         channels=len(xCutoff), size=size,
                         type=stackedfilter._type, order=self._order,
                         frequency=stackedfilter._freqpass)
            return retVal

        w, h = size
        xCutoff = np.clip(int(xCutoff), 0, w/2)
        if yCutoff is None:
            yCutoff = xCutoff
        yCutoff = np.clip(int(yCutoff), 0, h/2)
        flt = np.zeros((w, h))
        flt[0:xCutoff, 0:yCutoff] = 255
        flt[0:xCutoff, h-yCutoff:h] = 255
        flt[w-xCutoff:w, 0:yCutoff] = 255
        flt[w-xCutoff:w, h-yCutoff:h] = 255
        img = Image(flt)
        lowpassFilter = DFT(size=size, numpyarray=flt, image=img,
                            type="Lowpass", xCutoffLow=xCutoff,
                            yCutoffLow=yCutoff, frequency="lowpass")
        return lowpassFilter

    @classmethod
    def createHighpassFilter(self, xCutoff, yCutoff=None, size=(64, 64)):
        """
        **SUMMARY**

        Creates a highpass filter of given size and order.

        **PARAMETERS**

        * *xCutoff*       - int - horizontal cut off frequency
                          - list - provide a list of three cut off frequencies
                                   to create a 3 channel filter
        * *yCutoff*       - int - vertical cut off frequency
                          - list - provide a list of three cut off frequencies
                                   to create a 3 channel filter
        * *size*      - size of the filter (width, height)

        **RETURNS**

        DFT filter.

        **EXAMPLE**

        >>> flt = DFT.createHighpassFilter(xCutoff=75, size=(320, 280))

        >>> flt = DFT.createHighpassFilter(xCutoff=[75], size=(320, 280))

        >>> flt = DFT.createHighpassFilter(xCutoff=[75, 100, 120],
                                           size=(320, 280))

        >>> flt = DFT.createHighpassFilter(xCutoff=75, yCutoff=35, 
                                           size=(320, 280))

        >>> flt = DFT.createHighpassFilter(xCutoff=[75], yCutoff=[35],
                                           size=(320, 280))

        >>> flt = DFT.createHighpassFilter(xCutoff=[75, 100, 125], yCutoff=35,
                                           size=(320, 280))
        >>> # yCutoff will be [35, 35, 35]

        >>> flt = DFT.createHighpassFilter(xCutoff=[75, 113, 124],
                                           yCutoff=[35, 45, 90],
                                           size=(320, 280))
        
        >>> img = Image('lenna')
        >>> flt.applyFilter(img).show()
        """
        if isinstance(xCutoff, list):
            if len(xCutoff) != 3 and len(xCutoff) != 1:
                warnings.warn("xCutoff list must be of size 3 or 1")
                return None
            if isinstance(yCutoff, list):
                if len(yCutoff) != 3 and len(yCutoff) != 1:
                    warnings.warn("yCutoff list must be of size 3 or 1")
                    return None
                if len(yCutoff) == 1:
                    yCutoff = [yCutoff[0]]*len(xCutoff)
            else:
                yCutoff = [yCutoff]*len(xCutoff)
            stackedfilter = DFT()
            for xfreq, yfreq in zip(xCutoff, yCutoff):
                stackedfilter = stackedfilter._stackFilters(
                                self.createHighpassFilter(xfreq, yfreq, size))
            image = Image(stackedfilter._numpy)
            retVal = DFT(numpyarray=stackedfilter._numpy, image=image,
                         xCutoffHigh=xCutoff, yCutoffHigh=yCutoff,
                         channels=len(xCutoff), size=size,
                         type=stackedfilter._type, order=self._order,
                         frequency=stackedfilter._freqpass)
            return retVal

        lowpass = self.createLowpassFilter(xCutoff, yCutoff, size)
        w, h = lowpass.size()
        flt = lowpass._numpy
        flt = 255 - flt
        img = Image(flt)
        highpassFilter = DFT(size=size, numpyarray=flt, image=img,
                             type="Highpass", xCutoffHigh=xCutoff,
                             yCutoffHigh=yCutoff, frequency="highpass")
        return highpassFilter

    @classmethod
    def createBandpassFilter(self, xCutoffLow, xCutoffHigh, yCutoffLow=None,
                             yCutoffHigh=None, size=(64, 64)):
        """
        **SUMMARY**

        Creates a banf filter of given size and order.

        **PARAMETERS**

        * *xCutoffLow*    - int - horizontal lower cut off frequency
                          - list - provide a list of three cut off frequencies
        * *xCutoffHigh*   - int - horizontal higher cut off frequency
                          - list - provide a list of three cut off frequencies
        * *yCutoffLow*    - int - vertical lower cut off frequency
                          - list - provide a list of three cut off frequencies
        * *yCutoffHigh*   - int - verical higher cut off frequency
                          - list - provide a list of three cut off frequencies
                                   to create a 3 channel filter
        * *size*      - size of the filter (width, height)

        **RETURNS**

        DFT filter.

        **EXAMPLE**

        >>> flt = DFT.createBandpassFilter(xCutoffLow=75,
                                           xCutoffHigh=190, size=(320, 280))

        >>> flt = DFT.createBandpassFilter(xCutoffLow=[75],
                                           xCutoffHigh=[190], size=(320, 280))

        >>> flt = DFT.createBandpassFilter(xCutoffLow=[75, 120, 132],
                                           xCutoffHigh=[190, 210, 234],
                                           size=(320, 280))

        >>> flt = DFT.createBandpassFilter(xCutoffLow=75, xCutoffHigh=190,
                                           yCutoffLow=60, yCutoffHigh=210,
                                           size=(320, 280))

        >>> flt = DFT.createBandpassFilter(xCutoffLow=[75], xCutoffHigh=[190],
                                           yCutoffLow=[60], yCutoffHigh=[210],
                                           size=(320, 280))

        >>> flt = DFT.createBandpassFilter(xCutoffLow=[75, 120, 132],
                                           xCutoffHigh=[190, 210, 234], 
                                           yCutoffLow=[70, 110, 112], 
                                           yCutoffHigh=[180, 220, 220], 
                                           size=(320, 280))
        
        >>> img = Image('lenna')
        >>> flt.applyFilter(img).show()
        """
        lowpass = self.createLowpassFilter(xCutoffLow, yCutoffLow, size)
        highpass = self.createHighpassFilter(xCutoffHigh, yCutoffHigh, size)
        lowpassnumpy = lowpass._numpy
        highpassnumpy = highpass._numpy
        bandpassnumpy = lowpassnumpy + highpassnumpy
        bandpassnumpy = np.clip(bandpassnumpy, 0, 255)
        img = Image(bandpassnumpy)
        bandpassFilter = DFT(size=size, image=img,
                             numpyarray=bandpassnumpy, type="bandpass",
                             xCutoffLow=xCutoffLow, yCutoffLow=yCutoffLow,
                             xCutoffHigh=xCutoffHigh, yCutoffHigh=yCutoffHigh,
                             frequency="bandpass", channels=lowpass.channels)
        return bandpassFilter

    @classmethod
    def createNotchFilter(self, dia1, dia2=None, cen=None, size=(64, 64), type="lowpass"):
        """
        **SUMMARY**

        Creates a disk shaped notch filter of given diameter at given center.

        **PARAMETERS**

        * *dia1*       -  int - diameter of the disk shaped notch
                       - list - provide a list of three diameters to create
                               a 3 channel filter
        * *dia2*       -  int - outer diameter of the disk shaped notch
                                used for bandpass filter
                       - list - provide a list of three diameters to create
                               a 3 channel filter
        * *cen*        - tuple (x, y) center of the disk shaped notch
                         if not provided, it will be at the center of the 
                         filter
        * *size*       - size of the filter (width, height)
        * *type*:      - lowpass or highpass filter

        **RETURNS**
        DFT notch filter

        **EXAMPLE**

        >>> notch = DFT.createNotchFilter(dia1=200, cen=(200, 200),
                                          size=(512, 512), type="highpass")
        >>> notch = DFT.createNotchFilter(dia1=200, dia2=300, cen=(200, 200),
                                          size=(512, 512))
        >>> img = Image('lenna')
        >>> notch.applyFilter(img).show()
        """
        if isinstance(dia1, list):
            if len(dia1) != 3 and len(dia1) != 1:
                warnings.warn("diameter list must be of size 1 or 3")
                return None

            if isinstance(dia2, list):
                if len(dia2) != 3 and len(dia2) != 1:
                    warnings.warn("diameter list must be of size 3 or 1")
                    return None
                if len(dia2) == 1:
                    dia2 = [dia2[0]]*len(dia1)
            else:
                dia2 = [dia2]*len(dia1)

            if isinstance(cen, list):
                if len(cen) != 3 and len(cen) != 1:
                    warnings.warn("center list must be of size 3 or 1")
                    return None
                if len(cen) == 1:
                    cen = [cen[0]]*len(dia1)
            else:
                cen = [cen]*len(dia1)

            stackedfilter = DFT()
            for d1, d2, c in zip(dia1, dia2, cen):
                stackedfilter = stackedfilter._stackFilters(self.createNotchFilter(d1, d2, c, size, type))
            image = Image(stackedfilter._numpy)
            retVal = DFT(numpyarray=stackedfilter._numpy, image=image,
                         dia=dia1+dia2, channels = len(dia1), size=size,
                         type=stackedfilter._type,
                         frequency=stackedfilter._freqpass)
            return retVal

        w, h = size
        if cen is None:
            cen = (w/2, h/2)
        a, b = cen
        y, x = np.ogrid[-a:w-a, -b:h-b]
        r = dia1/2
        mask = x*x + y*y <= r*r
        flt = np.ones((w, h))
        flt[mask] = 255
        if type == "highpass":
            flt = 255-flt
        if dia2 is not None:
            a, b = cen
            y, x = np.ogrid[-a:w-a, -b:h-b]
            r = dia2/2
            mask = x*x + y*y <= r*r
            flt1 = np.ones((w, h))
            flt1[mask] = 255
            flt1 = 255 - flt1
            flt = flt + flt1
            np.clip(flt, 0, 255)
            type = "bandpass"
        img = Image(flt)
        notchfilter = DFT(size=size, numpyarray=flt, image=img, dia=dia1,
                          type="Notch", frequency=type)
        return notchfilter

    def applyFilter(self, image, grayscale=False):
        """
        **SUMMARY**

        Apply the DFT filter to given image.

        **PARAMETERS**

        * *image*     - SimpleCV.Image image
        * *grayscale* - if this value is True we perfrom the operation on the 
                        DFT of the gray version of the image and the result is
                        gray image. If grayscale is true we perform the 
                        operation on each channel and the recombine them to
                        create the result.

        **RETURNS**

        Filtered Image.

        **EXAMPLE**

        >>> notch = DFT.createNotchFilter(dia1=200, cen=(200, 200),
                                          size=(512, 512), type="highpass")
        >>> img = Image('lenna')
        >>> notch.applyFilter(img).show()
        """

        if self.width == 0 or self.height == 0:
            warnings.warn("Empty Filter. Returning the image.")
            return image
        w, h = image.size()
        if grayscale:
            image = image.toGray()
        fltImg = self._image
        if fltImg.size() != image.size():
            fltImg = fltImg.resize(w, h)
        filteredImage = image.applyDFTFilter(fltImg)
        return filteredImage

    def getImage(self):
        """
        **SUMMARY**

        Get the SimpleCV Image of the filter

        **RETURNS**

        Image of the filter.

        **EXAMPLE**

        >>> notch = DFT.createNotchFilter(dia1=200, cen=(200, 200),
                                          size=(512, 512), type="highpass")
        >>> notch.getImage().show()
        """
        if isinstance(self._image, type(None)):
            if isinstance(self._numpy, type(None)):
                warnings.warn("Filter doesn't contain any image")
            self._image = Image(self._numpy)
        return self._image

    def getNumpy(self):
        """
        **SUMMARY**

        Get the numpy array of the filter

        **RETURNS**

        numpy array of the filter.

        **EXAMPLE**

        >>> notch = DFT.createNotchFilter(dia1=200, cen=(200, 200),
                                          size=(512, 512), type="highpass")
        >>> notch.getNumpy()
        """
        if isinstance(self._numpy, type(None)):
            if isinstance(self._image, type(None)):
                warnings.warn("Filter doesn't contain any image")
            self._numpy = self._image.getNumpy()
        return self._numpy

    def getOrder(self):
        """
        **SUMMARY**

        Get order of the butterworth filter

        **RETURNS**

        order of the butterworth filter

        **EXAMPLE**

        >>> flt = DFT.createButterworthFilter(order=4)
        >>> print flt.getOrder()
        """
        return self._order

    def size(self):
        """
        **SUMMARY**

        Get size of the filter

        **RETURNS**

        tuple of (width, height)

        **EXAMPLE**

        >>> flt = DFT.createGaussianFilter(size=(380, 240))
        >>> print flt.size()
        """
        return (self.width, self.height)

    def getDia(self):
        """
        **SUMMARY**

        Get diameter of the filter

        **RETURNS**

        diameter of the filter

        **EXAMPLE**

        >>> flt = DFT.createGaussianFilter(dia=200, size=(380, 240))
        >>> print flt.getDia()
        """
        return self._dia

    def getType(self):
        """
        **SUMMARY**

        Get type of the filter

        **RETURNS**

        type of the filter

        **EXAMPLE**

        >>> flt = DFT.createGaussianFilter(dia=200, size=(380, 240))
        >>> print flt.getType() # Gaussian
        """
        return self._type

    def stackFilters(self, flt1, flt2):
        """
        **SUMMARY**

        Stack three signle channel filters of the same size to create
        a 3 channel filter.

        **PARAMETERS**

        * *flt1* - second filter to be stacked
        * *flt2* - thrid filter to be stacked

        **RETURNS**

        DFT filter

        **EXAMPLE**

        >>> flt1 = DFT.createGaussianFilter(dia=200, size=(380, 240))
        >>> flt2 = DFT.createGaussianFilter(dia=100, size=(380, 240))
        >>> flt2 = DFT.createGaussianFilter(dia=70, size=(380, 240))
        >>> flt = flt1.stackFilters(flt2, flt3) # 3 channel filter
        """
        if not(self.channels == 1 and flt1.channels == 1 and flt2.channels == 1):
            warnings.warn("Filters must have only 1 channel")
            return None
        if not (self.size() == flt1.size() and self.size() == flt2.size()):
            warnings.warn("All the filters must be of same size")
            return None
        numpyflt = self._numpy
        numpyflt1 = flt1._numpy
        numpyflt2 = flt2._numpy
        flt = np.dstack((numpyflt, numpyflt1, numpyflt2))
        img = Image(flt)
        stackedfilter = DFT(size=self.size(), numpyarray=flt, image=img, channels=3)
        return stackedfilter

    def _stackFilters(self, flt1):
        """
        **SUMMARY**

        stack two filters of same size. channels don't matter.

        **PARAMETERS**

        * *flt1* - second filter to be stacked

        **RETURNS**

        DFT filter

        """
        if isinstance(self._numpy, type(None)):
            return flt1
        if not self.size() == flt1.size():
            warnings.warn("All the filters must be of same size")
            return None
        numpyflt = self._numpy
        numpyflt1 = flt1._numpy
        flt = np.dstack((numpyflt, numpyflt1))
        stackedfilter = DFT(size=self.size(), numpyarray=flt,
                            channels=self.channels+flt1.channels,
                            type=self._type, frequency=self._freqpass)
        return stackedfilter
