#!/usr/bin/python

# SimpleCV system includes
import os
import sys
import warnings
import time
import socket
import re
import urllib2
import types
import SocketServer
import threading
import tempfile
import zipfile
import pickle
import glob #for directory scanning
import abc #abstract base class
import colorsys
import logging
import pygame as pg
import scipy.ndimage as ndimage
import scipy.stats.stats as sss  #for auto white balance
import scipy.cluster.vq as scv    
import scipy.linalg as nla  # for linear algebra / least squares
import math # math... who does that 
import copy # for deep copy
import numpy as np
import scipy.spatial.distance as spsd
import scipy.cluster.vq as cluster #for kmeans
import pygame as pg
import platform
import copy
import types
import time

from numpy import linspace
from scipy.interpolate import UnivariateSpline
from warnings import warn
from copy import copy
from math import *
from pkg_resources import load_entry_point
from SimpleHTTPServer import SimpleHTTPRequestHandler
from types import IntType, LongType, FloatType, InstanceType
from cStringIO import StringIO
from numpy import int32
from numpy import uint8
from EXIF import *
from pygame import gfxdraw
from pickle import *

# SimpleCV library includes
try:
    import cv2.cv as cv
except ImportError:
    try:
        import cv
    except ImportError:
        raise ImportError("Cannot load OpenCV library which is required by SimpleCV")

#optional libraries
PIL_ENABLED = True
try:
    import Image as pil
    from Image.GifImagePlugin import getheader, getdata
except ImportError:
    try:
        import PIL.Image as pil
        from PIL import ImageFont as pilImageFont
        from PIL import ImageDraw as pilImageDraw
        from PIL.GifImagePlugin import getheader, getdata
    except ImportError:
        PIL_ENABLED = False

FREENECT_ENABLED = True
try:
    import freenect
except ImportError:
    FREENECT_ENABLED = False

OCR_ENABLED = True
try:
    import tesseract
except ImportError:
    OCR_ENABLED = False


ORANGE_ENABLED = True
try:
    import orange
    import orngTest #for cross validation
    import orngStat
    import orngEnsemble # for bagging / boosting

except ImportError:
    ORANGE_ENABLED = False

#couple quick typecheck helper functions
def is_number(n):
    """
    Determines if it is a number or not

    Returns: Type
    """
    return type(n) in (IntType, LongType, FloatType)

def is_tuple(n):
    """
    Determines if it is a tuple or not

    Returns: Boolean
    """
    return type(n) == tuple

def reverse_tuple(n):
    """
    Reverses a tuple

    Returns: Tuple
    """
    return tuple(reversed(n))

def find(f, seq):
    """
    Search for item in a list

    Returns: Boolean
    """
    for item in seq:
        if (f == item):
            return True
    return False

def test():
    """
    This function is meant to run builtin unittests
    """

    print 'unit test'


def download_and_extract(URL):
    """
    This function takes in a URL for a zip file, extracts it and returns
    the temporary path it was extracted to
    """
    if URL == None:
        logger.warning("Please provide URL")
        return None

    tmpdir = tempfile.mkdtemp()
    filename = os.path.basename(URL)
    path = tmpdir + "/" + filename
    zdata = urllib2.urlopen(URL)

    print "Saving file to disk please wait...."
    with open(path, "wb") as local_file:
        local_file.write(zdata.read())

    zfile = zipfile.ZipFile(path)
    print "Extracting zipfile"
    try:
        zfile.extractall(tmpdir)
    except:
        logger.warning("Couldn't extract zip file")
        return None

    return tmpdir

def int_to_bin(i):
    """Integer to two bytes"""
    i1 = i % 256
    i2 = int(i/256)
    return chr(i1) + chr(i2)

def npArray2cvMat(inputMat, dataType=cv.CV_32FC1):
    """
    This function is a utility for converting numpy arrays to the cv.cvMat format.

    Returns: cvMatrix
    """
    if( type(inputMat) == np.ndarray ):
        sz = len(inputMat.shape)
        temp_mat = None
        if( dataType == cv.CV_32FC1 or dataType == cv.CV_32FC2 or dataType == cv.CV_32FC3 or dataType == cv.CV_32FC4 ):
            temp_mat = np.array(inputMat, dtype='float32')
        elif( dataType == cv.CV_8UC1 or  dataType == cv.CV_8UC2 or dataType == cv.CV_8UC3 or dataType == cv.CV_8UC3):
            temp_mat = np.array(inputMat,dtype='uint8')
        else:
            logger.warning("MatrixConversionUtil: the input matrix type is not supported")
            return None
        if( sz == 1 ): #this needs to be changed so we can do row/col vectors
            retVal = cv.CreateMat(inputMat.shape[0], 1, dataType)
            cv.SetData(retVal, temp_mat.tostring(), temp_mat.dtype.itemsize * temp_mat.shape[0])
        elif( sz == 2 ):
            retVal = cv.CreateMat(temp_mat.shape[0], temp_mat.shape[1], dataType)
            cv.SetData(retVal, temp_mat.tostring(), temp_mat.dtype.itemsize * temp_mat.shape[1])
        elif( sz > 2 ):
            logger.warning("MatrixConversionUtil: the input matrix type is not supported")
            return None
        return retVal
    else:
        logger.warning("MatrixConversionUtil: the input matrix type is not supported")

#Logging system - Global elements

consoleHandler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
consoleHandler.setFormatter(formatter)
logger = logging.getLogger('Main Logger')
logger.addHandler(consoleHandler)

try:
    import IPython
    ipython_version = IPython.__version__
except ImportError:
    ipython_version = None

#This is used with sys.excepthook to log all uncaught exceptions.
#By default, error messages ARE print to stderr.
def exception_handler(excType, excValue, traceback):
    logger.error("", exc_info=(excType, excValue, traceback))

    #print "Hey!",excValue
    #excValue has the most important info about the error.
    #It'd be possible to display only that and hide all the (unfriendly) rest.

sys.excepthook = exception_handler

def ipython_exception_handler(shell, excType, excValue, traceback,tb_offset=0):
    logger.error("", exc_info=(excType, excValue, traceback))


#The two following functions are used internally.
def init_logging(log_level):
    logger.setLevel(log_level)

def read_logging_level(log_level):
    levels_dict = {
        1: logging.DEBUG, "debug": logging.DEBUG,
        2: logging.INFO, "info": logging.INFO,
        3: logging.WARNING, "warning": logging.WARNING,
        4: logging.ERROR, "error": logging.ERROR,
        5: logging.CRITICAL, "critical": logging.CRITICAL
    }

    if isinstance(log_level,str):
       log_level = log_level.lower()

    if log_level in levels_dict:
        return levels_dict[log_level]
    else:
        print "The logging level given is not valid"
        return None

def get_logging_level():
    """
    This function prints the current logging level of the main logger.
    """
    levels_dict = {
        10: "DEBUG",
        20: "INFO",
        30: "WARNING",
        40: "ERROR",
        50: "CRITICAL"
    }

    print "The current logging level is:", levels_dict[logger.getEffectiveLevel()]

def set_logging(log_level,myfilename = None):
    """
    This function sets the threshold for the logging system and, if desired,
    directs the messages to a logfile. Level options:

    'DEBUG' or 1
    'INFO' or 2
    'WARNING' or 3
    'ERROR' or 4
    'CRITICAL' or 5

    If the user is on the interactive shell and wants to log to file, a custom
    excepthook is set. By default, if logging to file is not enabled, the way
    errors are displayed on the interactive shell is not changed.
    """

    if myfilename and ipython_version:
         try:
             if ipython_version.startswith("0.10"):
                 __IPYTHON__.set_custom_exc((Exception,), ipython_exception_handler)
             else:
                 ip = get_ipython()
                 ip.set_custom_exc((Exception,), ipython_exception_handler)
         except NameError: #In case the interactive shell is not being used
             sys.exc_clear()


    level = read_logging_level(log_level)

    if level and myfilename:
        fileHandler = logging.FileHandler(filename=myfilename)
        fileHandler.setLevel(level)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.removeHandler(consoleHandler) #Console logging is disabled.
        print "Now logging to",myfilename,"with level",log_level
    elif level:
        print "Now logging with level",log_level

    logger.setLevel(level)

def system():
    """
    **SUMMARY**
    Output of this function includes various informations related to system and library.
    Main purpose :
       1) While submiting a bug, report the output of this function
       2) Checking the current version and later upgrading the library based on the output

    **RETURNS**
    None

    **EXAMPLE**
    >>> import SimpleCV
    >>> SimpleCV.system()
    """
    try :
        import platform
        print "System : ", platform.system()
        print "OS version : ", platform.version()
        print "Python version :", platform.python_version()
        try :
            from cv2 import __version__
            print "Open CV version : " + __version__
        except ImportError :
            print "Open CV2 version : " + "2.1"
        if (PIL_ENABLED) :
            print "PIL version : ", pil.VERSION
        else :
            print "PIL module not installed"
        if (ORANGE_ENABLED) :
            print "Orange Version : " + orange.version
        else :
            print "Orange module not installed"
        try :
            import pygame as pg
            print "PyGame Version : " + pg.__version__
        except ImportError:
            print "PyGame module not installed"
        try :
            import pickle
            print "Pickle Version : " + pickle.__version__
        except :
            print "Pickle module not installed"

    except ImportError :
        print "You need to install Platform to use this function"
        print "to install you can use:"
        print "easy_install platform"
    return

class LazyProperty(object):

    def __init__(self, func):
        self._func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, klass=None):
        if obj is None: return None
        result = obj.__dict__[self.__name__] = self._func(obj)
        return result

class InitOptionsHandler(object):
    """
    **SUMMARY**

    This handler is supposed to store global variables. For now, its only value
    defines if SimpleCV is being run on an IPython notebook.

    """

    def __init__(self):
        self.on_notebook = False

    def enable_notebook(self):
        self.on_notebook = True


init_options_handler = InitOptionsHandler()

#supported image formats regular expression
IMAGE_FORMATS = ('*.bmp','*.gif','*.jpg','*.jpe','*.jpeg','*.png','*.pbm','*.pgm','*.ppm','*.tif','*.tiff','*.webp')
#maximum image size -
MAX_DIMENSION = 2*6000 # about twice the size of a full 35mm images - if you hit this, you got a lot data.
LAUNCH_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
