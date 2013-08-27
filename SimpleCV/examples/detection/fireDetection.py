'''
This is how to detect fire in an image using CIELAB colorspace using SimpleCV
'''
print __doc__

from SimpleCV import Image

img = Image("fireexample.jpg", sample=True)
labimg = img.toLAB()
lmean = 160
amean = 135
bmean = 180

l, a, b = labimg.splitChannels()

l1 = l.threshold(lmean)
a1 = a.threshold(amean)
b1 = b.threshold(bmean)

threshImg = a1 <= b1 
finImg = l1 & a1 & b1 & threshImg
finImgC = img & finImg
finImgC.show()