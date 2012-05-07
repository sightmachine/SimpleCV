#!/usr/bin/python

from SimpleCV import * 


disp = Display((800,600))
cam = Camera(1)
scale_f = 0.4
while disp.isNotDone():
    img = cam.getImage().scale(scale_f)
    binary = img.colorDistance(Color.WHITE).binarize().invert().dilate(4)
    blobs = img.findBlobsFromMask(binary)


myset = ImageSet("./legos")
i = 0
for m in myset:
    t = m.scale(.4)
    mask = t.colorDistance(Color.WHITE).binarize().invert().dilate(4)
    blobs = t.findBlobsFromMask(mask)
    if( len(blobs) > 0 ):
        h = blobs[-1].hullImage()
        h = h.rotate(blobs[-1].angle())
        mask = h.threshold(1).dilate(5)
        b2 = h.findBlobsFromMask(mask, threshold=1)
        if( b2 is not None):
           h2 = b2[-1].hullImage()
           h3 = h2.crop( 20,20, h2.width-40,h2.height-40)
           h4 = h3.pixelize((h3.width/4,h3.height/4))
           result = t.sideBySide(h3.sideBySide(h4)).scale(.5)
           ofn = "result"+str(i)+".png"
           result.save(ofn)
           result.show()
           i = i + 1
        time.sleep(1)
    
   
    
