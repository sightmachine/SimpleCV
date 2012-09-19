from SimpleCV import *
from CardUtil import *
from PlayingCardFactory import *
import numpy as np
    
data,labels = GetFullDataSet()
disp = Display((640,480))

print len(data)
for d in data:
    fname =  d.filename
    d.save(disp)
    doNext = False
    while not doNext:
        keys = disp.checkEvents()
        for k in keys:
            if( k == pg.K_SPACE ):
                print "Saved: " + fname 
                doNext = True
            elif( k == pg.K_d ):
                print fname 
                print "Removed: " + fname
                os.remove(fname)
                doNext = True
