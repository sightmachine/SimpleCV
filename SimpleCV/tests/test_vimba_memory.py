import gc
# From bytes.com/topic/python/answers/22097-hunting-memory-leak

import time
from SimpleCV.Camera import VimbaCamera, AVTCamera

"""
# at the beginning of code
gc.enable()
gc.set_debug(gc.DEBUG_LEAK)
"""

def printPrettyHeader(msg):
    print "*"*80 + "\n* %s *\n" % msg + "*"*80

def _takeShots(cam, numPics, filename):
    start = time.time()
    #print "Taking %d photos..." % numPics
    for i in range(numPics):
        img = cam.getImage()
        #if (i % 1000 == 0):
        #    img.save("%s_%d.png" % (filename, i))
    end = time.time()
    elapsed = end - start
    print "Took %f seconds" % elapsed

def test_takeManyShots(idx):
    c = VimbaCamera()
    #printPrettyHeader("Test takeManyShots %d" % idx)
    print "Test takeManyShots %d" % idx

    _takeShots(c, 1, "vimba%d" % idx)

def test_takeAVTManyShots(idx):
    c = AVTCamera()
    printPrettyHeader("Test takeAVTShots %d" % idx)

    _takeShots(c, 1, "avtnative%d" % idx)

#test_takeAVTManyShots(1)
#test_takeAVTManyShots(2)
#test_takeManyShots(1)
#test_takeManyShots(2)

def test_createManyCameras():
    printPrettyHeader("Test createManyCameras")
    numIter = 1000
    for i in range(numIter):
        test_takeManyShots(i)

test_createManyCameras()

"""
########################################################################3
# at the end of code:
print "\nGARBAGE:"
gc.collect()

print "\nGARBAGE OBJECTS:"
for x in gc.garbage:
    s = str(x)
    print type(x),"\n",s
"""