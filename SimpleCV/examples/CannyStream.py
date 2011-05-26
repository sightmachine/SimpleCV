#!/usr/bin/python 
from SimpleCV import *

"""
This is a simple demo which uses the up/down and left/right keyboard arrows
to show the thresholds of the edges() function.  
"""



import sys, curses
#start values for the edges function

def main(stdscr):
  stdscr.nodelay(1)
  t1 = 50 
  t2 = 100 
  cam = Camera()
  js = JpegStreamer()

  while (1):
    c = stdscr.getch() 
    if (c != -1):
        if (c == 259):
          t1 += 5
        elif (c == 258):
          t1 -= 5
        elif (c == 260):
          t2 -= 5
        elif (c == 261):
          t2 += 5

	if (t1 < 0):
          t1 = 0
        if (t2 < 0):
          t2 = 0

        stdscr.addstr(str(int(c)))
	stdscr.addstr("t1: " + str(t1) + ", t2 "+ str(t2) + "\n")
        stdscr.refresh()
	stdscr.move(0, 0)

    cam.getImage().flipHorizontal().edges(t1, t2).invert().save(js.framebuffer)
		 

if __name__ == '__main__':
  curses.wrapper(main)
