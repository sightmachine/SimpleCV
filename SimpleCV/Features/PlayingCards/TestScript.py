from SimpleCV import *
#from FeatureUtils import *
from CardUtil import *
from PlayingCardFactory import *
#import FeatureUtils
import numpy as np

def GetParallelSets(line_fs,parallel_thresh=25):
    result = []
    sz = len(line_fs)
    #construct the pairwise cross product ignoring dupes
    for i in range(0,sz):
        for j in range(0,sz):
            if( j<=i ):
                result.append(np.Inf)
            else:
                result.append(np.abs(line_fs[i].cross(line_fs[j])))

    result = np.array(result)
    # reshape it
    result = result.reshape(sz,sz)
    # find the lines that are less than our thresh
    l1,l2=np.where(result<parallel_thresh)
    idxs = zip(l1,l2)
    retVal = []
    # now construct the line pairs
    for idx in idxs:
        retVal.append((line_fs[idx[0]],line_fs[idx[1]]))
    return retVal


pcf = PlayingCardFactory()
data,labels = GetFullDataSet()
print len(data)
datapoints = zip(data,labels)
datapoints = datapoints[0:200]
result = []
passing = 0
for d in datapoints:
    img = d[0]
    label = d[1]
#    img = img.crop(img.width/3,0,2*img.width/3,img.height)
    #    img = img.equalize()
    img = img.edges()
    l = img.findLines(threshold=10)
    if( l is not None ):
        v = 70
        h = 30
        vl = l.filter(np.abs(l.angle()) > v)
        vl = vl.filter(vl.length() > img.height/6)
        hl = l.filter(np.abs(l.angle()) < h)
        hl = hl.filter(hl.length() > img.width/8)
        vl.draw(color=Color.RED,width=3)
        hl.draw(color=Color.BLUE,width=3)

#         derp = GetParallelSets(l)
#         color = Color()
#         for d in derp:
# #            img.clearLayers()
#             l.draw(color=Color.RED,width=3)
#         #     l.draw()
#             c = color.getRandom()
#             d[0].draw(color=c,width=3)
#             d[1].draw(color=c,width=3)
#             img.show()

        #top = np.min([8,len(l)])
        #l[-1*top:-1].draw(color=Color.RED,width=3)
        img.show()
        time.sleep(.5)
        #l.show(color=Color.RED,width=3)

    # fs = pcf.process(img)
    # r = (None,None)
    # if( fs is not None ):
    #     fs.show()
    #     r = fs[0].getCard()
    # result.append(r)
    # if(r==label):
    #     passing += 1
    #     print "PASS: "+str(label)+"->"+str(r)
    # else:
    #     print "FAIL: "+str(label)+"->"+str(r)
    #time.sleep(0.1)
#print labels
