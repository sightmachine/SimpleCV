from SimpleCV import *

color = Color()
img = Image('logotest1.png')
img = img.invert()
blobs = img.findBlobs()
img2 = Image('logotest6.png')
img2 = img2.invert()
blobs2 = img2.findBlobs()
data = blobs[0].ShapeContextMatch(blobs2[0])
mapvals = data[0]
fs1 = blobs[0].getShapeContext()
fs1.draw()
img = img.applyLayers()
fs2 = blobs2[0].getShapeContext()
fs2.draw()
img2 = img2.applyLayers()
img3 = img.sideBySide(img2)

for i in range(0,len(blobs[0]._completeContour)):
    #img3.clearLayers()
    lhs = blobs[0]._completeContour[i]
    idx = mapvals[i];
    rhs = blobs2[0]._completeContour[idx[0]]
    rhsShift = (rhs[0]+img.width,rhs[1])
    img3.drawLine(lhs,rhsShift,color=color.getRandom(),thickness=1)
    img3.show()
    time.sleep(0.01)

