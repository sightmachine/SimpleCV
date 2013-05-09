from SimpleCV.base import np
from SimpleCV.ImageClass import Image

class DFT:
    width = 0
    height = 0
    _numpy = None
    _image = None
    _dia = 0
    _type = "None"
    _order = 0
    _lowpass = False
    _highpass = False
    _bandpass = False
    _xCutoffLow = 0
    _yCutoffLow = 0
    _xCutoffHigh = 0
    _xCutoffHigh = 0

    def __init__(self, **kwargs):
        for key in kwargs:
            if key == 'width':
                self.width = kwargs[key]
            elif key == 'height':
                self.height = kwargs[key]
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
            elif key == 'lowpass':
                self._lowpass = kwargs[key]
            elif key == 'highpass':
                self._highpass = kwargs[key]
            elif key == 'bandpass':
                self._bandpass = kwargs[key]
            elif key == 'xCutoffLow':
                self._xCutoffLow = kwargs[key]
            elif key == 'yCutoffLow':
                self._yCutoffLow = kwargs[key]
            elif key == 'xCutoffHigh':
                self._xCutoffHigh = kwargs[key]
            elif key == 'yCutoffHigh':
                self._yCutoffHigh = kwargs[key]
            elif key == 'highpass':
                self._highpass = kwargs[key]
            elif key == 'lowhpass':
                self._lowpass = kwargs[key]
            elif key == 'bandpass':
                self._bandpass = kwargs[key]

    def __repr__(self):
        return "<SimpleCV.DFT Object Filter type: %s, size:(%d, %d)>" %(self._type, self.width, self.height)

    def __add__(self, flt):
        if not isinstance(flt, type(self)):
            warnings.warn("Provide SimpleCV.DFT object")
            return None
        if self.getSize() != flt.getSize():
            warnings.warn("Both SimpleCV.DFT object must have the same size")
            return None
        flt_numpy = self._numpy + flt._numpy
        flt_image = Image(flt_numpy)
        w, h = flt_image.size()
        retVal = DFT(numpyarray=flt_numpy, image=flt_image, width=w, height=h)
        return retVal

    def createGaussianFilter(self, dia=400, size=(64, 64), highpass=False):
        sz_x, sz_y = size
        x0 = sz_x/2
        y0 = sz_y/2
        X, Y = np.meshgrid(np.arange(sz_x), np.arange(sz_y))
        D = np.sqrt((X-x0)**2+(Y-y0)**2)
        flt = 255*np.exp(-0.5*(D/dia)**2) 
        if highpass:     #then invert the filter
            flt = 255 - flt
        img = Image(flt)
        retVal = DFT(width=sz_x, height=sz_y, numpyarray=flt, image=img, dia=dia, type="Gaussian")
        return retVal

    def createButterworthFilter(self, dia=400, size=(64, 64), order=2, highpass=False):
        sz_x, sz_y = size
        x0 = sz_x/2
        y0 = sz_y/2
        X, Y = np.meshgrid(np.arange(sz_x), np.arange(sz_y))
        D = np.sqrt((X-x0)**2+(Y-y0)**2)
        flt = 255/(1.0 + (D/dia)**(order*2))
        if highpass:     #then invert the filter
            flt = 255 - flt
        img = Image(flt)
        retVal = DFT(width=sz_x, height=sz_y, numpyarray=flt, image=img, dia=dia, type="Butterworth")
        return retVal

    def createLowpassFilter(self, xCutoff, yCutoff=None, size=(64, 64)):
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
        lowpassFilter = DFT(width=w, height=h, numpyarray=flt, image=img,
                            type="Lowpass", xCutoffLow=xCutoff,
                            yCutoffLow=yCutoff)
        return lowpassFilter

    def createHighpassFilter(self, xCutoff, yCutoff=None, size=(64, 64)):
        lowpass = self.createLowpassFilter(xCutoff, yCutoff, size)
        w, h = lowpass.getSize()
        flt = lowpass._numpy
        flt = 255 - flt
        img = Image(flt)
        highpassFilter = DFT(width=w, height=h, numpyarray=flt, image=img,
                             type="Highpass", xCutoffHigh=xCutoff,
                             yCutoffHigh=yCutoff)
        return highpassFilter

    def createBandpassFilter(self, xCutoffLow, xCutoffHigh, yCutoffLow=None, yCutoffHigh=None, size=(64, 64)):
        lowpass = self.createLowpassFilter(xCutoffLow, yCutoffLow, size)
        highpass = self.createHighpassFilter(xCutoffHigh, yCutoffHigh, size)
        lowpassnumpy = lowpass._numpy
        highpassnumpy = highpass._numpy
        bandpassnumpy = lowpassnumpy + highpassnumpy
        bandpassnumpy = np.clip(bandpassnumpy, 0, 255)
        img = Image(bandpassnumpy)
        bandpassFilter = DFT(width=size[0], height=size[1], image=img,
                             numpyarray=bandpassnumpy, type="bandpass",
                             xCutoffLow=xCutoffLow, yCutoffLow=yCutoffLow,
                             xCutoffHigh=xCutoffHigh, yCutoffHigh=yCutoffHigh)
        return bandpassFilter

    def applyFilter(self, image):
        if self.width == 0 or self.height == 0:
            warnings.warn("Empty Filter. Returning the image.")
            return image
        w, h = image.size()
        fltImg = self._image
        if fltImg.size() != image.size():
            fltImg.resize(w, h)
        filteredImage = image.applyDFTFilter(fltImg)
        return filteredImage

    def getImage(self):
        if isinstance(self._image, type(None)):
            if isinstance(self._numpy, type(None)):
                warnings.warn("Filter doesn't contain any image")
            self._image = Image(self._numpy)
        return self._image

    def getNumpy(self):
        if isinstance(self._numpy, type(None)):
            if isinstance(self._image, type(None)):
                warnings.warn("Filter doesn't contain any image")
            self._numpy = self._image.getNumpy()
        return self._numpy

    def getOrder(self):
        return self._order

    def getSize(self):
        return (self.width, self.height)

    def getDia(self):
        return self._dia

    def getType(self):
        return self._type

    def isHighpass(self):
        return self._highpass

    def isLowpass(self):
        return self._lowpass

    def isBandpass(self):
        return self._bandpass
