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

from copy import copy
from math import sqrt, atan2
from pkg_resources import load_entry_point
from SimpleHTTPServer import SimpleHTTPRequestHandler
from types import IntType, LongType, FloatType, InstanceType
from cStringIO import StringIO


# SimpleCV library includes
try:
    import cv2.cv as cv
except ImportError:
    try:
        import cv
    except ImportError:
        raise ImportError("Cannot load OpenCV library which is required by SimpleCV")

import numpy as np
import scipy.spatial.distance as spsd
import scipy.cluster.vq as cluster #for kmeans
from numpy import linspace
from scipy.interpolate import UnivariateSpline
import pygame as pg



#optional libraries
PIL_ENABLED = True
try:
    import Image as pil
except ImportError:
    try:
        import PIL.Image as pil
        from PIL import ImageFont as pilImageFont
        from PIL import ImageDraw as pilImageDraw
    except ImportError:
        PIL_ENABLED = False

ZXING_ENABLED = True
try:
    import zxing
except ImportError:
    ZXING_ENABLED = False

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

def npArray2cvMat(inputMat, dataType=cv.CV_32FC1):
    """
    This function is a utility for converting numpy arrays to the cv.cvMat format.

    Returns: cvMatrix
    """
    if( type(inputMat) == np.ndarray ):
        sz = len(inputMat.shape)
        if( sz == 1 ): #this needs to be changed so we can do row/col vectors
            retVal = cv.CreateMat(inputMat.shape[0], 1, dataType)
            cv.SetData(retVal, inputMat.tostring(), inputMat.dtype.itemsize * inputMat.shape[0])
        elif( sz == 2 ):
            retVal = cv.CreateMat(inputMat.shape[0], inputMat.shape[1], dataType)
            cv.SetData(retVal, inputMat.tostring(), inputMat.dtype.itemsize * inputMat.shape[1])
        elif( sz > 2 ):
            retVal = cv.CreateMat(inputMat.shape, dataType)
            #I am going to hold off on this..... no good approach... may not be needed
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

#supported image formats regular expression
IMAGE_FORMATS = ('*.bmp','*.gif','*.jpg','*.jpe','*.jpeg','*.png','*.pbm','*.pgm','*.ppm','*.tif','*.tiff','*.webp')
#maximum image size - 
MAX_DIMENSION = 2*6000 # about twice the size of a full 35mm images - if you hit this, you got a lot data.  
