#!/usr/bin/env python

import sys
import os
from SimpleCV import *

offset = (60,0)
left = Image("left.png")
right = Image("right.png")
(r,g,b)=left.splitChannels()
left_blue = left.mergeChannels(None,g,b);
(r,g,b) = right.splitChannels()
right_red = right.mergeChannels(r,g,None);
sz = (left.width+offset[0],left.height+offset[1])
output = left_blue.embiggen(size=sz,pos=(0,0))
output = output.blit(right_red,alpha=0.5,pos=offset)
output = output.crop(offset[0],y=offset[1],w=left.width-offset[0],h=left.height-offset[1])
output.save("threedee.png");
