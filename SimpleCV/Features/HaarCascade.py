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
     
     
     
     def __init__(self, fname, name=None):
          #if fname.isalpha():
          #     fname = MY_CASCADES_DIR + fname + ".xml"
     
          if( name is None ):
              self._mName = fname
          else:
              self._mName = name
          
          if HaarCascade._cache.has_key(fname):
              self._mCascade = HaarCascade._cache[fname]
              return

          no_underscores = "".join([c for c in fname if c != '_'])

          if no_underscores.isalnum():
             fname = fname + ".xml"

          fhandle = os.path.join(LAUNCH_PATH, 'Features','HaarCascades',fname)

          if (not os.path.exists(fhandle)):
              logger.warning("Could not find Haar Cascade file " + fname)
              logger.warning("Try running the function img.listHaarFeatures() to see what is available")
              return None
          self._mCascade = cv.Load(fhandle)
          HaarCascade._cache[fhandle] = self._mCascade

     def load(self, fname, name = None):
          if( name is None ):
              self._mName = fname
          else:
              self._mName = name
               
          if (not os.path.exists(fname)):
              logger.warning("Could not find Haar Cascade file " + fname)
              return None

          self._mCascade = cv.Load(fname)

     def getCascade(self):
          return self._mCascade

     def getName(self):
          return self._mName
    
     def setName(self,name):
          self._mName = name
