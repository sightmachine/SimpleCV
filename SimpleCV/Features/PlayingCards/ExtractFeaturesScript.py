from SimpleCV import *
from CardUtil import *
from PlayingCardFactory import *
import numpy as np
    
pcf = PlayingCardFactory()
data,labels = GetFullDataSet()
print len(data)
datapoints = zip(data,labels)
#datapoints = datapoints[0:40]
result = []
passing = 0
color = Color()
i = 0
path = "./train"
for s in SUITS:
    directory = path+"/"+s+"/"
    if not os.path.exists(directory):
            os.makedirs(directory)        
for r in RANKS:
    directory = path+"/"+r+"/"
    if not os.path.exists(directory):
        os.makedirs(directory)        

for d in datapoints:
    i = i + 1
    img = d[0]
    label = d[1]    
    fs = pcf.process(img)
    r = (None,None)
    if( fs is not None ):
        fs.show()
        r = fs[0].getCard()
        if fs[0].cardImg is None:
            continue
        spath = path+"/"+label[0]+"/"
        rpath = path+"/"+label[1]+"/"
        sfiles = len(glob.glob(spath+"*.png"))+1
        print glob.glob(rpath+"*.png")
        print "------->" + str(sfiles) 
        rfiles = len(glob.glob(rpath+"*.png"))+1
        rank_fname = rpath+label[1]+"-"+str(rfiles)+".png"
        print "saved rank:" + rank_fname
        fs[0].cardImg.save(rank_fname)
        for s in fs[0].suitBlobs:
            suit_fname = spath+label[0]+"-"+str(sfiles)+".png"
            temp = s.mImg.save(suit_fname)
            print "saved suit:" + suit_fname
            sfiles += 1 

    result.append(r)
    if(r==label):
        passing += 1
        print "PASS: "+str(label)+"->"+str(r)
    else:
        print "FAIL: "+str(label)+"->"+str(r)
    time.sleep(0.1)
#print labels
