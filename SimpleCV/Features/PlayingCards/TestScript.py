from SimpleCV import *
#from FeatureUtils import *
from CardUtil import *
from PlayingCardFactory import *
#import FeatureUtils
import numpy as np

def GetParallelSets(line_fs,parallel_thresh=100):
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
    print result
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
#datapoints = datapoints[0:400]
result = []
passing = 0
color = Color()
i = 0
for d in datapoints:
    i = i + 1
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
    time.sleep(0.1)
#print labels
