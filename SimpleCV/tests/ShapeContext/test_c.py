from SimpleCV import *

color = Color()
img = Image('JeepGood.png')
img = img.invert()
img2 = Image('JeepGood.png')
img2 = img2.invert()
#img2 = img2.resize(img.width,img.height)

blobs = img.findBlobs()
blobs2 = img2.findBlobs()



confuse = []

# fs = blobs[0].getShapeContext()
# fs.draw()
# img.show()
# time.sleep(20)
i = 0
for b in blobs:
    for d in blobs2:
        metric =  b.getMatchMetric(d)
        result = b.showCorrespondence(d,'bottom')
        title = "Match Quality: " + str(metric)
        result.drawText(title,20,20,color=Color.RED,fontsize=42)
        result.show()
        fname = "SanityCheckExample"+str(i)+".png"
        i = i+ 1
        result.save(fname)
        print "------------------------------"
        print metric
        confuse.append(metric)

print confuse

confuse = np.array(confuse)


print confuse.reshape(4,4)

time.sleep(10)
