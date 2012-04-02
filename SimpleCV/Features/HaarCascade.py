from SimpleCV.base import *

class HaarCascade():
     """
     This class wraps HaarCascade files for the findHaarFeatures file.
     To use the class provide it with the path to a Haar cascade XML file and 
     optionally a name. 
     """
     _mCascade = None
     _mName = None
     def __init__(self, fname, name=None):
          if( name is None ):
               self._mName = fname
          else:
               self._mName = name
               
          if (not os.path.exists(fname)):
               logger.warning("Could not find Haar Cascade file " + fname)
               return None
          self._mCascade = cv.Load(fname)

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
