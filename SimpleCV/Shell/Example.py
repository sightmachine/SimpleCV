#!/usr/bin/python 
import os
import glob
from SimpleCV import *


def listFiles():
	files = []
	for dirname, dirnames, filenames in os.walk('./SimpleCV/examples'):
		for subdirname in dirnames:
			#print os.path.join(dirname, subdirname)
			filenames = [ fi for fi in filenames if fi.endswith(".py") ]
			for filename in filenames:
				#print os.path.join(dirname, filename)
				files.append(filename.replace(".py",""))

	return files

def magic_examples(self, arg):
	HOMEDIR = os.getcwd()
	files = listFiles()

	if(arg.lower() == "list"):
		for file in files:
			print file
		
	elif(arg == ""):
		print "To use examples type:"
		print "example name"
		print ""
		print "to see which examples are available type:"
		print "example list"
		print ""
        
	elif(arg in files):
		os.chdir("./SimpleCV/examples")
		try:
			__import__(arg)
		except ImportError:
			print "Error: can't run example: " + arg
		
		os.chdir(HOMEDIR)
	elif(arg.lower() == "joshua"):
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
		print "Example: " + arg + " does not exist, or an error occured"
			
