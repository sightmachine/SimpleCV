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
from copy import copy
from math import sqrt, atan2
from pkg_resources import load_entry_point
from SimpleHTTPServer import SimpleHTTPRequestHandler
from types import IntType, LongType, FloatType, InstanceType
from cStringIO import StringIO

# SimpleCV library includes
import cv
import numpy as np
import scipy.spatial.distance as spsd
from numpy import linspace
from scipy.interpolate import UnivariateSpline


#optional libraries
PIL_ENABLED = True
try:
    import PIL.Image as pil
    from PIL import ImageFont as pilImageFont
    from PIL import ImageDraw as pilImageDraw
except ImportError:
    try:
        import Image as pil  #needed on homebrew on mac
    except ImportError:
        PIL_ENABLED = False 

BLOBS_ENABLED = True
try:
    import cvblob as cvb
except ImportError:
    BLOBS_ENABLED = False 

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
        warnings.warn("MatrixConversionUtil: the input matrix type is not supported")


