#!/usr/bin/env python
# 
# Released under the BSD license. See LICENSE file for details.
"""
This is a simple demo that interfaces with the Arduino. To use it you have to
have the standard Firmata firmware running on the Arduino itself.
This should be built into the Arduino IDE but if you need help:
http://firmata.org

You will also need pyfirmata (https://github.com/tino/pyFirmata) installed:
pip install pyfirmata

Once they are installed you also have to verify the USB location of the Arduino.
On linux it is typically: /dev/ttyUSBO or /dev/ttyACM0

but the Arduino IDE should tell you where you should mount the Arduino from.
"""

print __doc__

import time
from SimpleCV import Camera
from pyfirmata import Arduino, util


board = Arduino('/dev/ttyUSB0')  # The location of the Arduino
analog_pin_1 = board.get_pin('a:1:i')  # Use pin 1 as input
analog_pin_2 = board.get_pin('a:2:i')  # Use pin 2 as input
button_13 = board.get_pin('d:13:i')  # Use pin 13 for button input

it = util.Iterator(board)  # Initalize the pin monitor for the Arduino
it.start()  # Start the pin monitor loop

multiplier = 400.0  # A value to adjust the edge threshold by
cam = Camera()  # Initalize the camera

while True:
    t1 = analog_pin_1.read()  # Read the value from pin 1
    t2 = analog_pin_2.read()  # Read the value from pin 2
    b13 = button_13.read()  # Read if the button has been pressed.

    if not t1:  # Set a default if no value read
        t1 = 50 
    else:
        t1 *= multiplier 

    if not t2:  # Set a default if no value read
        t2 = 100
    else:
        t2 *= multiplier

    print "t1 " + str(t1) + ", t2 " + str(t2) + ", b13 " + str(b13)
    img = cam.getImage().flipHorizontal()
    edged_img = img.edges(int(t1), int(t2)).invert().smooth()
    edged_img.show()
    time.sleep(0.1)
