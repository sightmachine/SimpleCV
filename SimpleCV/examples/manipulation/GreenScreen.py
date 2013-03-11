'''
This program basically functions like a greenscreen that typically
a weather or news reporter would use.  It allows you to super impose
anything standing in front of a "green screen" in front of another image
this should even work with a camera is the user is standing in front
of a green background
'''
print __doc__

from SimpleCV import *

gs = Image("greenscreen.png", sample=True)
gs.show()
time.sleep(5)
background = Image("icecave.png", sample=True)
background.show()
time.sleep(5)
matte = gs.hueDistance(color=Color.GREEN, minvalue = 40).binarize()
matte.show()
time.sleep(5)
result = (gs-matte)+(background-matte.invert())
result.show()
time.sleep(5)
