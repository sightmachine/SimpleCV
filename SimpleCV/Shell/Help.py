#This is the help system for the SimpleCV shell

from SimpleCV import *
from subprocess import call
import platform

lb = "\n" #linebreak
tb = "\t" #tab

def clear():
  if platform.system() == "Windows":
    return
  call("clear")

#Command to define the help system
def magic_help(self,arg):
  
  if(arg == ""):
    clear()
    print "To use help just type:"
    print "simplehelp command"
    print ""
    print "List of commands available are:"
    print "image"
    print "feature"
    print "featureset"
    print "camera"
    print ""
    print ""

    
  elif(arg.lower() == "image"):
    clear()
    print Image.__doc__

  elif(arg.lower() == "feature"):
    clear()
    print Feature.__doc__

  elif(arg.lower() == "featureset"):
    clear()
    print FeatureSet.__doc__
    
  elif(arg.lower() == "joshua"):
      clear()
      print "Greetings Professor Falken"
      print ""
      print "Hello"
      print ""
      print "A Strange Game."
      print "The only winning move is"
      print "not to play."
      print ""
      print "How about a nice game of chess?"
      print ""
        
  elif(arg.lower() == "camera"):
    clear()
    print Camera.__doc__

  else:
    print "No help available for: " + arg.upper()

#TODO:
#expand on this section
