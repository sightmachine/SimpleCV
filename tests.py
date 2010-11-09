#!/usr/bin/python

import os, sys
from SimpleCV import * 
from nose.tools import with_setup

testimage = "sampleimages/9dots4lines.png"
testimage2 = "sampleimages/aerospace.jpg"
testoutput = "sampleimages/9d4l.jpg"

def setup_context():
  img = Image(testimage)
  
def destroy_context():
  img = ""

@with_setup(setup_context, destroy_context)
def test_loadsave():
  img = Image(testimage)
  img.save(testoutput)  
  if (os.path.isfile(testoutput)):
    os.remove(testoutput)
    return 1
  else: 
    return 0
  
def test_bitmap():
  img = Image(testimage)
  bmp = img.getBitmap();
  if bmp.width > 0:
    return 1
  else:
    return 0

def test_matrix():
  img = Image(testimage)
  m = img.getMatrix()
  if (m.rows == img.getBitmap().width):
    return 1
  return 0 
  
def test_scale():
  img = Image(testimage)
  thumb = img.scale(30,30)
  thumb.save(testoutput)

def test_getitem():
  img = Image(testimage)
  colors = img[1,1]
  if (colors[0] == 255 and colors[1] == 255 and colors[2] == 255):
    return 1
  else: 
    return 0

def test_getslice():
  img = Image(testimage)
  section = img[1:10,1:10]
  section.save(testoutput)
  return 1


def test_setitem():
  img = Image(testimage)
  img[1,1] = (0, 0, 0)
  newimg = Image(img.getBitmap())
  colors = newimg[1,1]
  if (colors[0] == 0 and colors[1] == 0 and colors[2] == 0):
    return 1
  else:
    return 0

def test_setslice():
  img = Image(testimage)
  img[1:10,1:10] = (0,0,0) #make a black box
  newimg = Image(img.getBitmap())
  section = newimg[1:10,1:10]
  for i in range(5):
    colors = section[i,0]
    if (colors[0] != 0 or colors[1] != 0 or colors[2] != 0):
      return 0  
  return 1

def test_findCorners():
  img = Image(testimage2)
  corners = img.findCorners(25)
  if (len(corners) == 0):
    return 0 
  corners.draw()
  img.save(testoutput)
  
"""
def test_Harris(img):
  for (x,y) in cv.GoodFeaturesToTrack(img, eig_image, temp_image, 10, 0.04, 1.0, useHarris = True):
    cv.Circle(img, (x,y), 4, 0);
    print "good feature at", x,y

def test_Canny():
  img = cv.LoadImageM("sampleimages/9dots4lines.png", cv.CV_LOAD_IMAGE_GRAYSCALE)
  eig_image = cv.CreateMat(img.rows, img.cols, cv.CV_32FC1)
  temp_image = cv.CreateMat(img.rows, img.cols, cv.CV_32FC1)
  cv.Canny(img, temp_image, 10, 100, 11);
  cv.SaveImage("sampleimages/9d4lfeatures.png", temp_image);

def main(argv):
  test_getslice()

if (__name__ == "__main__"):
  main(sys.argv)

"""
