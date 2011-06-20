#Define cheatsheet
#
from subprocess import call
import platform

lb = "\n" #linebreak
tb = "\t" #tab

def clear():
  if platform.system() == "Windows":
    return
  call("clear")

def magic_cheatsheet(self,arg):
  if(arg == ""):
    clear()
    print "+///////////////    SimpleCV Cheatsheet   ///////////////////+"
    print "-------------------------------------------------------------"
    print "Variables"
    print "-------------------------------------------------------------"
    print "who - brings up list of known variables"
    print "psearch varname int - returns the variable starting with varname* of type int"
    print "store var - allows setting of a variable and its value to ipython profile"
    print "store var > /tmp/a.txt  - set a variable's value into a file"
    print "store - no arguments shows all the stored variables with their values "
    print "reset - deletes all the stored variables held by SimpleCV shell"
    print "store -r  - recovers the previously held variable names"
    print "store -z whacks held variables completely."
    print ""
    print "-------------------------------------------------------------"
    print "Logging:"
    print "-------------------------------------------------------------"
    print "logstate - reports status of ipython logging (writes to ipython_log.py as default)"
    print "logstart - starts logging of session"
    print "logon - starts logging"
    print "logoff - toggles logging off"
    print "p is shorthand for print -> p sys.path"
    print "page - pretty prints -> page sys.path"
    print ""
    print "-------------------------------------------------------------"
    print "Help System"
    print "-------------------------------------------------------------"
    print "iPython integrates with pydocs system"
    print "help(sys)"
    print "help('for')  help on keyword"
    print "help('FOR') - caps shows you the topic"
    print "help() - takes you to help subsystem"
    print "  type topics and it brings up a list of topics to get help on"
    print "help TOPIC label"
    print ""
    print "-------------------------------------------------------------"
    print "Command History"
    print "-------------------------------------------------------------"
    print "[15]  is the number in the iPython history caching"
    print "_i - shows last command"
    print "_ii - shows two commands back"
    print "_i1 - shows first command"
    print "In[3] - global variable that shows third command"
    print "hist - shows last 20 or so history"
    print "hist 1 10 - shows range of last 10 commands"
    print "hist 10 - last 10 commands"
    print "del varname - removes it from namespace"
    print "exec _i3 - executes the third command in history list"
    print "exec In[1:4] - execute the commands in the range in the list"
    print ""
    print "-------------------------------------------------------------"
    print "Alias command history"
    print "-------------------------------------------------------------"
    print "macro my_macro 1-4 5"
    print "- - Can now type begin and it executes the defined history"
    print "run my_macro - will run the macro you created"
    print "save my_macro 1-3 - saves off the 3 lines of history to the file my_macro.py"
    print ""
    print ""
    print ""
    
