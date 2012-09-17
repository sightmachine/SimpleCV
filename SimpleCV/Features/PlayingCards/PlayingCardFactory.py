from SimpleCV.base import *
from SimpleCV.ImageClass import *
from SimpleCV.Color import * 
from SimpleCV.Features.Features import Feature, FeatureSet
from SimpleCV.Features.PlayingCards.PlayingCard import *
class CardError(Exception):
    def __init__(self, card=None,message=None):
        self.card = card
        self.msg = message
    def __str__(self):
        return repr(self.msg)

        
class PlayingCardFactory():
    
    def __init__(self,parameterDict=None):
        if(parameterDict is not None):
            self.parameterize(parameterDict)

    def parameterize(self,parameterDict):
        """
        Parameterize from a dictionary so we can optimize performance.
        """
        pass
        
    def process(self,img):
        """
        Process the image. Return a featureset with a single
        PlayingCard feature or None
        """
        # Can we find anything that looks like a card
        card = self._findCardEdges(img)
        if( card is None ): # if we don't see it just bail
            warnings.warn("Could not find a card.")
            return None
        try:
            # extract the basic features and get color
            card = self._estimateColor(card)
            # okay, we got a color and some features
            # go ahead and estimate the suit
            card = self._estimateSuit(card)
            # Do we think this is a face card this
            # is an easier test
            isFace,card = self._isFaceCard(card)
            if(isFace):
                # if we are a face card get the face. This is had
                card = self._estimateFaceCard(card)
            else:
                # otherwise get the rank
                # first pass is corners second
                # pass is the card body
                card = self._estimateRank(card)
            # now go back do some sanity checks
            # and cleanup the features so it is not
            # too heavy
            card = self._refineEstimates(card)
        except CardError as ce:
            card = ce.card
            if( card is not None):
            # maybe we got a joker or someone
            # is being a jackass and showing us the
            # back of the card. 
                card = self._isNonStandardCard(card)
            warnings.warn(ce.msg) # we may swallow this later
            # optionally we may want to log these to
            # see where we fail and why or do a parameter
            # adjustment and try again
        except:
            # this means we had an error somewhere
            # else maybe numpy
            print "Generic Error."
            return None
        return FeatureSet([card])

    def _preprocess(self,img):
        """
        Any image preprocessing options go here.
        """
        return img
        
    def _findCardEdges(self,img):
        """
        Try to find a card, if we do return a card feature
        otherwise return None
        """
        #ppimg = self._preprocess(img)
        retVal = None
        e = img.edges(t1=1,t2=50)
        e2 = img.edges(t1=10,t2=100)
        e3 = img.sobel()
        e = e+e2+e3
        e = e.dilate(2).erode(1)
        final = img-e
        bin= final.threshold(150).morphClose()
        max_sz = img.width*img.height
        b = img.findBlobsFromMask(bin,minsize=max_sz*0.005,maxsize=max_sz*0.3)
        b = b.sortDistance(point=(img.width/2,img.height/2))
        if( b is not None ):
            w = np.min([b[0].minRectWidth(),b[0].minRectHeight()])
            h = np.max([b[0].minRectWidth(),b[0].minRectHeight()])
            ar = w/h
            if( ar > 0.6 and ar < 0.75 ):
                src = b[0].minRect()
                if(b[0].angle() < 0 ):
                    src = (src[3],src[1],src[0],src[2])
                else:
                    src = (src[2],src[3],src[1],src[0])
                dst = ((w,h),(0,h),(0,0),(w,0))
                pWarp = cv.CreateMat(3, 3, cv.CV_32FC1) #create an empty 3x3 matrix
                cv.GetPerspectiveTransform(src, dst, pWarp) #figure out the warp matri
                temp = Image((w,h))
                cv.WarpPerspective(img.getBitmap(),temp.getBitmap(), pWarp)
                temp = temp.flipOver()
                tl = b[0].topLeftCorner()
                bw = b[0].width()
                bh = b[0].height()
                retVal = PlayingCard(img,tl[0],tl[1],bw,bh)
                retVal.cardImg = temp
                retVal.corners = b[0].minRect()
                retVal.c_width = b[0].minRectWidth()
                retVal.c_height = b[0].minRectHeight()
                retVal.c_angle = b[0].angle()
        # create the feature, hang any preprocessing
        # steps on the feature
        return retVal
        
    def _estimateColor(self,card):
        """
        Take in a card feature and determine the color.
        if we find a color return the feature otherwise
        throw. 
        """
        return card
        
    def _estimateSuit(self,card):
        """
        Using the card feature determine suit.

        If we find something return the card, otherwise
        throw.
        """
        return card
        
    def _isFaceCard(self,card):
        """
        Determine if we have a face card
        return any updates to the card and the state.
        """
        return False,card
        
    def _estimateFaceCard(self,card):
        """
        Determine if we have a face card K/Q/J and some A
        """
        return card
        
    def _estimateRank(self,card):
        """
        Determine the rank and reutrn the card otherwise throw.
        """
        return card
        
    def _isNonStandardCard(self,card):
        """
        Determine if our card is not a normal card like a joker
        the backside of a card or something similar. Return either the
        card or throw.
        """
        return card

    def _refineEstimates(self,card):
        """
        Do a post process step if we want.
        e.g. find corners with sub-pix accuracy to
        do a swell overlay. Do any numpy sanitation
        for Seer. 
        """
        return card
