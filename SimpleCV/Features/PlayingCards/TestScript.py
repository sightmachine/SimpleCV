from SimpleCV import *
from CardUtil import *
from PlayingCardFactory import *
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
    fs = pcf.process(img)
    r = (None,None)
    if( fs is not None ):
        fs.show()
        r = fs[0].getCard()
    result.append(r)
    if(r==label):
        passing += 1
        print "PASS: "+str(label)+"->"+str(r)
    else:
        print "FAIL: "+str(label)+"->"+str(r)
    time.sleep(0.001)
#print labels