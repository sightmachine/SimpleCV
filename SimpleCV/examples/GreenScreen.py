from SimpleCV import *
from SimpleCV.Display import Display, pg
import time

gs = Image("./../sampleimages/greenscreen.png")
gs.show()
time.sleep(5)
background = Image("./../sampleimages/icecave.png")
background.show()
time.sleep(5)
matte = gs.hueDistance(color=Color.GREEN, minvalue = 40).binarize()
matte.show()
time.sleep(5)
result = (gs-matte)+(background-matte.invert())
result.show()
time.sleep(5)
result.save('result.png')

