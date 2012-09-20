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

def CreateModel(data,r,rankdict):
    print "Doing: " +path
    dset = []
    for d in data:
        bin = d.threshold(1)
        fs = d.findBlobsFromMask(bin)
        if( fs is not None ):
            dset.append(fs[0].mHu)
    dset = np.array(dset)
    avg =  np.average(dset,0)
    rstr = r+"_Hu"
    rankdict[rstr] = avg
    d = ssd.cdist(dset,[avg])
    threshold = np.average(d)
    threshold_sd= np.std(d)
    rstr = r+"_avg"
    rankdict[rstr] = threshold
    rstr = r+"_std"
    rankdict[rstr] = threshold_sd
    rstr = r+"_threshold"
    rankdict[rstr] = threshold+(3*threshold_sd)
 
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
