#!/usr/bin/python

import os, sys
from SimpleCV import * 
from nose.tools import with_setup


testimage = "sampleimages/9dots4lines.png"
testvideo = "sampleimages/fasteners.mpg"
testoutput = "sampleimages/cam.jpg"


def test_camera_constructor():
  mycam = VirtualCamera(testimage, "image")

  props = mycam.getAllProperties()

  for i in props.keys():
    print str(i) + ": " + str(props[i]) + "\n"
  
  pass

def test_camera_image():
  mycam = VirtualCamera(testimage, "image")

  img = mycam.getImage()
  img.save(testoutput)

def test_camera_video():
  mycam = VirtualCamera(testvideo, "video")

  img = mycam.getImage()
  img.save(testoutput)

