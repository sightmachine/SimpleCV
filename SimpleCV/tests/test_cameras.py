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

def test_camera_properties():
    mycam = Camera()
    properties = mycam.getAllProperties()
    known_properties = {'brightness', 'contrast', 'exposure', 'gain', 'height', 'hue', 'saturation', 'width'}
    for i in known_properties: #checks to see if all the properties are properly returned
        if i not in properties:
            assert False

    for i in properties: #checks to see if getProperty is consistent
        if mycam.getProperty(i) != properties[i]:
            assert False

    #checks if the property values are within range
    if properties['brightness'] < 0 or properties['brightness'] > 1:
        assert False
    if properties['contrast'] < 0 or properties['contrast'] > 1:
        assert False
    if properties['saturation'] < 0:
        assert False
    if properties['height'] < 0:
        assert False
    if properties['width'] < 0:
        assert False
    pass