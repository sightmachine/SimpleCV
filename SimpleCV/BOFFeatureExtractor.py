from SimpleCV.base import *
from SimpleCV.ImageClass import Image
from SimpleCV.FeatureExtractorBase import *
import scipy.cluster.vq as cluster #for kmeans
import glob
import os
import abc

class BOFFeatureExtractor(object):
    
    mPatchSize = (11,11)
    mNumCodes = 128
    
    def __init__(self,patchsz=(11,11),numcodes=256):
        self.mPatchSize = patchsz
        self.mNumCodes = numcodes
    
    def generate(self,imgdirs,numcodes=256,sz=(11,11),imgs_per_dir=50):
        """
        WARNING: THIS METHOD WILL TAKE FOREVER
        """
        rawFeatures = np.zeros(sz[0]*sz[1])
        for path in imgdirs:
            fcount = 0
            files = glob.glob( os.path.join(path, '*.jpg'))
            if(len(files) >= imgs_per_dir):
                for i in range(imgs_per_dir):
                    infile = files[i]
                    print "Opening file: " + infile
                    img = Image(infile)
                    newFeat = self._getPatches(img)
                    print "     Got " + str(len(newFeat)) + " features."
                    rawFeatures = np.vstack((rawFeatures,newFeat))
                    #rawFeatures.extend(newFeat)
                    del img
        print "=================================="
        print "Got " + str(len(rawFeatures)) + " features "
        print "Doing K-Means .... this will take a long ass time"
        centroids = self._makeCodebook(rawFeatures)
        retVal = self._codebook2Img(centroids,self.mPatchSize,self.mNumCodes,(16,8),4)
        retVal.save('codebook.png')
        
    def _makeCodebook(self,data):
        """
        Do the k-means ... this is slow as as shit
        """
        [centroids, membership] = cluster.kmeans2(data,self.mNumCodes, minit='points')
        return(centroids)
        
    def _img2Codebook(self, img, patchsize, count, patch_arrangement, spacersz):
        """
        img = the image
        patchsize = the patch size (ususally 11x11)
        count = total codes
        patch_arrangement = how are the patches grided in the image (eg 128 = (8x16) 256=(16x16) )
        spacersz = the number of pixels between patches
        """
        for widx in range(patch_arrangement[0]):
            for hidx in range(patch_arrangement[1]):
                x = (widx*patchsz[0])+((widx+1)*spacersz)
                y = (hidx*patchsz[1])+((hidx+1)*spacersz)
                temp = Image.crop(x,y,patchsz[0],patchsz[1])

        
        
    def _codebook2Img(self, cb, patchsize, count, patch_arrangement, spacersz):
        """
        cb = the codebook
        patchsize = the patch size (ususally 11x11)
        count = total codes
        patch_arrangement = how are the patches grided in the image (eg 128 = (8x16) 256=(16x16) )
        spacersz = the number of pixels between patches
        """
        w = (patchsize[0]*patch_arrangement[0])+((patch_arrangement[0]+1)*spacersz)
        h = (patchsize[1]*patch_arrangement[1])+((patch_arrangement[1]+1)*spacersz)
        bm = cv.CreateImage((w,h), cv.IPL_DEPTH_8U, 1)
        cv.Zero(bm)
        img = Image(bm)
        count = 0
        for widx in range(patch_arrangement[0]):
            for hidx in range(patch_arrangement[1]):
                x = (widx*patchsize[0])+((widx+1)*spacersz)
                y = (hidx*patchsize[1])+((hidx+1)*spacersz)
                temp = Image(cb[count,:].reshape(patchsize[0],patchsize[1]))    
                img.blit(temp,pos=(x,y))
                count = count + 1
        return img
        
    def _getPatches(self,img):
        #retVal = [] # may need to go to np.array
        img2 = img.toHLS()
        lmat = cv.CreateImage((img.width,img.height), cv.IPL_DEPTH_8U, 1)
        patch = cv.CreateImage(self.mPatchSize,cv.IPL_DEPTH_8U,1)
        cv.Split(img2.getBitmap(),None,lmat,None,None)
        wsteps = img2.width/self.mPatchSize[0]
        hsteps = img2.height/self.mPatchSize[1]
        w=self.mPatchSize[0]
        h=self.mPatchSize[1]
        length = w*h
        retVal = np.zeros(length)
        for widx in range(wsteps):
            for hidx in range(hsteps):
                cv.SetImageROI(lmat,(widx,hidx,w,h)) 
                cv.EqualizeHist(lmat,patch)
                cv.ResetImageROI(lmat)
                
                retVal = np.vstack((retVal,np.array(patch[:,:]).reshape(length)))
                #retVal.append()
        print retVal
        print retVal.shape
        return retVal

        
    
    def load(self,imgfile,datafile):
        return
    
    def save(self,imgfile,datafile):
        return
    
    def extract(self, img):
        """
        Given an image extract the feature vector. The output should be a list
        object of all of the features. These features can be of any interal type
        (string, float, integer) but must contain no sub lists.
        """
    
      
    def getFieldNames(self):
        """
        This method gives the names of each field in the feature vector in the
        order in which they are returned. For example, 'xpos' or 'width'
        """
    
    def getFieldTypes(self):
        """
        This method returns the field types
        - Do we need this - spec out 
        """

    def getNumFields(self):
        """
        This method returns the total number of fields in the feature vector.
        """
        return self.mNumCodes