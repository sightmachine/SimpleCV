#!/usr/bin/python

from SimpleCV import *
import time

c = Camera()
vs = VideoStream("foo.avi")

for i in range(0,500):
    c.getImage().edges().invert().save(vs)
    time.sleep(0.05)
