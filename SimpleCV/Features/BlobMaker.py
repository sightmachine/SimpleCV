from SimpleCV.base import *
#import cv2 as cv2

class BlobMaker:
    """
    Blob maker encapsulates all of the contour extraction process and data, so
    it can be used inside the image class, or extended and used outside the image
    class. The general idea is that the blob maker provides the utilites that one
    would use for blob extraction. Later implementations may include tracking and
    other features.
    """
    mMemStorage = None
    def __init__(self):
        pass

    def extractUsingModel(self, img, colormodel,minsize=10, maxsize=0):
        """
        Extract blobs using a color model
        img        - The input image
        colormodel - The color model to use.
        minsize    - The minimum size of the returned features.
        maxsize    - The maximum size of the returned features 0=uses the default value.

        Parameters:
            img - Image
            colormodel - ColorModel object
            minsize - Int
            maxsize - Int
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

    def extractFromBinary(self,binaryImg,colorImg, minsize = 5, maxsize = -1,appx_level=3):
        """
        This method performs blob extraction given a binary source image that is used
        to get the blob images, and a color source image.
        binarymg- The binary image with the blobs.
        colorImg - The color image.
        minSize  - The minimum size of the blobs in pixels.
        maxSize  - The maximum blob size in pixels.
        * *appx_level* - The blob approximation level - an integer for the maximum distance between the true edge and the approximation edge - lower numbers yield better approximation.
        """
        #If you hit this recursion limit may god have mercy on your soul.
        #If you really are having problems set the value higher, but this means
        # you have over 10,000,000 blobs in your image.
        sys.setrecursionlimit(5000)
        #h_next moves to the next external contour
        #v_next() moves to the next internal contour
        if (maxsize <= 0):
            maxsize = colorImg.width * colorImg.height
        binaryImg.show()
        retVal = []
        test = binaryImg.meanColor()
        if( test[0]==0.00 and test[1]==0.00 and test[2]==0.00):
            return FeatureSet(retVal)

        # There are a couple of weird corner cases with the opencv
        # connect components libraries - when you try to find contours
        # in an all black image, or an image with a single white pixel
        # that sits on the edge of an image the whole thing explodes
        # this check catches those bugs. -KAS
        # Also I am submitting a bug report to Willow Garage - please bare with us.
        ptest = (4*255.0)/(binaryImg.width*binaryImg.height) # val if two pixels are white
        if( test[0]<=ptest and test[1]<=ptest and test[2]<=ptest):
            return retVal
        contourImage = binaryImg.edges().getGrayNumpy()
        print contourImage.shape, contourImage.dtype
        contours, hierarchy = cv2.findContours(contourImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #seq = cv.FindContours( binaryImg._getGrayscaleBitmap(), self.mMemStorage, cv.CV_RETR_TREE, cv.CV_CHAIN_APPROX_SIMPLE)
        if not contours:
            warnings.warn("Unable to find Blobs. Retuning Empty FeatureSet.")
            return FeatureSet([])
        try:
            # note to self
            # http://code.activestate.com/recipes/474088-tail-call-optimization-decorator/
            retVal = self._extractFromBinary(contours,False,colorImg,minsize,maxsize,appx_level)
        except RuntimeError,e:
            logger.warning("You exceeded the recursion limit. This means you probably have too many blobs in your image. We suggest you do some morphological operations (erode/dilate) to reduce the number of blobs in your image. This function was designed to max out at about 5000 blobs per image.")
        return FeatureSet(retVal)

    def _extractFromBinary(self, contours, isaHole, colorImg,minsize,maxsize,appx_level):
        """
        The recursive entry point for the blob extraction. The blobs and holes are presented
        as a tree and we traverse up and across the tree.
        """
        retVal = []

        if(not contours):
            return retVal
        for contour in contours:
            temp = self._extractData(contour, colorImg, minsize, maxsize, appx_level)
            if temp is not None:
                retVal.append(temp)
        return retVal

    def _extractData(self, contour, color, minsize, maxsize, appx_level):
        """
        Extract the bulk of the data from a give blob. If the blob's are is too large
        or too small the method returns none.
        """
        if( contour is None or not len(contour)):
            return None
        area = cv2.contourArea(contour)
        if( area < minsize or area > maxsize):
            return None

        retVal = Blob()
        retVal.image = color
        retVal.mArea = area

        retVal.mMinRectangle = cv2.minAreaRect(contour)
        bb = cv2.boundingRect(contour)
        retVal.x = bb[0]+(bb[2]/2)
        retVal.y = bb[1]+(bb[3]/2)
        retVal.mPerimeter = cv2.arcLength(contour, True)
        retVal.mContour = contour
        if( retVal.mContour is not None):
            retVal.mContourAppx = []
            print len(retVal.mContour)
            print np.array([retVal.mContour])
            appx = cv2.approxPolyDP(np.array(retVal.mContour,'float32'),appx_level,True)
            for p in appx:
                retVal.mContourAppx.append((int(p[0][0]),int(p[0][1])))

        # so this is a bit hacky....

        # For blobs that live right on the edge of the image OpenCV reports the position and width
        #   height as being one over for the true position. E.g. if a blob is at (0,0) OpenCV reports
        #   its position as (1,1). Likewise the width and height for the other corners is reported as
        #   being one less than the width and height. This is a known bug.

        xx = bb[0]
        yy = bb[1]
        ww = bb[2]
        hh = bb[3]
        retVal.points = [(xx,yy),(xx+ww,yy),(xx+ww,yy+hh),(xx,yy+hh)]
        retVal._updateExtents()
        chull = cv2.convexHull(contour, returnPoints=1)
        retVal.mConvexHull = list(chull)
        # KAS -- FLAG FOR REPLACE 6/6/2012
        #hullMask = self._getHullMask(chull,bb)

        # KAS -- FLAG FOR REPLACE 6/6/2012
        #retVal.mHullImg = self._getBlobAsImage(chull,bb,color.getBitmap(),hullMask)

        # KAS -- FLAG FOR REPLACE 6/6/2012
        #retVal.mHullMask = Image(hullMask)

        del chull

        moments = cv2.moments(contour)

        #This is a hack for a python wrapper bug that was missing
        #the constants required from the ctype
        retVal.m00 = area
        retVal.m10 = moments['m10']
        retVal.m01 = moments['m01']
        retVal.m11 = moments['m11']
        retVal.m20 = moments['m20']
        retVal.m02 = moments['m02']
        retVal.m21 = moments['m21']
        retVal.m12 = moments['m12']

        retVal.mHu = cv2.HuMoments(moments)

        # KAS -- FLAG FOR REPLACE 6/6/2012
        mask = self._getMask(contour, bb)
        #retVal.mMask = Image(mask)

        retVal.mAvgColor = self._getAvg(color.getNumpy(),bb,mask)
        print retVal.mAvgColor
        retVal.mAvgColor = retVal.mAvgColor[0:2]
        #retVal.mAvgColor = self._getAvg(color.getBitmap(),retVal.mBoundingBox,mask)
        #retVal.mAvgColor = retVal.mAvgColor[0:3]

        # KAS -- FLAG FOR REPLACE 6/6/2012
        #retVal.mImg = self._getBlobAsImage(seq,bb,color.getBitmap(),mask)

        retVal.mHoleContour = self._getHoles(contour)
        retVal.mAspectRatio = retVal.mMinRectangle[1][0]/retVal.mMinRectangle[1][1]

        return retVal

    def _getHoles(self, contours):
        """
        This method returns the holes associated with a blob as a list of tuples.
        """
        retVal = None
        for contour in contours:
            if( len(contour) >= 3 ): #exclude single pixel holes
                    retVal.append(contour)
        return retVal


    def _getMask(self, contour, bb):
        """
        Return a binary image of a particular contour sequence.
        """
        #bb = cv.BoundingRect(seq)
        bb = cv2.boundingRect(contour)
        mask = np.zeros((bb[3], bb[2]))
        cv2.drawContours(mask, [contour], 0, (0), thickness=-1, offset=(-1*bb[0],-1*bb[1]))
        # I don't think there's ever going to be v_next()
        """
        holes = seq.v_next()
        if( holes is not None ):
            cv.DrawContours(mask,holes,(0),(255),0,thickness=-1, offset=(-1*bb[0],-1*bb[1]))
            while( holes.h_next() is not None ):
                holes = holes.h_next();
                if(holes is not None):
                    cv.DrawContours(mask,holes,(0),(255),0,thickness=-1, offset=(-1*bb[0],-1*bb[1]))
        """
        return mask

    def _getHullMask(self, hull, bb):
        """
        Return a mask of the convex hull of a blob.
        """
        bb = cv2.boundingRect(hull)
        mask = np.zeros((bb[3], bb[2]))
        cv2.drawContours(mask, [hull], 0, (255), thickness=-1, offset=(-1*bb[0],-1*bb[1]))
        return mask

    def _getAvg(self, colornp, bb, mask):
        """
        Calculate the average color of a blob given the mask.
        """
        print "need to do avg with mask"
        img = colornp[bb[0]:bb[0]+bb[2], bb[1]:bb[1]+bb[3]]
        color = (np.average(img[:,:,0]), np.average(img[:,:,1]), np.average(img[:,:,2]))
        return color

    def _getBlobAsImage(self, colornp, bb, mask):
        """
        Return an image that contains just pixels defined by the blob sequence.
        """
        print "need to do mask and copy too. sigh."
        img = colornp[bb[0]:bb[0]+bb[2], bb[1]:bb[1]+bb[3]]
        return(Image(img))



from SimpleCV.ImageClass import Image
from SimpleCV.Features.Features import FeatureSet
from SimpleCV.Features.Blob import Blob
