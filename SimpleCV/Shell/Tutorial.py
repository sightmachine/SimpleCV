#!/usr/bin/python

# A Basic SimpleCV interactive shell tutorial

#load required libraries
from SimpleCV import *

from subprocess import call
from code import InteractiveInterpreter
import platform

lb = "\n" #linebreak
tb = "\t" #tab
tutorial_interpreter = InteractiveInterpreter(globals())
logo = None
image = None

#Command to clear the shell screen
def shellclear():
    if platform.system() == "Windows":
      return
    call("clear")

def attempt(variable_name, desired_class):
    prompt_and_run()
    return isinstance(globals().get(variable_name),desired_class)

def prompt_and_run():
    command = raw_input("SimpleCV:> ")
    tutorial_interpreter.runsource(command)
    return command

def command_loop(command, desired_tuple):
    while True:
        print command
        print lb

        if attempt(desired_tuple[0], desired_tuple[1]):
            return

        print lb
        print "Oops! %s is still not %s" % (desired_tuple[0], str(desired_tuple[1]))

def tutorial_image():
    shellclear()
    print "SimpleCV Image tutorial"
    print "-----------------------"
    print lb
    print "Using images are simple, in SimpleCV."
    print lb
    print "First thing we are going to do is load an image. Try it yourself:"
    print lb

    cmd = "logo = Image(\"simplecv\")"
    desired_tuple = ('logo', Image)
    command_loop(cmd, desired_tuple)
   
  #  while True:
  #      print "logo = Image(\"simplecv\")"
  #      print lb

  #      if attempt("logo", Image):
  #          break
  #      
  #      print lb
  #      print "Oops! 'logo' is still not an Image!" 
  #      print lb

    print "Correct! You just loaded SimpleCV logo into memory."
    print "Let's try it to use one of your images. There are different ways to"
    print "do that. You can try, for example:"
    print lb
    print "img = Image(URL_TO_MY_PICTURE) or img = Image(PATH_TO_MY_PICTURE)"
    print lb
    cmd =  "Example: img = Image('http://simplecv.org/images/logo.gif')"
    
    desired_tuple = ('img', Image)
    command_loop(cmd, desired_tuple)

    print "Perfect! Now we want to see it:"
    print lb
    cmd = "img.show()"
    print cmd
    print lb

    while True:
        if prompt_and_run().endswith('.show()'):
            break

    return

def tutorial_save():
    shellclear()
    print "Once you have an Image Object loaded in memory you can"
    print "now save it to disk.  If you don't or don't know how then"
    print "you can run the image tutorial"
    print lb
    raw_input("[Press enter to continue]")
    shellclear()
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

    shellclear()
    print "Correct, you just saved a new copy of the image to /tmp/new.jpg"
    print "as you can see in SimpleCV most of the functions are intuitive"
    print lb
    raw_input("[Press enter to continue]")
    return

def tutorial_copy():
    shellclear()
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
    shellclear()
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
    shellclear()
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
    shellclear()
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
    shellclear()
    print "Correct, you just returned a 5 pixel by 5 pixel image object"
    print lb
    return

def tutorial_corners():
    shellclear()
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
    shellclear()
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
    shellclear()
    print "Correct, you just returned a featureset object which contains"
    print "feature objects.  These feature objects contain data from the"
    print "found corners"
    print lb
    return

      
def magic_tutorial(self,arg):
    if (arg == ""):
        shellclear()
        print "+--------------------------------+"
        print " Welcome to the SimpleCV tutorial "
        print "+--------------------------------+"
        print lb
        print "At anytime on the SimpleCV Interactive Shell you can type tutorial,"
        print "then press the tab key and it will autocomplete any tutorial that"
        print "is currently available."
        print lb
        print "Let's start off with Loading and Saving images!"
        print lb
        print lb
        raw_input("[Press enter to continue]")
        tutorial_image()
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
