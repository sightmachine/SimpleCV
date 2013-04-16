#!/usr/bin/python
'''
This example illustrates the smartRotate Function in Image class.
'''
print __doc__

import time

from SimpleCV import *

tilted = Image('tilted_glass.jpg',sample = True )
aligned = tilted.smartRotate()
final = tilted.sideBySide(aligned)

print "It's a miracle"
final.show()
time.sleep(2)

