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
  import Image as pil
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
