#!/usr/bin/python

# A Basic SimpleCV interactive shell tutorial

#load required libraries
from SimpleCV import *

from subprocess import call
import platform

lb = "\n" #linebreak
tb = "\t" #tab

#Command to clear the shell screen
def clear():
  if platform.system() == "Windows":
    return
  call("clear")


def tutorial_image():
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

def tutorial_save():
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
def tutorial_copy():
  clear()
  print "Image Copy"
  print "If you need a copy of an image, this is also very simple"
  print "img = Image('./SimpleCV/sampleimages/color.jpg')"
  print "clonedimage = img.copy()"
  print lb
  print lb
  in_text = ""
  shouldbe = "clone = img.copy()"
  print "Please type this now:"
  print shouldbe
  print lb
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

def tutorial_slicing():
  clear()
  print "Slicing:"
  print "Slicing is sort of a new paradigm to access parts of an image"
  print "Typically in vision a region of interest (ROI) is given.  "
  print "In this case slicing is a very powerful way to access parts"
  print "of an image, or basically any matrix in SimpleCV in general."
  print lb
  print "This is done by using:"
  print "section = img[1:10,1:10]"
  print lb
  print "What is returned is an image object with that window."
  print "the slicing basically acts like a ROI but returns an image"
  print "so if you wanted to say run edge detection on a 20x20 box"
  print "in the picture that started at x=5,y=10 you use:"
  print "foundedges = img[5:25,10:30].edges()"
  print lb
  raw_input("[Press enter to continue]")
  clear()
  in_text = ""
  shouldbe = "ROI = img[1:6,1:6]"
  print "Please type this now:"
  print shouldbe
  print lb
  while (in_text != shouldbe):
    in_text = raw_input("SimpleCV:>")
    if(in_text != shouldbe):
      print "sorry, that is incorrect"
      print "please type:"
      print shouldbe
  clear()
  print "Correct, you just returned a 5 pixel by 5 pixel image object"
  print lb
  return

def tutorial_corners():
  clear()
  print "Finding corners:"
  print "This will find corner Feature objects and return them as a FeatureSet"
  print "the  strongest corners first.  The parameters give the number"
  print "of corners to look for, the minimum quality of the corner feature"
  print "and the minimum distance between corners. "
  print lb
  print "This is also very easy to do in SimpleCV, you use:"
  print "foundcorners = image.findCorners()"
  print lb
  print "Now keep in mind parameters can be passed as a threshold as well"
  print "to the function so you can use:"
  print "foundcorners = image.findCorners(2)"
  print lb
  print "If you are unsure what parameters to pass it you can always"
  print "the built in help support by typing"
  print "help image.finderCorners"
  print lb
  print "keep in mind this help works for all of the functions available"
  print "in SimpleCV"
  print lb
  raw_input("[Press enter to continue]")
  clear()
  in_text = ""
  shouldbe = "corners = img.findCorners()"
  print "Please type this now:"
  print shouldbe
  print lb
  while (in_text != shouldbe):
    in_text = raw_input("SimpleCV:>")
    if(in_text != shouldbe):
      print "sorry, that is incorrect"
      print "please type:"
      print shouldbe
  clear()
  print "Correct, you just returned a featureset object which contains"
  print "feature objects.  These feature objects contain data from the"
  print "found corners"
  print lb
  return

    
def magic_tutorial(self,arg):
  if (arg == ""):
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
    print lb
    print lb
    raw_input("[Press enter to continue]")
    tutorial_image()
    tutorial_save()
    tutorial_copy()
    tutorial_slicing()
    tutorial_corners()
    
    return
    
  elif (arg == "image"):
    tutorial_image()

  elif (arg == "save"):
    tutorial_save()
    
  elif (arg == "copy"):
    tutorial_copy()
    
  elif (arg == "slicing"):
    tutorial_slicing()
      
  elif (arg == "corners"):
    tutorial_corners()
