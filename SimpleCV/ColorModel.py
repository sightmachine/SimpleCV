# SimpleCV Color Model Library
#load required libraries
from SimpleCV.base import *
from SimpleCV.ImageClass import *


class ColorModel:
    """
    **SUMMARY**

    The color model is used to model the color of foreground and background objects
    by using a a training set of images.

    You can create the color model with any number of "training" images, or
    add images to the model with add() and remove().  Then for your data images,
    you can useThresholdImage() to return a segmented picture.

    """
    #TODO: Discretize the colorspace into smaller intervals,eg r=[0-7][8-15] etc
    #TODO: Work in HSV space
    mIsBackground = True
    mData = {}
    mBits = 1

    def __init__(self, data = None, isBackground=True):
        self.mIsBackground = isBackground
        self.mData = {}
        self.mBits = 1

        if data:
            try:
                [ self.add(d) for d in data ]
            except TypeError:
                self.add(data)


    def _makeCanonical(self, data):
        """
        Turn input types in a common form used by the rest of the class -- a
        4-bit shifted list of unique colors
        """
        ret = ''

        #first cast everything to a numpy array
        if(data.__class__.__name__ == 'Image'):
            ret =  data.getNumpy().reshape(-1, 3)
        elif(data.__class__.__name__ == 'cvmat'):
            ret = np.array(data).reshape(-1, 3)
        elif(data.__class__.__name__ == 'list'  ):
            temp = []
            for d in data: #do the bgr conversion
                t = (d[2],d[1],d[0])
                temp.append(t)
            ret = np.array(temp,dtype='uint8')
        elif (data.__class__.__name__=='tuple'):
            ret = np.array((data[2],data[1],data[0]),'uint8')
        elif(data.__class__.__name__=='np.array'):
            ret = data
        else:
            logger.warning("ColorModel: color is not in an accepted format!")
            return None

        rs = np.right_shift(ret, self.mBits)  #right shift 4 bits

        if( len(rs.shape) > 1 ):
            uniques = np.unique(rs.view([('',rs.dtype)]*rs.shape[1])).view(rs.dtype).reshape(-1, 3)
        else:
            uniques = [rs]
        #create a unique set of colors.  I had to look this one up

        #create a dict of encoded strings
        return dict.fromkeys(map(np.ndarray.tostring, uniques), 1)

    def reset(self):
        """
        **SUMMARY**
        Resets the color model. I.e. clears it out the stored values.


        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> cm = ColorModel()
        >>> cm.add(Image("lenna))
        >>> cm.clear()

        """
        self.mData = {}

    def add(self, data):
        """
        **SUMMARY**

        Add an image, array, or tuple to the color model.

        **PARAMETERS**

        * *data* - An image, array, or tupple of values to the color model.

        **RETURNS**

        Nothings.

        **EXAMPLE**

        >>> cm = ColorModel()
        >>> cm.add(Image("lenna))
        >>> cm.clear()

        """
        self.mData.update(self._makeCanonical(data))

    def remove(self, data):
        """
        **SUMMARY**

        Remove an image, array, or tuple from the model.

        **PARAMETERS**

        * *data* - An image, array, or tupple of value.

        **RETURNS**

        Nothings.

        **EXAMPLE**

        >>> cm = ColorModel()
        >>> cm.add(Image("lenna))
        >>> cm.remove(Color.BLACK)

        """
        self.mData = dict.fromkeys(set(self.mData) ^ set(self._makeCanonical(data)), 1)

    def threshold(self, img):
        """
        **SUMMARY**

        Perform a threshold operation on the given image. This involves iterating
        over the image and comparing each pixel to the model. If the pixel is in the
        model it is set to be either the foreground (white) or background (black) based
        on the setting of mIsBackground.

        **PARAMETERS**

        * *img* - the image to perform the threshold on.

        **RETURNS**

        The thresholded image.

        **EXAMPLE**

        >>> cm = ColorModel()
        >>> cm.add(color.RED)
        >>> cm.add(color.BLUE)
        >>> result = cm.threshold(Image("lenna")
        >>> result.show()

        """
        a = 0
        b = 255
        if( self.mIsBackground == False ):
            a = 255
            b = 0

        rs = np.right_shift(img.getNumpy(), self.mBits).reshape(-1, 3) #bitshift down and reshape to Nx3
        mapped = np.array(map(self.mData.has_key, map(np.ndarray.tostring, rs))) #map to True/False based on the model
        thresh = np.where(mapped, a, b) #replace True and False with fg and bg
        return Image(thresh.reshape(img.width, img.height))

    def contains(self, c):
        """
        **SUMMARY**

        Return true if a particular color is in our color model.

        **PARAMETERS**

        * *c* - A three value color tupple.

        **RETURNS**

        Returns True if the color is in the model, False otherwise.

        **EXAMPLE**

        >>> cm = ColorModel()
        >>> cm.add(Color.RED)
        >>> cm.add(Color.BLUE)
        >>> if( cm.contains(Color.RED) )
        >>>   print "Yo - we gots red y'all."


       """
        #reverse the color, cast to uint8, right shift, convert to string, check dict
        return self.mData.has_key(np.right_shift(np.cast['uint8'](c[::-1]), self.mBits).tostring())

    def setIsForeground(self):
        """
        **SUMMARY**

        Set our model as being foreground imagery. I.e. things in the model are the foreground
        and will be marked as white during the threhsold operation.

        **RETURNS**

        Nothing.

        """
        mIsBackground = False

    def setIsBackground(self):
        """
        **SUMMARY**

        Set our model as being background imagery. I.e. things in the model are the background
        and will be marked as black during the threhsold operation.


        **RETURNS**

        Nothing.

        """
        mIsBackground = True

    def load(self, filename):
        """
        **SUMMARY**

        Load the color model from the specified file.

        **TO DO**

        This should be converted to pickle.

        **PARAMETERS**

        * *filename* - The file name and path to load the data from.

        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> cm = ColorModel()
        >>> cm.load("myColors.txt")
        >>> cm.add(Color.RED)
        >>> cm.add(Color.BLUE)
        >>> cm.save("mymodel)

        """
        self.mData =  load(open(filename))

    def save(self, filename):
        """
        **SUMMARY**

        Save a color model file.

        **PARAMETERS**

        * *filename* - The file name and path to save the data to.

        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> cm = ColorModel()
        >>> cm.add(Color.RED)
        >>> cm.add(Color.BLUE)
        >>> cm.save("mymodel.txt")

        **TO DO**

        This should be converted to pickle.

        """
        dump(self.mData, open(filename, "wb"))
