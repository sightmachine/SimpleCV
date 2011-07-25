#!/usr/bin/python 
from SimpleCV import *
morphology = Image('../sampleimages/blockhead.png')
chull = Image('../sampleimages/chull.png')
deep = Image('../sampleimages/test.png')
hard = Image('../sampleimages/test.png')
bm = BlobMaker()
morphology.binarize(thresh=10).invert().save("DERP.png")
#ZOMG! NEW RULE ALL BLOBS ARE WHITE, ALWAYS AND FOREVER AMEN
test = bm.extractFromBinary(morphology.binarize(thresh=10).invert(),morphology)
print(len(test))
i = 0
blobLayer = DrawingLayer((morphology.width,morphology.height))
resultLayer = DrawingLayer((morphology.width,morphology.height))
test.reverse()
for b in test:
    b.drawMaskedToLayer(blobLayer)
    b.draw(alpha=128,w=4,color=Color.AQUAMARINE)
    b.drawHoles(alpha=128,w=4,color=Color.BLUE)
    name = "Blob"+str(i)+".png"
    b.mImg.save(name)
    print(name)
    #if( b.mHoleContour is not None):
    #    for h in b.mHoleContour:
    #        print("     "+str(h))
    #        blobLayer.polygon(h,color=Color.RED, width=2, antialias=False )
    #blobLayer.polygon(b.mConvexHull, color=Color.GREEN, width=2,antialias=False)
    i = i + 1
morphology.save('DidItDraw.png')
morphology.addDrawingLayer(blobLayer)
morphology.save('blob_ouput.png')
morphology.clear()
morphology.clearLayers()
morphology.addDrawingLayer(blobLayer)
morphology.save('redrawn.png')