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
    self.image_copy()
    
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
    print "Saving an image is very simple, pardon the pun."
    print "but once it's loaded into memory, it's literally just:"
    print "image.save()"
    print lb
    print "This will save the image back to the location it was loaded from"
    print "so if you did img = Image('/tmp/test.jpg'), then it will save"
    print "it back there, otherwise you can do:"
    print "Image.save('/any/path/you/want')"
    print lb
    print "So try it now and save an image somewhere on your system"
    print "img.save('/tmp/new.jpg')"
    print lb
    in_text = ""
    shouldbe = "img.save('/tmp/new.jpg')"
    while (in_text != shouldbe):
      in_text = raw_input("SimpleCV:>")
      if(in_text != shouldbe):
        print "sorry, that is incorrect"
        print "please type:"
        print shouldbe

    clear()
    print "Correct, you just saved a new copy of the image to /tmp/new.jpg"
    print "as you can see in SimpleCV most of the functions are intuitive"
    print lb
    raw_input("[Press enter to continue]")
    return

  def image_copy(self):
    clear()
    print "If you need a copy of an image, this is also very simple"
    print "img = Image('./SimpleCV/sampleimages/color.jpg')"
    print "clonedimage = img.copy()"
    print lb
    print lb
    in_text = ""
    shouldbe = "clone = img.copy()"
    print "Please type this now:"
    print shouldbe
    while (in_text != shouldbe):
      in_text = raw_input("SimpleCV:>")
      if(in_text != shouldbe):
        print "sorry, that is incorrect"
        print "please type:"
        print shouldbe
    clear()
    print "Correct, you just cloned an image into memory"
    print "you need to be careful when using this method though"
    print "as using a reference vs. a copy.  For instance if you just"
    print "typed: clone = img"
    print "then clone is actually pointing at the same thing in memory"
    print "and if you did clone.binarize() it is the same as img.binarize()"
    print "so if you want a copy of an image you have to return a copy of"
    print "not just point a reference to it"
    print lb
    raw_input("[Press enter to continue]")
    return

    
