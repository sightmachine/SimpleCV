import numpy as np
import cv2
import time
from SimpleCV.Camera import VimbaCamera, AVTCamera
from SimpleCV import Display
from pymba import Vimba

def printPrettyHeader(msg):
    print "*"*80 + "\n* %s *\n" % msg + "*"*80

def _takeShots(cam, numPics, filename):
    start = time.time()
    #print "Taking %d photos..." % numPics
    for i in range(numPics):
        img = cam.getImage()
        img.save("%s_%d.png" % (filename, i))
    end = time.time()
    elapsed = end - start
    print "Took %f seconds" % elapsed

'''
def test_AVT_threaded_getImage():
    printPrettyHeader("Test AVT_threaded_getImage")
    c = AVTCamera(threaded=True)
    time.sleep(0.2)
    img = c.getImage()
    img.save("avt.png")
'''

def test_Vimba_threaded_getImage():
    printPrettyHeader("Test Vimba_threaded_getImage")
    c = VimbaCamera(threaded=True)
    time.sleep(0.2)
    img = c.getImage()
    img.save("vimba.png")

    time.sleep(0.2)

    c.shutdown()
