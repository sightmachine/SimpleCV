from glob import glob
from SimpleCV import Image, ImageSet

SUITS = ('c', 'd', 'h', 's')
RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A')
MISC = ( 'none','bad','joker')

def GetSpecificCardData(suit,rank,path="./data/",label=True):
    fullpath = path+"/"+suit+"/"+rank+"/"
    print fullpath
    iset = ImageSet(fullpath)
    if( label ):
        label_vals = []
        l = (suit,rank) # not sure this is how we want to do this
        sz = len(iset)
        for i in range(0,sz):
            label_vals.append(l)
        return iset,label_vals
    else:
        return iset

def GetFullDataSet(path="./data",label=True): # just load everything
    data = ImageSet()
    labels = []
    for s in SUITS:
        for r in RANKS:
            if( label ):
                d,l = GetSpecificCardData(s,r,path,label)
                data += d
                labels += l
            else:
                d = GetSpecificCardData(s,r,path,label)
                data += d
    if( label ):
        return data,labels
    else:
        return data
