from SimpleCV import *
from CardUtil import *
from PlayingCardFactory import *
import numpy as np
ranks = ['1','2','3','4','5','69','7','8','0','10','J','Q','K','A']
keys =  [pg.K_1,pg.K_2,pg.K_3,pg.K_4,pg.K_5,pg.K_6,pg.K_7,pg.K_8,pg.K_0,pg.K_t,pg.K_j,pg.K_q,pg.K_k,pg.K_a]
path = "./train/ranks/"

print len(ranks)
print len(keys)
data = ImageSet(path)
print len(data)
npath = "./train/ranks/"    
fullpaths = []
kdict = {}
for r in range(len(ranks)):
    npath = path + ranks[r] + "/"
    print npath
    kdict[keys[r]]=npath
    fullpaths.append(npath)
    if not os.path.exists(npath):
        os.makedirs(npath)        

print kdict
disp = Display((640,480))

print len(data)
for d in data:
    fname =  d.filename
    d.save(disp)
    doNext = False
    while not doNext:
        keys = disp.checkEvents()
        for k in keys:
            if(kdict.has_key(k)):
                path = kdict[k]
                nfiles = len(glob.glob(path+"*.*"))+1
                fname = path+"rank-"+str(nfiles)+".png"
                print "Saving as: " + fname
                d.save(fname)
                doNext = True


