from SimpleCV.base import *
from SimpleCV.ImageClass import Image
from SimpleCV.Features import FeatureSet
from SimpleCV.Blob import Blob


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

    def extractUsingModel(self, img, colormodel,minsize=10, maxsize=0):
        """
        Extract blobs using a color model
        img        - The input image
        colormodel - The color model to use.
        minsize    - The minimum size of the returned features.
        maxsize    - The maximum size of the returned features 0=uses the default value. 
        """
        if (maxsize <= 0):  
          maxsize = img.width * img.height 
        gray = colormodel.threshold(img)
        blobs = self.extractFromBinary(gray,img,minArea=minsize,maxArea=maxsize)
        retVal = sorted(blobs,key=lambda x: x.mArea, reverse=True)
        return FeatureSet(retVal)
    
    def extract(self, img, threshval = 127, minsize=10, maxsize=0, threshblocksize=3, threshconstant=5):
        """
        This method performs a threshold operation on the input image and then
        extracts and returns the blobs.
        img       - The input image (color or b&w)
        threshval - The threshold value for the binarize operation. If threshval = -1 adaptive thresholding is used
        minsize   - The minimum blob size in pixels.
        maxsize   - The maximum blob size in pixels. 0=uses the default value.
        threshblocksize - The adaptive threhold block size.
        threshconstant  - The minimum to subtract off the adaptive threshold
        """
        if (maxsize <= 0):  
          maxsize = img.width * img.height
    
        #create a single channel image, thresholded to parameters

        blobs = self.extractFromBinary(img.binarize(threshval, 255, threshblocksize, threshconstant).invert(),img,minsize,maxsize)
        retVal = sorted(blobs,key=lambda x: x.mArea, reverse=True)
        return FeatureSet(retVal)    
    
    def extractFromBinary(self,binaryImg,colorImg, minsize = 5, maxsize = -1):
        """
        This method performs blob extraction given a binary source image that is used
        to get the blob images, and a color source image.
        binaryImg- The binary image with the blobs.
        colorImg - The color image.
        minSize  - The minimum size of the blobs in pixels.
        maxSize  - The maximum blob size in pixels. 
        """
        #h_next moves to the next external contour
        #v_next() moves to the next internal contour
        if (maxsize <= 0):  
          maxsize = img.width * img.height 
          
        seq = cv.FindContours(binaryImg._getGrayscaleBitmap(), cv.CreateMemStorage(), cv.CV_RETR_TREE, cv.CV_CHAIN_APPROX_SIMPLE)
        retVal = []
        retVal = self._extractFromBinary(seq,False,colorImg,minsize,maxsize)
        del seq
        return retVal
    
    def _extractFromBinary(self, seq, isaHole, colorImg,minsize,maxsize):
        """
        The recursive entry point for the blob extraction. The blobs and holes are presented
        as a tree and we traverse up and across the tree. 
        """
        #if there is nothing return the list
        #if(seq is None):
        #    return None
        retVal = []
        
        if( not isaHole ): #if we aren't a hole then we are an object, so get and return our featuress         
            temp =  self._extractData(seq,colorImg,minsize,maxsize)
            if( temp is not None ):
                retVal.append(temp)
            
                    
        #get the current feature
        nextBlob = seq.h_next() # move to the next feature on our level
        nextLayer = seq.v_next() # move down a layer

        if( nextBlob is not None ):
            #the next object is whatever this object is, add its list to ours
            retVal += self._extractFromBinary(nextBlob, isaHole, colorImg, minsize,maxsize)
        if(nextLayer is not None): #the next object, since it is down a layer is different
            retVal += self._extractFromBinary(nextLayer, not isaHole, colorImg, minsize,maxsize)
        

        return retVal
    
    def _extractData(self,seq,color,minsize,maxsize):
        """
        Extract the bulk of the data from a give blob. If the blob's are is too large
        or too small the method returns none. 
        """
        if( seq == None or not len(seq)):
            return None
        area = cv.ContourArea(seq)
        if( area < minsize or area > maxsize):
            return None
        retVal = Blob()
        retVal.image = color 
        retVal.mArea = area
        retVal.mMinRectangle = cv.MinAreaRect2(seq)
        retVal.mBoundingBox = cv.BoundingRect(seq)
        retVal.x = retVal.mBoundingBox[0]+(retVal.mBoundingBox[2]/2)
        retVal.y = retVal.mBoundingBox[1]+(retVal.mBoundingBox[3]/2)
        retVal.mPerimeter = cv.ArcLength(seq)
        
        retVal.mContour = list(seq)
        chull = cv.ConvexHull2(seq,cv.CreateMemStorage(),return_points=1)
        retVal.mConvexHull = list(chull)
        retVal.mHullMask = self._getHullMask(chull,retVal.mBoundingBox)
        del chull

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
        retVal.mMask = self._getMask(seq,retVal.mBoundingBox)
        mask = retVal.mMask
        retVal.mAvgColor = self._getAvg(color.getBitmap(),retVal.mBoundingBox,mask)
        retVal.mImg = self._getBlobAsImage(seq,retVal.mBoundingBox,color.getBitmap(),mask)
        retVal.mHoleContour = self._getHoles(seq)
        
        bb = retVal.mBoundingBox
        retVal.points.append((bb[0], bb[1]))
        retVal.points.append((bb[0] + bb[2], bb[1]))
        retVal.points.append((bb[0] + bb[2], bb[1] + bb[3]))
        retVal.points.append((bb[0], bb[1] + bb[3]))
        
        return retVal
    
    def _getHoles(self,seq):
        """
        This method returns the holes associated with a blob as a list of tuples.
        """
        retVal = None
        holes = seq.v_next()
        if( holes is not None ):
            retVal = [list(holes)]
            while( holes.h_next() is not None ):
                holes = holes.h_next();
                temp = list(holes)
                if( len(temp) >= 3 ): #exclude single pixel holes 
                    retVal.append(temp)
        return retVal
        
    def _getMask(self,seq,bb):
        """
        Return a binary image of a particular contour sequence. 
        """
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
        return mask
    
    def _getHullMask(self,hull,bb):
        """
        Return a mask of the convex hull of a blob. 
        """
        bb = cv.BoundingRect(hull)
        mask = cv.CreateImage((bb[2],bb[3]),cv.IPL_DEPTH_8U,1)
        cv.Zero(mask)
        cv.DrawContours(mask,hull,(255),(0),0,thickness=-1, offset=(-1*bb[0],-1*bb[1]))
        return mask
    
    def _getAvg(self,colorbitmap,bb,mask):
        """
        Calculate the average color of a blob given the mask. 
        """
        cv.SetImageROI(colorbitmap,bb)
        #may need the offset parameter
        avg = cv.Avg(colorbitmap,mask)
        cv.ResetImageROI(colorbitmap)
        return avg
    
    def _getBlobAsImage(self,seq,bb,colorbitmap,mask):
        """
        Return an image that contains just pixels defined by the blob sequence. 
        """
        cv.SetImageROI(colorbitmap,bb)
        outputImg = cv.CreateImage((bb[2],bb[3]),cv.IPL_DEPTH_8U,3)
        cv.Copy(colorbitmap,outputImg,mask)
        cv.ResetImageROI(colorbitmap)
        return(Image(outputImg))
        
