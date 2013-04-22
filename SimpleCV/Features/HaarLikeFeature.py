from SimpleCV.base import *
from SimpleCV.ImageClass import Image


class HaarLikeFeature():
    """
    Create a single Haar feature and optionally set the regions that define
    the Haar feature and its name. The formal of the feature is

    The format is [[[TL],[BR],SIGN],[[TL],[BR],SIGN].....]
    Where TR and BL are the unit coorinates for the top right and bottom
    left coodinates.

    For example
    [[[0,0],[0.5,0.5],1],[[0.5.0],[1.0,1.0],-1]]

    Takes the right side of the image and subtracts from the left hand side
    of the image.
    """
    mName = None
    mRegions = None
    def __init__(self, name=None,regions=None):

        self.mName = name;
        self.mRegions = regions;


    def setRegions(self,regions):
        """
        Set the list of regions. The regions are square coordinates on a unit
        sized image followed by the sign of a region.

        The format is [[[TL],[BR],SIGN],[[TL],[BR],SIGN].....]
        Where TR and BL are the unit coorinates for the top right and bottom
        left coodinates.

        For example
        [[[0,0],[0.5,0.5],1],[[0.5.0],[1.0,1.0],-1]]

        Takes the right side of the image and subtracts from the left hand side
        of the image.
        """
        self.mRegions = regions

    def setName(self,name):
        """
        Set the name of this feature, the name must be unique.
        """
        self.mName = name

    def apply(self, intImg ):
        """
        This method takes in an integral image and applies the haar-cascade
        to the image, and returns the result.
        """
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
        """
        Write the Haar cascade to a human readable file. file is an open file pointer.
        """
        file.write(self.mName)
        file.write(" "+str(len(self.mRegions))+"\n")
        for i in range(len(self.mRegions)):
            temp = self.mRegions[i]
            for j in range(len(temp)):
                file.write(str(temp[j])+' ')
            file.write('\n')
        file.write('\n')
