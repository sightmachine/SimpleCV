#!/usr/bin/python

# A Basic SimpleCV interactive shell tutorial

#load required libraries
from scvLibSys import *
from scvLibInc import *
lb = "\n" #linebreak

class Tutorial():
  
  text = None
  
  def __init__(self):
    text = None
    
  def start(self):
    print "??????????????????????????????????"
    print " Welcome to the SimpleCV tutorial "
    print "??????????????????????????????????"
    print lb
    print "at anytime you can type tutorial."
    print "then press the tab key and it will autocomplete any tutorial"
    print "you may need help with."
    print lb
    print "Please press enter to continue"

    cmd = ""
    input(cmd)

    self.image()
    
  def image(self):
    print "please"
