from SimpleCV import *
img = Image('../sampleimages/9dots4lines.png')
t=img.upload('flickr','ccfa805e5c7693b96fb548fa0f7a36da','db1479dbba974633')
print t
img = Image('../sampleimages/barcode.png')
t=img.upload('flickr')
print t
img = Image('../sampleimages/circles.png')
t=img.invert().upload('flickr')
print t
