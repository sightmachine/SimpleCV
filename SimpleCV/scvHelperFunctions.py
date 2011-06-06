#!/usr/bin/python

#load system libraries
from scvLibSys import *
#library includes
from scvLibInc import *



#couple quick typecheck helper functions
def is_number(n):
  return n in (IntType, LongType, FloatType)

def is_tuple(n):
  return type(n) == tuple 

def reverse_tuple(n):
  return tuple(reversed(n))
