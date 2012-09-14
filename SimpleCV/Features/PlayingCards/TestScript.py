from SimpleCV import *
from CardUtil import *
from PlayingCardFactory import *
pcf = PlayingCardFactory()
data,labels = GetFullDataSet()
print len(data)
for d in data:
    fs = pcf.process(d)
    fs.show()
#   #    time.sleep(0.1)
#print labels