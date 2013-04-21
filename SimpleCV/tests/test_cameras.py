#!/usr/bin/python

import os, sys
from SimpleCV import *
from nose.tools import with_setup


testoutput = "sampleimages/cam.jpg"
video = "../sampleimages/ball.mov"

def test_virtual_camera_constructor():
    mycam = VirtualCamera(testoutput, 'image')

    props = mycam.getAllProperties()

    for i in props.keys():
        print str(i) + ": " + str(props[i]) + "\n"


    pass

def test_camera_image():
    mycam = Camera(0)

    img = mycam.getImage()
    img.save(testoutput)
    pass

def test_virtual_camera_referencing():
    mycam = VirtualCamera(video, "video")
    img1 = mycam.getImage()
    for i in xrange(20):
        img2 = mycam.getImage()

    np1 = img1.getNumpy()
    np2 = img2.getNumpy()
    from numpy import array_equal
    if array_equal(np1, np2):
        assert False
    pass