from SimpleCV.base import *
from SimpleCV.ImageClass import *
from SimpleCV.Color import * 
from SimpleCV.Features.Features import Feature, FeatureSet
from SimpleCV.Features.PlayingCards.PlayingCard import *
import scipy.spatial.distance as ssd
import sys,traceback

class CardError(Exception):
    def __init__(self, card=None,message=None):
        self.card = card
        self.msg = message
    def __str__(self):
        return repr(self.msg)

        
class PlayingCardFactory():
    
    def __init__(self,parameterDict=None,model="card_models.pkl"):
        if(parameterDict is not None):
            self.parameterize(parameterDict)
        # we need to do checks here
        self.models = pickle.load(open(model,'rb'))
        self._loadModels()

    def matchVal(self,a,b):
        mySigns = np.sign(a)
        myLogs = np.log(np.abs(a))
        myM = mySigns * myLogs
        
        #otherSigns = np.sign(b)
        #otherLogs = np.log(np.abs(b))
        #otherM = otherSigns * otherLogs
        
        return np.sum(abs((1/ myM - 1/b)))

    def _loadModels(self):
        self.rank_models = []
        ranks = ['2','3','4','5','69','7','8','0','10','J','Q','K','A']
        for r in ranks:
            r_model = r+"_Hu"
            r_thresh = r+"_threshold"
            self.rank_models.append((r,self.models[r_model],self.models[r_thresh]))
        self.suit_models = []
        suits = ['c','d','h','s']
        for s in suits:
            s_model = s+"_Hu"
            s_thresh = s+"_threshold"
            self.suit_models.append((s,self.models[s_model],self.models[s_thresh]))
        print "LOADED MODELS"
        print self.suit_models
        print self.rank_models

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
#             card = self._estimateSuit(card)
#             # Do we think this is a face card this
#             # is an easier test
#             isFace,card = self._isFaceCard(card)
#             if(isFace):
#                 # if we are a face card get the face. This is had
#                 card = self._estimateFaceCard(card)
#             else:
#                 # otherwise get the rank
#                 # first pass is corners second
#                 # pass is the card body
#                 card = self._estimateRank(card)
#             # now go back do some sanity checks
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
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]      
            print(exc_type, fname, exc_tb.tb_lineno)
            return None
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
        

    def _blobsNearCorners(self,blobs,corners,cutoff):
        def dist(a,b):
            return np.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
        near_corners = FeatureSet()
        not_near_corners = FeatureSet()
        tl_t,tr_t,bl_t,br_t = corners
        #print corners
        for blob in blobs:
            tl = blob.topLeftCorner()
            tr = blob.topRightCorner()
            bl = blob.bottomLeftCorner()
            br = blob.bottomRightCorner()
            a = dist(tl,tl_t)
            b = dist(tr,tr_t)
            c = dist(bl,bl_t)
            d = dist(br,br_t)
            #print tl,tr,bl,br
            if( a < cutoff or b < cutoff or c < cutoff or d < cutoff ):
                near_corners.append(blob)
            else:
                not_near_corners.append(blob)
        return near_corners,not_near_corners

    def _estimateColor(self,card):
        """
        Take in a card feature and determine the color.
        if we find a color return the feature otherwise
        throw. 
        """
        if( card.cardImg is not None):
            img = card.cardImg.resize(h=card.img.height)
            temp = img.invert().dilate()
            binary = temp.threshold(100).morphClose()
#            binary = temp.binarize().morphClose().invert()
            sz = img.width*img.height
            b = img.findBlobsFromMask(binary,minsize = sz*.0005, maxsize=sz*0.1)
            fs = FeatureSet()
            for bs in b:
                if(not bs.isOnEdge() and bs.aspectRatio() > 0.4 and bs.aspectRatio() < 2.2 ):
                    fs.append(bs)
            
            w = img.width
            h = img.height
            tl = (0,0)
            tr = (w,0)
            bl = (0,h)
            br = (w,h)
            corners = [tl,tr,bl,br]
            cutoff = 70 # distance from the corners 
            card.rankBlobs,card.suitBlobs = self._blobsNearCorners(fs,corners,cutoff)
            if( len(card.rankBlobs) > 0 ):
                card.rankBlobs.show(color=Color.RED,width=-1)
                time.sleep(1)
            if( len(card.suitBlobs) > 0 ):
                card.suitBlobs.show(color=Color.BLUE,width=-1)
                time.sleep(1)
        else:
            raise CardError(card, "No card image to extract card color from.")
        return card
        
    def _estimateSuit(self,card):
        """
        Using the card feature determine suit.

        If we find something return the card, otherwise
        throw.
        """
        blobs = card.suitBlobs
        found = []
        fv = []
        for b in blobs:
            sample = b.mHu
            vals = []
            suits = []
            for m in self.suit_models:
                #v = self.matchVal(sample,m[1])
                v = ssd.cdist([sample],[m[1]])[0][0]
                if( v < m[2] ):
                    vals.append(v)
                    suits.append(m[0])
            if( len(suits) > 0 ):
                if( len(suits) == 1):
                    found.append(suits[0])
                    fv.append(vals[0])
                else:
                    vals = np.array(vals)
                    idx = np.where(vals==np.min(vals))[0]
                    found.append(suits[idx])
                    fv.append(vals[idx])
        
        print zip(found,fv) 
        fv = np.array(fv)
        idx = np.where(fv==np.min(fv))[0]
        card.suit = found[idx]
#         suit_vals = ['c','h','d','s']
#         best_count = 0
#         best_suit = None
#         for s in suit_vals:
#             test = found.count(s)
#             if(test > best_count):
#                 best_count = test
#                 best_suit = s
#         card.suit = best_suit
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
