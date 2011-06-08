#!/usr/bin/python 
from SimpleCV import *

"""
This class can be used to quickly calibrate a camera 
"""

import sys, curses
#start values for the edges function

def main(stdscr):
  stdscr.nodelay(1)
  cam = Camera()
  js = JpegStreamer()

  baseName = "CalibImage"
  ext = ".png"
  count = 0
  quit = False
  imgList = []
  while (quit == False):
    img = cam.getImage()
    grid = cam.markCalibrationGrid(img,dimensions=(5,8))
    c = int(stdscr.getch())
    if( c == 113 ):
      quit = True
    elif( c == 32 ):
      fname = baseName+str(count)+ext
      img.save(fname)
      imgList.append(img)
      count = count + 1
      print("Saved "+fname+"\n")
    elif( c == 99 ):
      #print("Calibrate!\n")      
      m = cam.calibrate(imgList,dimensions=(5,8))
      cam.saveCalibration("Default")
      print(m)

    stdscr.addstr(str(c))
    stdscr.refresh()
    stdscr.move(0, 0)

    grid.save(js.framebuffer)
		 
  stdscr.keypad(0)
  curses.echo()
  curses.nocbreak()
  curses.endwin()

if __name__ == '__main__':
  curses.wrapper(main)
