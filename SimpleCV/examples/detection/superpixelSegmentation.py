"""
This example shows the usage of superpixel segmentation. It shows
how each segmented superpixel individually. And also shows the usage
of colorWithClusterMeans() functions which draws superpixel in its
mean color
"""
print __doc__

from SimpleCV import Image
import time

img = Image("lenna")
sp = img.segmentSuperpixels(300, 30)
for superpixel in sp:
    superpixel.image.show()
    time.sleep(0.1)

sp.show()
time.sleep(3)
sp.colorWithClusterMeans().show()
time.sleep(3)