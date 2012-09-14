from SimpleCV.base import *
from SimpleCV.ImageClass import *
from SimpleCV.Color import * 
from SimpleCV.Features.Features import Feature, FeatureSet
from SimpleCV.Features.Detection import Lines
"""
So this is a place holder for some routines that should live in
featureset if we can make it specific to a type of features
"""

def GetParallelSets(line_fs,parallel_thresh=2):
    result = []
    for l1 in lines:
        for l2 in lines:
            result.append(np.abs(l1.cross(l2)))

    result = np.array(result)
    sz = len(line_fs)
    result = result.reshape(sz,sz)
    l1,l2=np.where(result<parallel_thresh)
    idxs = zip(l1,l2)
    retVal = []
    for idx in idxs:
        if(idx[0]!=idx[1]):
            retVal.append((line_fs[idx[0]],line_fs[idx[1]]))
    return retVal

def ParallelDistance(line1,line2):
    pass