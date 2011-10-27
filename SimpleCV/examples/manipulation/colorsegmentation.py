#!/usr/bin/python

import time
from SimpleCV import *

c = Camera()
i = c.getImage()
cm = ColorModel(i)

d = i.show()
t = int(time.time())
ticks = 0

while not d.isDone():
    cm.threshold(c.getImage()).save(d)
    #~ c.getImage().save(d)
    time.sleep(0.01)
    ticks = ticks + 1
    if (int(time.time()) > t):
      print str(ticks) + " fps"
      ticks = 0
      t = int(time.time())
    
