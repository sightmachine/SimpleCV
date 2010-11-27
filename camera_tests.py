#!/usr/bin/python

import os, sys
from SimpleCV import * 
from nose.tools import with_setup


testoutput = "sampleimages/cam.jpg"


def test_camera_constructor():
  mycam = Camera(0)

  props = mycam.getAllProperties()

  for i in props.keys():
    print str(i) + ": " + str(props[i]) + "\n"
  
  
  return 1

def test_camera_image():
  mycam = Camera(0)

  img = mycam.getImage()
  img.save(testoutput)

