#This is the help system for the SimpleCV shell

from subprocess import call

lb = "\n" #linebreak
tb = "\t" #tab

def clear():
  call("clear")


#Command to define the help system
def magic_help(self,arg):
  if(arg == ""):
    clear()
    print "To use help just type:"
    print "simplehelp command"
    print ""
    print "List of commands available are:"
    print ""
    

  else:
    print "No help available for" + arg.upper()

#TODO:
#expand on this section
