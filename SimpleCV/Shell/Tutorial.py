#!/usr/bin/python

# A Basic SimpleCV interactive shell tutorial

#load required libraries
from SimpleCV import *

from subprocess import call

lb = "\n" #linebreak
tb = "\t" #tab

def clear():
  call("clear")


class Tutorial():
  
  text = None
  
  def __init__(self):
    text = None
    
  def start(self):
    clear()
    print "??????????????????????????????????"
    print " Welcome to the SimpleCV tutorial "
    print "??????????????????????????????????"
    print lb
    print "At anytime on the SimpleCV:> you can type tutorial."
    print "then press the tab key and it will autocomplete any tutorial"
    print "that is currently available."
    print lb
    print "You will first learn how to load an image"
    raw_input("[Press enter to continue]")
    self.image()
    self.image_save()
    
    return
    
  def image(self):
    clear()
    print "SimpleCV Image tutorial"
    print "-----------------------"
    print lb
    print "using images are simple, in SimpleCV"
    print "to start find a location where an actual file exist"
    print "in this example we have /tmp/simplecv.jpg"
    print "so to load this into memory, it's as easy as:"
    print lb
    print "img = Image('./SimpleCV/sampleimages/color.jpg')"
    print lb
    raw_input("[Press enter to continue]")
    clear()
    print "Now try it yourself at the terminal"
    print "img = Image('./SimpleCV/sampleimages/color.jpg')"
    print lb
    in_text = ""
    shouldbe = "img = Image('./SimpleCV/sampleimages/color.jpg')"
    while (in_text != shouldbe):
      in_text = raw_input("SimpleCV:>")
      if(in_text != shouldbe):
        print "sorry, that is incorrect"
        print "please type:"
        print shouldbe

    clear()
    print "Correct, you just loaded an image into memory"
    print "Images are the basis for everything in SimpleCV"
    print "they are what manipulations are performed on"
    print "but that is the basis for the image tutorial"
    print lb
    raw_input("[Press enter to continue]")
    return

  def image_save(self):
    clear()
    print "Once you have an Image Object loaded in memory you can"
    print "now save it to disk.  If you don't or don't know how then"
    print "you can run the image tutorial"
    print lb
    raw_input("[Press enter to continue]")
    clear()
    
    
    
