#!/usr/bin/env python

import sys
import os
from SimpleCV import *

offset = (0,0)
left = Image("left.png")
right = Image("right.png")
(r,g,b)=left.splitChannels()
left_blue = left.mergeChannels(None,b,g);
left_blue.save("blue.png")
(r,g,b) = right.splitChannels()
right_red = right.mergeChannels(r,None,None);
right_red.save("red.png")
sz = (left.width+offset[0],left.height+offset[1])
output = left_blue.embiggen(size=sz,pos=(0,0))
output = output.blit(right_red,alpha=0.5,pos=offset)
output = output.crop(offset[0],y=offset[1],w=left.width-offset[0],h=left.height-offset[1])
output.save("threedee.png");
