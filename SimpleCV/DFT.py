from SimpleCV.base import np, warnings
from SimpleCV.ImageClass import Image

class DFT:
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
        flt = self._numpy
        flt = 255 - flt
        img = Image(flt)
        invertedfilter = DFT(numpyarray=flt, image=img,
                             size=self.size(), type=self._type)
        invertedfilter._updateParams(self)
        return invertedfilter

    def createGaussianFilter(self, dia=400, size=(64, 64), highpass=False):
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

    def createButterworthFilter(self, dia=400, size=(64, 64), order=2, highpass=False):
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

    def createLowpassFilter(self, xCutoff, yCutoff=None, size=(64, 64)):
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

    def createHighpassFilter(self, xCutoff, yCutoff=None, size=(64, 64)):
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
                stackedfilter = stackedfilter._stackFilters(self.createHighpassFilter(xfreq, yfreq, size))
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

    def createBandpassFilter(self, xCutoffLow, xCutoffHigh, yCutoffLow=None, yCutoffHigh=None, size=(64, 64)):
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

    def createNotchFilter(self, dia1, dia2=None, cen=None, size=(64, 64), type="lowpass"):
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

    def applyFilter(self, image):
        if self.width == 0 or self.height == 0:
            warnings.warn("Empty Filter. Returning the image.")
            return image
        w, h = image.size()
        fltImg = self._image
        if fltImg.size() != image.size():
            fltImg = fltImg.resize(w, h)
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

    def size(self):
        return (self.width, self.height)

    def getDia(self):
        return self._dia

    def getType(self):
        return self._type

    def stackFilters(self, flt1, flt2):
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
