from SimpleCV.base import *
from SimpleCV.Features.Features import Feature, FeatureSet
from SimpleCV.Color import Color
from SimpleCV.ImageClass import Image
from SimpleCV.Features.Detection import ShapeContextDescriptor
import math
import scipy.stats as sps 

class ShapeContextClassifier():
    
   def  __init__(self,images,labels):
       self.imgMap = {}
       self.ptMap = {}
       self.descMap = {} 
       self.labels = labels
       self.images = images
       for i in range(0,len(images)):
           print "precomputing " + images[i].filename
           self.imgMap[labels[i]] = images[i]
           pts,desc = self._image2FeatureVector(images[i])
           self.ptMap[labels[i]] = pts
           self.descMap[labels[i]] = desc 

   def _image2FeatureVector(self,img):
       #IMAGES MUST BE WHITE ON BLACK!
       fulllist = []
       raw_descriptors = []
       blobs = img.findBlobs()
       if( blobs is not None ):
           for b in blobs:
               fulllist += b._filterSCPoints()
               
               raw_descriptors = blobs[0]._generateSC(fulllist) 
       return fulllist,raw_descriptors


   def _getMatch(self,model_scd,test_scd):
       correspondence,distance = self._doMatching(model_scd,test_scd)
       return self._matchQuality(distances)

   def _doMatching(self,model_scd,test_scd):       
        osc = test_scd
        mysc = model_scd
        otherIdx = []
        distance = [] 
        from sklearn import neighbors
        knn = neighbors.KNeighborsClassifier()
        knn.fit(mysc,range(0,len(mysc)))
        results = []
        for sample in osc:
            best = knn.predict(sample)
            idx = best[0]
            scd = mysc[idx]
            diff = (sample-scd)**2
            sums = (sample+scd)
            temp = 0.5*np.sum(diff)/np.sum(sums)
            if( math.isnan(temp) ):
                temp = sys.maxint
            distance.append(temp)
            
        # We may want this to be a reciprical relationship. Given blobs a,b with points
        # a1 .... an and b1. ... bn it is only a1 and b1 are a match if and only if
        # they are both each other's best match. 
 #        for scd in mysc:
#             results = []
#             for sample in osc:



#                 diff = (sample-scd)**2
#                 sums = (sample+scd)
#                 temp = 0.5*np.sum(diff)/np.sum(sums)
#                 if( math.isnan(temp) ):
#                     temp = sys.maxint
#                 results.append(temp)

#             distance.append(np.min(results))
#             idx = np.where(results==np.min(results))[0] # where our value is min return the idx
#             if( len(idx) == 0  ):
#                 print "WARNING!!!"
#                 otherIdx.append(0) # we need to deal cleanly with ties here
#                 distance.append(sys.maxint) # where one patch matches closesly    
#             else:
#                 val = results[idx[0]] 
#                 otherIdx.append(idx[0]) # we need to deal cleanly with ties here
#                 distance.append(val) # where one patch matches closesly    

        return [otherIdx,distance]

   def _matchQuality(self,distances):
       distances = np.array(distances)
       sd = np.std(distances)
       x = np.mean(distances)
       min = np.min(distances)
       # not sure trimmed mean is perfect
       # realistically we should have some bimodal dist
       # and we want to throw away stuff with awful matches
       # so long as the number of points is not a huge
       # chunk of our points.
       tmean = sps.tmean(distances,(min,x+sd))
       return tmean

   def classify(self,image):
       points,descriptors = self._image2FeatureVector(image)
       matchDict = {}
       for key,value in self.descMap.items():
           correspondence, distances = self._doMatching(value,descriptors)
           result = self._matchQuality(distances)
           matchDict[key] = result
           #print key + " : " + str(result)

       best = sys.maxint
       best_name = "No Match"
       for k,v in matchDict.items():
           if ( v < best ):
               best = v 
               best_name = k
           
       return best_name, matchDict
