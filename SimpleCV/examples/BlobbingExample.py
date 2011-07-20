#!/usr/bin/python 
from SimpleCV import *
morphology = Image('../sampleimages/hardblob.png')
chull = Image('../sampleimages/chull.png')
deep = Image('../sampleimages/test.png')
hard = Image('../sampleimages/test.png')
bm = BlobMaker()
morphology.binarize(thresh=10).invert().save("DERP.png")
#ZOMG! NEW RULE ALL BLOBS ARE WHITE, ALWAYS AND FOREVER AMEN
test = bm.extractFromBinary(morphology.binarize(thresh=10).invert(),morphology,doImg=True)
print(len(test))
i = 0
blobLayer = DrawingLayer((morphology.width,morphology.height))
for b in test:
    name = "Blob"+str(i)+".png"
    b.mImg.save(name)
    print(b.mContour)
    blobLayer.polygon(b.mContour,color=Color.RED, filled=True)
    blobLayer.polygon(b.mConvexHull, color=Color.GREEN, width=2,antialias=False)
    i = i + 1

morphology.addDrawingLayer(blobLayer)
morphology.save('blob_ouput.png')