from SimpleCV.base import *
from SimpleCV.Features.Features import Feature, FeatureSet
from SimpleCV.Color import Color
from SimpleCV.ImageClass import Image
from SimpleCV.Features.Detection import ShapeContextDescriptor
import math
import scipy.stats as sps


"""
Classify an object based on shape context
"""
class ShapeContextClassifier():

    def  __init__(self,images,labels):
        """
        Create a shape context classifier.

        * *images* - a list of input binary images where the things
          to be detected are white.

        * *labels* - the names of each class of objects.
        """
        # The below import has been done in init since it throws "Need scikits learn installed" for $import SimpleCV
        try:
            from sklearn import neighbors
        except:
            print "Need scikits learn installed"

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
        """
        generate a list of points, SC descriptors, and the count of points
        """
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
        # we may want to base the count on the num best_matchesber of large blobs
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
        """
        Classify an input image.

        * *image* - the input binary image.
        * *blobFilter* - Do a first pass where you only match objects
          that have the same number of blobs - speeds up computation
          and match quality.
        """
        points,descriptors,count,matchDict,matchStd = self._buildMatchDict(image, blobFilter)
        best = sys.maxint
        best_name = "No Match"
        for k,v in matchDict.items():
            if ( v < best ):
                best = v
                best_name = k

        return best_name, best, matchDict, matchStd

    def getTopNMatches(self,image,n=3, blobFilter = True):
        """
        Classify an input image and return the top n results.

        * *image* - the input binary image.
        * *n* - the number of results to return.
        * *blobFilter* - Do a first pass where you only match objects
          that have the same number of blobs - speeds up computation
          and match quality.
        """
        n = np.clip(n,1,len(self.labels))
        points,descriptors,count,matchDict,matchStd = self._buildMatchDict(image,blobFilter)
        best_matches = list(sorted(matchDict, key=matchDict.__getitem__))
        retList = []
        for k in best_matches:
            retList.append((k,matchDict[k]))
        return retList[0:n], matchDict, matchStd
