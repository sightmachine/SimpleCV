import numpy as np
import cv2
import time
from SimpleCV.Camera import VimbaCamera, AVTCamera
from SimpleCV import Display

#c = VimbaCamera(0, threaded=True) # async
#time.sleep(0.2)

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

def _takeManyVimbaShots(idx):
    c = VimbaCamera()
    print "_takeManyVimbaShots %d" % idx

    _takeShots(c, 10, "cam_vimba%d" % idx)

def _takeAVTManyShots(idx):
    c = AVTCamera()
    print "_takeAVTManyShots %d" % idx

    _takeShots(c, 10, "cam_avtnative%d" % idx)

#_takeAVTManyShots(1)
#_takeAVTManyShots(2)
#_takeManyVimbaShots(1)
#_takeManyVimbaShots(2)

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


def test_createManyCameras():
    printPrettyHeader("Test createManyCameras")
    numIter = 10 #1000
    for i in range(numIter):
        _takeManyVimbaShots(i)

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

def test_takeManyShots():
    c = VimbaCamera()
    printPrettyHeader("Test takeManyShots")

    _takeShots(c, 5, "vimba")

def test_AVT_takeManyShots():
    c = AVTCamera()
    printPrettyHeader("Test AVT_takeManyShots")

    _takeShots(c, 5, "avtnative")

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
