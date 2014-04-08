#!/usr/bin/python
import os, sys
from SimpleCV import *
from nose.tools import with_setup

def test_font_get_methods():
    font = Font()
    if font.getFont() != "ubuntu":
        print "the default font should be None."
        assert False
    if font.getSize() != 16:
        print "the default font size should be 16." 
        assert False
    font = Font("astloch", 24)
    if font.getFont() != "astloch":
        print "the constructor fails to successfully construct the font."
        assert False
    if font.getSize() != 24:
        print "the constructor fails to successfully set the right font size." 
        assert False
    pass


def test_font_set_methods():
    font = Font("astloch", 32)
    font.setSize(16)
    if font.getSize() != 16:
        print "the setSize method fails to successfully set the right font size." 
        assert False
    font.setFont("ubuntu")
    if font.getFont() != "ubuntu":
        print "the setFont method fails to successfully set the right font." 
        assert False
    pass