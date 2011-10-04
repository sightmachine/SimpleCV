from SimpleCV.base import *
from SimpleCV.ImageClass import Image


class HaarLikeFeature():

    mName = None
    mRegions = None
    def __init__(self, name=None,regions=None):
        self.mName = name;
        self.mRegions = regions;
    
    def setRegions(self,regions):
        self.mRegions = regions
    
    def setName(self,name):
        self.mName = name
    
    def apply(self, intImg ):
        w = intImg.shape[0]-1
        h = intImg.shape[1]-1
        accumulator = 0
        for i in range(len(self.mRegions)):
            # using the integral image
            # A = Lower Right Hand Corner
            # B = upper right hand corner
            # C = lower left hand corner
            # D = upper left hand corner
            # sum = A - B - C  + D
            # regions are in
            # (p,q,r,s,t) format
            p = self.mRegions[i][0] # p = left (all are unit length)
            q = self.mRegions[i][1] # q = top
            r = self.mRegions[i][2] # r = right
            s = self.mRegions[i][3] # s = bottom
            sign = self.mRegions[i][4] # t = sign
            xA = int(w*r)
            yA = int(h*s) 
            xB = int(w*r)
            yB = int(h*q)
            xC = int(w*p)
            yC = int(h*s)
            xD = int(w*p)
            yD = int(h*q)
            accumulator += sign*(intImg[xA,yA]-intImg[xB,yB]-intImg[xC,yC]+intImg[xD,yD])
        return accumulator
    
    def writeToFile(self,file):
        file.write(self.mName)
        file.write(" "+str(len(self.mRegions))+"\n")
        for i in range(len(self.mRegions)):
            temp = self.mRegions[i]
            for j in range(len(temp)):
                file.write(str(temp[j])+' ')
            file.write('\n')
        file.write('\n')
