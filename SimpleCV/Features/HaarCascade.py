from SimpleCV.base import *

class HaarCascade():
    """
    This class wraps HaarCascade files for the findHaarFeatures file.
    To use the class provide it with the path to a Haar cascade XML file and
    optionally a name.
    """
    _mCascade = None
    _mName = None
    _cache = {}
    _fhandle = None


    def __init__(self, fname=None, name=None):
        #if fname.isalpha():
        #     fname = MY_CASCADES_DIR + fname + ".xml"

        if( name is None ):
            self._mName = fname
        else:
            self._mName = name

        #First checks the path given by the user, if not then checks SimpleCV's default folder
        if fname is not None:
            if os.path.exists(fname):
                self._fhandle = os.path.abspath(fname)
            else:
                self._fhandle = os.path.join(LAUNCH_PATH, 'Features','HaarCascades',fname)
                if (not os.path.exists(self._fhandle)):
                    logger.warning("Could not find Haar Cascade file " + fname)
                    logger.warning("Try running the function img.listHaarFeatures() to see what is available")
                    return None
            
            self._mCascade = cv.Load(self._fhandle)

            if HaarCascade._cache.has_key(self._fhandle):
                self._mCascade = HaarCascade._cache[self._fhandle]
                return
            HaarCascade._cache[self._fhandle] = self._mCascade

    def load(self, fname=None, name = None):
        if( name is None ):
            self._mName = fname
        else:
            self._mName = name

        if fname is not None:
            if os.path.exists(fname):
                self._fhandle = os.path.abspath(fname)
            else:
                self._fhandle = os.path.join(LAUNCH_PATH, 'Features','HaarCascades',fname)
                if (not os.path.exists(self._fhandle)):
                    logger.warning("Could not find Haar Cascade file " + fname)
                    logger.warning("Try running the function img.listHaarFeatures() to see what is available")
                    return None
            
            self._mCascade = cv.Load(self._fhandle)

            if HaarCascade._cache.has_key(self._fhandle):
                self._mCascade = HaarCascade._cache[fname]
                return
            HaarCascade._cache[self._fhandle] = self._mCascade
        else:
            logger.warning("No file path mentioned.")

    def getCascade(self):
        return self._mCascade

    def getName(self):
        return self._mName

    def setName(self,name):
        self._mName = name

    def getFHandle(self):
        return self._fhandle
