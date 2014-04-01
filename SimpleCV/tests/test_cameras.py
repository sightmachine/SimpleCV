#!/usr/bin/python

import os, sys
from SimpleCV import *
from nose.tools import with_setup


testoutput = "sampleimages/cam.jpg"


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

def test_camera_multiple_instances():
    cam1 = Camera()
    img1 = cam1.getImage()
    cam2 = Camera()
    img2 = cam2.getImage()

    if not cam1 or not cam2 or not img1 or not img2:
        assert False

    cam3 = Camera(0) # assuming the default camera index is 0
    img3 = cam3.getImage()

    if not cam3 or not img3:
        assert False
    pass
