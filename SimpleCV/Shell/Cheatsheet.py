#Define cheatsheet
#
from subprocess import call

lb = "\n" #linebreak
tb = "\t" #tab

def clear():
  call("clear")


def magic_cheatsheet(self,arg):
  if(arg == ""):
    clear()
    print "SimpleCV Cheatsheet"
    print "+-----------------------------------------------------------+"
    print ""
    print ""

    
