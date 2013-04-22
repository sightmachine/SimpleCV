from SimpleCV import *

color = Color()
img = Image('badge.png')
img = img.invert()
blobs = img.findBlobs()
img2 = Image('deformed.png')
img2 = img2.invert()
blobs2 = img2.findBlobs()

for j in range(0,len(blobs)):
    data = blobs[j].ShapeContextMatch(blobs2[j])
    mapvals = data[0]
    fs1 = blobs[j].getShapeContext()
    fs1.draw()
    fs2 = blobs2[j].getShapeContext()
    fs2.draw()

img2 = img2.applyLayers()
img = img.applyLayers()
img3 = img.sideBySide(img2,'bottom')

for j in range(0,3):
    data = blobs[j].ShapeContextMatch(blobs2[j])
    mapvals = data[0]
    for i in range(0,len(blobs[j]._completeContour)):
    #img3.clearLayers()
        lhs = blobs[j]._completeContour[i]
        idx = mapvals[i];
        rhs = blobs2[j]._completeContour[idx[0]]
        rhsShift = (rhs[0],rhs[1]+img.height)
        img3.drawLine(lhs,rhsShift,color=color.getRandom(),thickness=1)
        img3.show()
