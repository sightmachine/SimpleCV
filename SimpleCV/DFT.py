from SimpleCV.base import np
from SimpleCV.ImageClass import Image

class DFT:
    width = 0
    height = 0
    _numpy = ""
    _image = ""
    _dia = 0
    _type = "None"
    _order = 0

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

    def __repr__(self):
        return "<SimpleCV.DFT Object Filter type: %s, size:(%d, %d)>" %(self._type, self.width, self.height)

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

    def applyFilter(self, image):
        if self.width == 0 or self.height == 0:
            warnings.warn("Empty Filter. Returning the image.")
            return image
        w, h = image.size()
        fltImg = self._image.resize(w, h)
        filteredImage = image.applyDFTFilter(fltImg)
        return filteredImage
