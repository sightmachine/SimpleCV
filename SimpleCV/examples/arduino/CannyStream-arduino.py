#!/usr/bin/python 
"""
This is a simple demo that interfaces with the Arduino. To use it you have to have
the standard firmata firmware running on the arduino itself.
This should be built into the arduino IDE but if you need help:
http://firmata.org

You will also need pyfirmata installed:
http://bitbucket.org/tino/pyfirmata


Once they are installed you also have to verify the USB location of the Arduino.
On linux it is typically:
/dev/ttyUSBO

but the Arduino IDE should tell you where you should mount the arduino from.

"""

print __doc__

from SimpleCV import *
import sys, curses, time
from pyfirmata import Arduino, util


board = Arduino('/dev/ttyUSB0') #the location of the arduino
analog_pin_1 = board.get_pin('a:1:i') #use pin 1 of the arduino as input
analog_pin_2 = board.get_pin('a:2:i') #use pin 2 of the arduino as input
button_13 = board.get_pin('d:13:i') #use pin 13 of the arduino for button input

it = util.Iterator(board) # initalize the pin monitor for the arduino
it.start() # start the pin monitor loop

multiplier = 400.0 # a value to adjust the edge threshold by
cam = Camera() #initalize the camera

while True:
  t1 = analog_pin_1.read() # read the value from pin 1
  t2 = analog_pin_2.read() # read the value from pin 2
  b13 = button_13.read() # read if the button has been pressed.

  if not t1: #Set a default if no value read
    t1 = 50 
  else:
    t1 *= multiplier 

  if not t2: # set a default if no value read
    t2 = 100 
  else:
    t2 *= multiplier

  print "t1 " + str(t1) + ", t2 " + str(t2) + ", b13 " + str(b13)
  cam.getImage().flipHorizontal().edges(int(t1), int(t2)).invert().smooth().show()
  time.sleep(0.01)
   


