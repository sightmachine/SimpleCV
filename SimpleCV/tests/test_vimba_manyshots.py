import numpy as np
import cv2
import time
from SimpleCV.Camera import VimbaCamera, AVTCamera
from SimpleCV import Display

#c = VimbaCamera(0, threaded=True) # async
#time.sleep(0.2)

def printPrettyHeader(msg):
    print "*"*80 + "\n* %s *\n" % msg + "*"*80

"""
def test_getImageDisplay():
    c = VimbaCamera()
    printPrettyHeader("Test getImage")

    img = c.getImage()
    display = Display()
    img.save(display)
    img.save("test_getImage_scv_display2.png")
    print "test_getImage_scv_display2.png saved"
"""

def _takeShots(cam, numPics, filename):
    start = time.time()
    print "Taking %d photos..." % numPics
    for i in range(numPics):
        img = cam.getImage()
        if (i % 100 == 0):
            print "At %d" % i
        #img.save("%s_%d.png" % (filename, i))
    end = time.time()
    elapsed = end - start
    print "Took %f seconds" % elapsed

"""
def test_oneGrayShot():
    c = VimbaCamera(properties={"mode":"gray"})
    printPrettyHeader("Test oneGrayShot")

    img = c.getImage()
    img.save("test_oneGrayShot.png")

def test_oneShot():
    c = VimbaCamera()
    printPrettyHeader("Test oneShot")

    img = c.getImage()
    img.save("test_oneShot.png")
"""

"""
def test_takeManyShots():
    c = VimbaCamera()
    printPrettyHeader("Test takeManyShots")

    _takeShots(c, 100, "vimba")
"""

def test_makeLotsOfCamera():
    numIter = 1000
    print "Creating %d cameras..." % numIter
    start = time.time()
    for i in range(numIter):
        print "At camera=%d" % i
        cam = VimbaCamera()
        img = cam.getImage()
    end = time.time()
    elapsed = end - start
    print "Took %f seconds" % elapsed

"""
def test_AVT_takeManyShots():
    c = AVTCamera()
    printPrettyHeader("Test AVT_takeManyShots")

    _takeShots(c, 10, "avtnative")
"""