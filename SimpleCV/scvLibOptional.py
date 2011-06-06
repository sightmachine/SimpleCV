#!/usr/bin/python
# SimpleCV optional libraries

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
