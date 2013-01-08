from SimpleCV.base import *
from SimpleCV.Features.Features import Feature, FeatureSet
from SimpleCV.Color import Color
from SimpleCV.ImageClass import Image
from SimpleCV.Features.Detection import ShapeContextDescriptor
import math
import scipy.stats as sps 
from sklearn import neighbors

class ShapeContextClassifier():

    def  __init__(self,images,labels):
        self.imgMap = {}
        self.ptMap = {}
        self.descMap = {}
        self.knnMap = {}
        self.blobCount = {}
        self.labels = labels
        self.images = images
        import warnings
        warnings.simplefilter("ignore")
        for i in range(0,len(images)):
            print "precomputing " + images[i].filename
            self.imgMap[labels[i]] = images[i]
           
            pts,desc,count  = self._image2FeatureVector(images[i])
            self.blobCount[labels[i]] = count 
            self.ptMap[labels[i]] = pts
            self.descMap[labels[i]] = desc
            knn = neighbors.KNeighborsClassifier()
            knn.fit(desc,range(0,len(pts))) 
            self.knnMap[labels[i]] = knn
            
    def _image2FeatureVector(self,img):
        #IMAGES MUST BE WHITE ON BLACK!
        fulllist = []
        raw_descriptors = []
        blobs = img.findBlobs(minsize=50)
        count = 0
        if( blobs is not None ):
            count = len(blobs)
            for b in blobs:
                fulllist += b._filterSCPoints()
                raw_descriptors = blobs[0]._generateSC(fulllist) 
        return fulllist,raw_descriptors,count

    
    def _getMatch(self,model_scd,test_scd):
        correspondence,distance = self._doMatching(model_scd,test_scd)
        return self._matchQuality(distances)

    def _doMatching(self,model_name,test_scd):       
        myPts = len(test_scd)
        otPts = len(self.ptMap[model_name])
        # some magic metric that keeps features
        # with a lot of points from dominating
        #metric = 1.0 + np.log10( np.max([myPts,otPts])/np.min([myPts,otPts])) # <-- this could be moved to after the sum
        otherIdx = []
        distance = [] 
        import warnings
        warnings.simplefilter("ignore")
        results = []
        for sample in test_scd:
            best = self.knnMap[model_name].predict(sample)
            idx = best[0] # this is where we can play with k
            scd = self.descMap[model_name][idx]
            temp = np.sqrt(np.sum(((sample-scd)**2)))
            #temp = 0.5*np.sum((sample-scd)**2)/np.sum((sample+scd))
            if( math.isnan(temp) ):
                temp = sys.maxint
            distance.append(temp)
        return [otherIdx,distance]

    def _matchQuality(self,distances):
        #distances = np.array(distances)
        #sd = np.std(distances)
        #x = np.mean(distances)
        #min = np.min(distances)
        # not sure trimmed mean is perfect
        # realistically we should have some bimodal dist
        # and we want to throw away stuff with awful matches
        # so long as the number of points is not a huge
        # chunk of our points.
        #tmean = sps.tmean(distances,(min,x+sd))
        tmean = np.mean(distances)
        std = np.std(distances)
        return tmean,std


    def _buildMatchDict(self,image, countBlobs):
        # we may want to base the count on the number of large blobs
        points,descriptors,count = self._image2FeatureVector(image)
        matchDict = {}
        matchStd = {}
        for key,value in self.descMap.items():
            if( countBlobs and self.blobCount[key] == count ): # only do matching for similar number of blobs
                #need to hold on to correspondences
                correspondence, distances = self._doMatching(key,descriptors)
                result,std = self._matchQuality(distances)
                matchDict[key] = result
                matchStd[key] = std
            elif( not countBlobs ):
                correspondence, distances = self._doMatching(key,descriptors)
                result,std = self._matchQuality(distances)
                matchDict[key] = result
                matchStd[key] = std
                
        return points,descriptors,count,matchDict, matchStd
                
    def classify(self,image, blobFilter=True):
        points,descriptors,count,matchDict,matchStd = self._buildMatchDict(image, blobFilter)
        best = sys.maxint
        best_name = "No Match"
        for k,v in matchDict.items():
            if ( v < best ):
                best = v 
                best_name = k
           
        return best_name, best, matchDict, matchStd

    def getTopNMatches(self,image,n=3, blobFilter = True):
        n = np.clip(n,1,len(self.labels))
        points,descriptors,count,matchDict,matchStd = self._buildMatchDict(image,blobFilter)
        best_matches = list(sorted(matchDict, key=matchDict.__getitem__))
        retList = []
        for k in best_matches:
            retList.append((k,matchDict[k]))
        return retList, matchDict, matchStd

