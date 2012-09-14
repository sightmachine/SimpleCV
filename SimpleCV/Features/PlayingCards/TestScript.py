from SimpleCV import *
from CardUtil import *

data,labels = GetFullDataSet()
print len(data)
for d in data:
    d.scale(0.5).binarize().invert().show()
#    time.sleep(0.1)
#print labels