from SimpleCV import *
img = Image('lenna')

img1 = img.toYCrCb()
if (img1.isYCrCb()):
    print "Converted to YCrCb\n"

img1 = img.toBGR()
img2 = img1.toYCrCb()
if (img2.isYCrCb()):
    print "Converted BGR to YCrCb\n"

img1 = img.toHLS()
img2 = img1.toYCrCb()
if (img2.isYCrCb()):
    print "Converted HLS to YCrCb\n"

img1 = img.toHSV()
img2 = img1.toYCrCb()
if (img2.isYCrCb()):
    print "Converted HSV to YCrCb\n"

img1 = img.toXYZ()
img2 = img1.toYCrCb()
if (img2.isYCrCb()):
    print "Converted XYZ to YCrCb\n"

img1 = img.toYCrCb()
img2 = img1.toRGB()
if (img2.isYCrCb()):
    print "Converted from YCrCb to RGB\n"

img1 = img.toYCrCb()
img2 = img1.toBGR()
if (img2.isRGB()):
    print "Converted from YCrCb to RGB\n"

img1 = img.toYCrCb()
img2 = img1.toHLS()
if (img2.isHLS()):
    print "Converted from YCrCb to HLS\n"

img1 = img.toYCrCb()
img2 = img1.toHSV()
if (img2.isHSV()):
    print "Converted from YCrCb to HSV\n"

img1 = img.toYCrCb()
img2 = img1.toXYZ()
if (img2.isXYZ()):
    print "Converted from YCrCb to XYZ\n"

img1 = img.toGray()
img2 = img1.toGray()
if (img2.isGray()):
    print "Converted from Gray to Gray\n"
