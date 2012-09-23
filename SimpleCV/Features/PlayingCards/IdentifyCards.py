from SimpleCV import *
import sys, traceback
from CardUtil import *
from PlayingCardFactory import *
import numpy as np


cam = Camera()
pcf = PlayingCardFactory()
while True:
    img = cam.getImage()
    result = pcf.process(img)
    if( result is not None ):
        result.draw()
        if( result[0].rank is not None and result[0].suit is not None):
            str = "RANK: "+result[0].rank+" SUIT: "+result[0].suit
            img.drawText(str,10,10,color=Color.RED,fontsize=32)
    if(img is not None):
        img.show()
    time.sleep(.1)