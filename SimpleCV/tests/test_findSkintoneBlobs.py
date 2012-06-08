import SimpleCV as sv
import time
img = sv.Image('./standard/04001.jpg')
blobs = img.findSkintoneBlobs()
img.show()
time.sleep(3)
img.crop(blobs[-1]).show()
time.sleep(3)
img = sv.Image('./standard/04000.jpg')
blobs = img.findSkintoneBlobs()
img.show()
time.sleep(3)
img.crop(blobs[-1]).show()
time.sleep(3)
