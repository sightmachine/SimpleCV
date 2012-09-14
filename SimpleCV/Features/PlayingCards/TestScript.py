from SimpleCV import *
from CardUtil import *
from PlayingCardFactory import *
import numpy as np
pcf = PlayingCardFactory()
data,labels = GetFullDataSet()
print len(data)
datapoints = zip(data,labels)
datapoints = datapoints[0:100]
result = []
passing = 0
for d in datapoints:
    img = d[0]
    label = d[1]
    img = img.crop(img.width/3,0,2*img.width/3,img.height)
    img = img.equalize()
    l = img.findLines(threshold=30)
    if( l is not None ):
        v = 80
        l = l.filter(np.abs(l.angle()) > v)
        l = l.sortLength()
        #top = np.min([8,len(l)])
        #l[-1*top:-1].draw(color=Color.RED,width=3)
        #img.show()
        l.show(color=Color.RED,width=3)
    
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
    time.sleep(0.01)
#print labels