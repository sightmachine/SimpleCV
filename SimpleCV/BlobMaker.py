from SimpleCV.base import *
from SimpleBlob import *
from SimpleCV.ImageClass import *

class BlobMaker:
    """
    Blob maker encapsulates all of the contour extraction process and data, so
    it can be used inside the image class, or extended and used outside the image
    class. The general idea is that the blob maker provides the utilites that one
    would use for blob extraction. Later implementations may include tracking and
    other features.
    """
    def __init__(self):
        return None

    def extractUsingModel(self, img, colormodel,doHist = False):
        """
        Extract using either a color model or yet to be writtne background model
        (e.g. codebook or just an alpha beta color model)
        """
        return None
    
    def extractFromBinary(self,binaryImg,colorImg,doHist = False, minArea = 5):
        #h_next moves to the next external contour
        #v_next() moves to the next internal contour
        seq = cv.FindContours(binaryImg._getGrayscaleBitmap(), cv.CreateMemStorage(), cv.CV_RETR_TREE, cv.CV_CHAIN_APPROX_SIMPLE)
        retVal = []
        retVal = self._extractFromBinary(seq,False,colorImg,doHist,minArea)
        return retVal
    
    def _extractFromBinary(self, seq, isaHole, colorImg, doHist, minArea):
        #if there is nothing return the list
        if(seq is None):
            return None
        retVal = []
        #get the current feature
        nextBlob = seq.h_next()
        nextLayer = seq.v_next()

        if(nextBlob is not None):
            retVal += self._extractFromBinary(nextBlob, isaHole, colorImg, doHist, minArea)
        if(nextLayer is not None):
            retVal += self._extractFromBinary(nextLayer, not isaHole, colorImg, doHist, minArea)
        
        if( not isaHole ):         
            temp =  self._extractData(seq,colorImg,doHist,minArea)
            if( temp is not None ):
               retVal.append(temp)
            
        return retVal
    
        #
        #return(bloblist.append(self._extractData(bloblist, seq, colorImg, doHist, minArea)))
        #
        #while( seq.h_next() is not None ):
        #    seq = seq.h_next();
        #    temp = self._extractData(seq,colorImg,doHist,minArea)
        #    if(temp is not None):
        #        retVal.append(temp)
        #        #holes = seq
        #        #while( holes.v_next() is not None ):
        #        #    holes = holes.v_next()
        #        #   temp = self._extractData(holes,colorImg,doHist)
        #        #  if(temp is not None):
        #        #      retVal.append(temp)
        return retVal
    
    def _extractData(self,seq,color,doHist = False,minArea=5):
        if( seq == None ):
            return None
        area = cv.ContourArea(seq)
        if( area < minArea):
            return None
        retVal = SimpleBlob()
        retVal.mArea = area #cv.ContourArea(seq)
        retVal.mContour = list(seq)
        chull = cv.ConvexHull2(seq,cv.CreateMemStorage(),return_points=1)
        retVal.mConvexHull = list(chull)
        del chull
        retVal.mMinRectangle = cv.MinAreaRect2(seq)
        retVal.mBoundingBox = cv.BoundingRect(seq)
        retVal.mPerimeter = cv.ArcLength(seq)
        retVal.mArea = cv.ContourArea(seq)
        moments = cv.Moments(seq)
        retVal.m00 = moments.m00
        retVal.m10 = moments.m10
        retVal.m01 = moments.m01
        retVal.m11 = moments.m11
        retVal.m20 = moments.m20
        retVal.m02 = moments.m02
        retVal.m21 = moments.m21
        retVal.m12 = moments.m12
        retVal.mHu = cv.GetHuMoments(moments)
        mask = self._getMask(seq,retVal.mBoundingBox)
        retVal.mAvgColor = self._getAvg(color.getBitmap(),retVal.mBoundingBox,mask)
        retVal.mImg = self._getBlobAsImage(seq,retVal.mBoundingBox,color.getBitmap(),mask)
        return retVal
    
    def _getMask(self,seq,bb):
        bb = cv.BoundingRect(seq)
        mask = cv.CreateImage((bb[2],bb[3]),cv.IPL_DEPTH_8U,1)
        cv.Zero(mask)
        cv.DrawContours(mask,seq,(255),(0),0,thickness=-1, offset=(-1*bb[0],-1*bb[1]))
        holes = seq.v_next()
        if( holes is not None ):
            cv.DrawContours(mask,holes,(0),(255),0,thickness=-1, offset=(-1*bb[0],-1*bb[1]))
            while( holes.h_next() is not None ):
                holes = holes.h_next();
                if(holes is not None):
                    cv.DrawContours(mask,holes,(0),(255),0,thickness=-1, offset=(-1*bb[0],-1*bb[1]))
                    
        derp = Image(mask)
        derp.save("DERPINGTON.PNG")
        return mask
        
    def _getAvg(self,colorbitmap,bb,mask):
        cv.SetImageROI(colorbitmap,bb)
        #may need the offset parameter
        avg = cv.Avg(colorbitmap,mask)
        cv.ResetImageROI(colorbitmap)
        return avg
    
    def _getBlobAsImage(self,seq,bb,colorbitmap,mask):
        cv.SetImageROI(colorbitmap,bb)
        outputImg = cv.CreateImage((bb[2],bb[3]),cv.IPL_DEPTH_8U,3)
        cv.Copy(colorbitmap,outputImg,mask)
        cv.ResetImageROI(colorbitmap)
        return(Image(outputImg))
        
    def _extractEdgeHist(self,seq):
        return None