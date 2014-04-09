import numpy as np
import cv2
import time
from SimpleCV.Camera import VimbaCamera


def printPrettyHeader(msg):
    print "*"*80 + "\n* %s *\n" % msg + "*"*80

def _getProperty(c):
    printPrettyHeader("Test getProperty")

    prop = "ExposureMode"
    print "%s=%s" % (prop, c.getProperty(prop))

def _getAllProperties(c):
    printPrettyHeader("Test getAllProperties")

    allprops = c.getAllProperties()
    for k in sorted(allprops.iterkeys()) :
        print "%s=%s" % (k,allprops[k])

def _setProperty(c):
    printPrettyHeader("Test setProperty (toggle AcquisitionMode)")

    prop = "AcquisitionMode"
    val = c.getProperty(prop)
    print "BEFORE: %s=%s" % (prop, val)
    newval = "Continuous" if val == "SingleFrame" else "SingleFrame"
    print "newval=%s" % newval
    c.setProperty(prop, "Continuous")
    time.sleep(0.2)
    val = c.getProperty(prop)
    print "AFTER: %s=%s" % (prop, val)

def _setupASyncMode(c):
    printPrettyHeader("Test setupASyncMode (toggle TriggerSource)")

    prop1 = 'AcquisitionMode'
    prop2 = 'TriggerSource'    
    print 'BEFORE: %s=%s, %s=%s' % (prop1, c.getProperty(prop1), prop2, c.getProperty(prop2))
    c.setupASyncMode()
    print 'AFTER: %s=%s, %s=%s' % (prop1, c.getProperty(prop1), prop2, c.getProperty(prop2))

def _setupSyncMode(c):
    printPrettyHeader("Test setupSyncMode (toggle TriggerSource)")

    prop1 = 'AcquisitionMode'
    prop2 = 'TriggerSource'    
    print 'BEFORE: %s=%s, %s=%s' % (prop1, c.getProperty(prop1), prop2, c.getProperty(prop2))
    c.setupSyncMode()
    print 'AFTER: %s=%s, %s=%s' % (prop1, c.getProperty(prop1), prop2, c.getProperty(prop2))

def _getImage(c):
    printPrettyHeader("Test getImage")

    img = c.getImage()
    img.save("test_getImage_scv.png")
    print "test_getImage_scv.png saved"

def _runCommand(c):
    printPrettyHeader("Test runCommand")
    vimbacam = c._camera
    f = vimbacam.getFrame()    # creates a frame
    f.announceFrame()
        
    vimbacam.startCapture()
    f.queueFrameCapture()
    c.runCommand("AcquisitionStart")
    c.runCommand("AcquisitionStop")
    f.waitFrameCapture(1000)
    moreUsefulImgData = np.ndarray(buffer = f.getBufferByteData(),
             dtype = np.uint8,
             shape = (f.height, f.width, 1))
    rgb = cv2.cvtColor(moreUsefulImgData, cv2.COLOR_BAYER_RG2RGB)
    vimbacam.endCapture()
    cv2.imwrite('test_runCommand.png', rgb)
    print "test_runCommand.png saved"

def _listAllCameras(c):
    printPrettyHeader("Test listAllCameras")

    l = c.listAllCameras()
    for i in l:
        print 'Camera Id=%s' % i.cameraIdString

def test_all():
    c = VimbaCamera()
    _getProperty(c)
    _getAllProperties(c)
    _setProperty(c)
    _setupASyncMode(c)
    _setupSyncMode(c)

    _getImage(c)
    _runCommand(c)
    _listAllCameras(c)

