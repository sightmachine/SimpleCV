#!/usr/bin/python

from SimpleCV import Image 

testimage = "sampleimages/9dots4lines.png"
testoutput = "sampleimages/9d4l.jpg"


def test_loadsave():
  img = Image(testimage)
  img.save(testoutput)  

def test_bitmap():
  img = Image(testimage)
  bmp = img.getBitmap();
  if bmp.width > 0:
    return 1
  else:
    return 0

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
"""
