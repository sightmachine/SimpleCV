#!/usr/bin/env python

import sys
import os
from SimpleCV import *

def threedee_me(left, right, offset):
    (r,g,b)=left.splitChannels()
    left_blue = left.mergeChannels(None,b,g);
    #left_blue.save("blue.png", sample=True)
    (r,g,b) = right.splitChannels()
    right_red = right.mergeChannels(r,None,None);
    #right_red.save("red.png", sample=True)
    sz = (left.width+offset[0],left.height+offset[1])
    output = left_blue.embiggen(size=sz,pos=(0,0))
    output = output.blit(right_red,alpha=0.5,pos=offset)
    output = output.crop(offset[0],y=offset[1],w=left.width-offset[0],h=left.height-offset[1])
    return output

print "Taking pictures. Please move your camera slightly to its right"
print "after every picture."

c = Camera()
time.sleep(1)
images = []

for i in range(5):
    images.append(c.getImage())
    print "Picture %d taken" % (i + 1)
    time.sleep(1)

offset = (0,0)

for i in range(4):
    left = images[i]
    right = images[i+1]
    output = threedee_me(left, right, offset)
    print output.save(temp = True)
    output.show()
    time.sleep(2)

