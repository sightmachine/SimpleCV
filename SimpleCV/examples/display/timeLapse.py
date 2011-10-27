#!/usr/bin/python 
from SimpleCV import *

import sys, time, socket
import curses # Using curses for async keyboard input

scr = curses.initscr() #init
curses.cbreak() #curses setup
scr.nodelay(1)  #tell curses to use non-blocking input

#settings for the project
path  = ""     #Path for output files
fname = "TimeLapse" #File base name
ext = ".jpg"     #File extension
frame = 0;
sTime = 1; # time, in s, between captures

#Create the camera
cam = Camera()

NotDone = 1 # break boolean
while(NotDone):
  c = scr.getch() #get the last key input
  if c == ord('q'): #q means quit
      NotDone = 0
  img = cam.getImage() #get image
  fileName = path + fname + str(frame) + ext #make file name
  scr.addstr(fileName+'\n') # curses requires us to use a different print mechanism
  img.save(fileName) # save the output
  frame = frame + 1
  time.sleep(sTime)#sleep

curses.nocbreak() #cleanup curses
curses.endwin()
exit(0)
