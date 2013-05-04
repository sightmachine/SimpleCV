#!/usr/bin/python
import os
import glob
from subprocess import call
from SimpleCV import *
import sys


def listFiles(directory):
    for path, dirs, files in os.walk(directory):
        for f in files:
            yield os.path.join(path, f)


def magic_examples(self, arg):
    DIR = os.path.join(LAUNCH_PATH, 'examples')
    files = [f for f in listFiles(DIR) if f.endswith('.py')]
    file_names = [file.split('/')[-1] for file in files]
    iarg = None
    arg = str(arg)

    try:
        iarg = int(arg)
    except:
        pass

    if isinstance(arg, str) and arg == "":
        counter = 0
        print "Available Examples:"
        print "--------------------------------------------"
        for file in file_names:
            print "[",counter,"]:",file
            counter += 1

        print "Just type example #, to run the example on the list"
        print "for instance: example 1"
        print ""
        print "Close the window or press ctrl+c to stop the example"

    elif isinstance(iarg, int):
        print "running example:", files[iarg]
        try:
            call([sys.executable, files[iarg]])
        except:
            print "Couldn't run example:", files[iarg]


    elif isinstance(arg, str) and arg.lower() == "joshua":
        print "GREETINGS PROFESSOR FALKEN"
        print ""
        print "HELLO"
        print ""
        print "A STRANGE GAME."
        print "THE ONLY WINNING MOVE IS"
        print "NOT TO PLAY."
        print ""
        print "HOW ABOUT A NICE GAME OF CHESS?"
        print ""


    else:
        print "Example: " + arg + " does not exist, or an error occurred"
