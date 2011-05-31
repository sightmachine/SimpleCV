#!/usr/bin/python 
from SimpleCV import *

"""
This is a simple demo which uses the up/down and left/right keyboard arrows
to show the thresholds of the edges() function.  
"""
import sys, curses, time
#start values for the edges function

from pyfirmata import Arduino, util


def main():
  board = Arduino('/dev/ttyUSB0')

  #starting values

  multiplier = 400.0

  cam = Camera(1)
  js = JpegStreamer()

  analog_4 = board.get_pin('a:4:i')
  analog_5 = board.get_pin('a:5:i')

  it = util.Iterator(board) 
  it.start()

  while (1):
    #print str(analog_5.read()) + "\t\t" + str(analog_4.read())
    t1 = analog_5.read()
    t2 = analog_4.read()

    if not t1: 
      t1 = 50 
    else:
      t1 *= multiplier 

    if not t2: 
      t2 = 100 
    else:
      t2 *= multiplier

    print "t1 " + str(t1) + ", t2 " + str(t2)
    cam.getImage().flipHorizontal().edges(int(t1), int(t2)).invert().smooth().save(js.framebuffer)

    time.sleep(0.01)
		 

main()
