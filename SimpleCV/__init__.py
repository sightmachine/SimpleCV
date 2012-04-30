__version__ = '1.2.0'

from SimpleCV.base import *
from SimpleCV.Camera import *
from SimpleCV.Color import *
from SimpleCV.Display import *
from SimpleCV.Features import *
from SimpleCV.ImageClass import *
from SimpleCV.Stream import *
from SimpleCV.Font import *
from SimpleCV.ColorModel import *
from SimpleCV.DrawingLayer import *
from SimpleCV.Segmentation import *
from SimpleCV.MachineLearning import *


if (__name__ == '__main__'):
    from SimpleCV.Shell import *
    main(sys.argv)
def system():
    """
    **SUMMARY**
    Output of this function includes various informations related to the system and versions of libraries. 
    Main purpose is during :
       1) Submiting bug reports 
       2) Checking the version and later upgrading the library versions based on the current output. 
   
    **RETURNS**
    None  
    
    **EXAMPLE**
    >>> import SimpleCV
    >>> SimpleCV.system()
    """         	
    try:
        import platform
        print "System : ", platform.system()
        print "OS version : ", platform.version()
        print "Python version :", platform.python_version()
        try :
            from cv2 import __version__
            print "Open CV version : " + __version__
        except :
            print "Open CV version : " + "2.1"
        print "PIL version : ", pil.VERSION
        print "Orange Version : " + orange.version
        print "PyGame Version : " + pg.__version__
        print "Pickle Version : " + pickle.__version__
    except:
        print "You need to install Platform to use this function"
        print "to install you can use:"
        print "easy_install platform"
    return