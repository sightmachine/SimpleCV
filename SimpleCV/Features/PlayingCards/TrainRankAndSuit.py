from SimpleCV import Image, Display,Camera,Color,ImageSet
import numpy as np
import scipy.spatial.distance as ssd
import glob,os
import pygame as pg
import pickle
from CardUtil import SUITS, RANKS, MISC


rpath = "./train/ranks/"
ranks = ['2','3','4','5','69','7','8','0','10','J','Q','K','A']
spath = "./train/"
suits = ['c','d','h','s']

def matchVal(a,b):
    #mySigns = np.sign(a)
    #myLogs = np.log(np.abs(a))
    #myM = mySigns * myLogs
    
    #otherSigns = np.sign(b)
    #otherLogs = np.log(np.abs(b))
    #otherM = otherSigns * otherLogs
        
    return np.sum(abs((1/ a - 1/ b)))

def CreateModel(data,r,rankdict):
    print "Doing: " +path
    dset = []
    for d in data:
        bin = d.threshold(1)
        fs = d.findBlobsFromMask(bin)
        if( fs is not None ):
            hu = fs[0].mHu
            #signs = np.sign(hu)
            #logs = np.log(np.abs(hu))
            #final = signs*logs
            dset.append(hu)
#    temp = dset[0]
    dset = np.array(dset)
#    avg = dset[1]
    avg =  np.average(dset,0)
    rstr = r+"_Hu"
    rankdict[rstr] = avg
    d = ssd.cdist(dset,[avg])
    #d = []
    #for h in dset:
    #    d.append(matchVal(avg,h))
    threshold = np.average(d)
    threshold_sd= np.std(d)
    rstr = r+"_avg"
    rankdict[rstr] = threshold
    rstr = r+"_std"
    rankdict[rstr] = threshold_sd
    rstr = r+"_threshold"
    rankdict[rstr] = threshold
 
    print "----------------------"
    print "For rank " + r
    print "Hu Moment"
    print avg
    print "Threshold: "+str(threshold)
    print "ThresholdSD: "+str(threshold_sd)
    return rankdict


dataDict = {}
for r in ranks:
    path = rpath+r
    data = ImageSet(path)
    dataDict = CreateModel(data,r,dataDict)

for s in suits:
    path = spath+s
    data = ImageSet(path)
    dataDict = CreateModel(data,s,dataDict)
   
print dataDict
pickle.dump( dataDict, open( "card_models.pkl", "wb" ))
