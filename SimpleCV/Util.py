#!/usr/bin/python

#load system libraries
from __init__ import *


#couple quick typecheck helper functions
def is_number(n):
  return n in (IntType, LongType, FloatType)

def is_tuple(n):
  return type(n) == tuple 

def reverse_tuple(n):
  return tuple(reversed(n))


"""
This function is a utility for converting numpy arrays to the cv.cvMat format.  
"""
def npArray2cvMat(inputMat, dataType=cv.CV_32FC1):
  if( type(inputMat) == np.ndarray ):
    sz = len(inputMat.shape)
    if( sz == 1 ): #this needs to be changed so we can do row/col vectors
      retVal = cv.CreateMat(inputMat.shape[0],1,dataType)
      cv.SetData(retVal, inputMat.tostring(),inputMat.dtype.itemsize * inputMat.shape[0])
    elif( sz == 2 ):
      retVal = cv.CreateMat(inputMat.shape[0],inputMat.shape[1],dataType)
      cv.SetData(retVal, inputMat.tostring(),inputMat.dtype.itemsize * inputMat.shape[1])
    elif( sz > 2 ):
      retVal = cv.CreateMat(inputMat.shape,dataType)
      #I am going to hold off on this..... no good approach... may not be needed    
    return retVal
  else:
    warnings.warn("MatrixConversionUtil: the input matrix type is not supported")
