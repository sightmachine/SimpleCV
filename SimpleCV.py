#!/usr/bin/python

#system includes
import sys

#library includes
import cv
import numpy


class Image:
  width = 0    #width and height in px
  height = 0
  depth = 0
  filename = "" #source filename

  _bitmap = ""  #the bitmap (iplimage)  representation of the image
  _matrix = ""  #the matrix (cvmat) representation
  _bitmap_frames = []   #working space for bitmaps
  _matrix_frames = []   #working space for matricies 

  #initialize the frame
  #parameters: source designation (filename)
  #todo: handle camera/capture from file cases (detect on file extension)
  def __init__(self, sourcefile):
    self.filename = sourcefile
    bm = self.getBitmap()   
    self.width = bm.width
    self.height = bm.height
    self.depth = bm.depth

  #get the bitmap version (iplimage) of the image
  def getBitmap(self):
    if (self._bitmap):
      return self._bitmap
    else:
      self._bitmap = cv.LoadImage(self.filename, iscolor=cv.CV_LOAD_IMAGE_UNCHANGED) 
      return self._bitmap

  #get the matrix version of the image, if the matrix version doesn't exist
  #convert the bitmap
  def getMatrix(self):
    if (self._matrix):
      return self._matrix
    else:
      self._matrix = cv.GetMat(self.getBitmap) #convert the bitmap to a matrix
      return self._matrix;

  #save the image, if no filename then use the load filename and overwrite
  def save(self, filename=""):
    if (filename):
      cv.SaveImage(filename, self.getBitmap())  
    else:
      cv.SaveImage(self.sourcefile, self.getBitmap())

    return 1


def main(argv):
  print "hello world"   

if (__name__ == "__main__"):
  main(sys.argv)
