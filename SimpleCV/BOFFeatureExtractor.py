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
    mPadding = 0
    mLayout = (8,16)
    mCodebookImg = None
    mCodebook = None
    
    def __init__(self,patchsz=(11,11),numcodes=128,imglayout=(8,16),padding=0):
        self.mPadding = padding
        self.mLayout = imglayout
        self.mPatchSize = patchsz
        self.mNumCodes = numcodes
    
    def generate(self,imgdirs,numcodes=128,sz=(11,11),imgs_per_dir=50,img_layout=(8,16),padding=0):
        """
        WARNING: THIS METHOD WILL TAKE FOREVER
        """
        self.mPadding = padding
        self.mLayout = img_layout
        self.mNumCodes = numcodes
        self.mPatchSize = sz
        rawFeatures = np.zeros(sz[0]*sz[1])#fakeout numpy so we can use vstack
        for path in imgdirs:
            fcount = 0
            files = glob.glob( os.path.join(path, '*.jpg'))
            nimgs = min(len(files),imgs_per_dir)
            for i in range(nimgs):
                print(path+" "+str(i)+" of "+str(imgs_per_dir))
                infile = files[i]
                print "Opening file: " + infile
                img = Image(infile)
                newFeat = self._getPatches(img)
                print "     Got " + str(len(newFeat)) + " features."
                rawFeatures = np.vstack((rawFeatures,newFeat))
                del img
        rawFeatures = rawFeatures[1:,:] # pop the fake value we put on the top
        print "=================================="
        print "Got " + str(len(rawFeatures)) + " features "
        print "Doing K-Means .... this take a long time"
        self.mCodebook = self._makeCodebook(rawFeatures)
        self.mCodebookImg = self._codebook2Img(self.mCodebook,self.mPatchSize,self.mNumCodes,self.mLayout,self.mPadding)
        self.mCodebookImg.save('codebook.png')
        
        
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
        img = img.toHLS()
        lmat = cv.CreateImage((img.width,img.height), cv.IPL_DEPTH_8U, 1)
        patch = cv.CreateImage(patchsize,cv.IPL_DEPTH_8U,1)
        cv.Split(img.getBitmap(),None,lmat,None,None)
        w = patchsize[0]
        h = patchsize[1]
        length = w*h
        retVal = np.zeros(length)
        for widx in range(patch_arrangement[0]):
            for hidx in range(patch_arrangement[1]):
                x = (widx*patchsize[0])+((widx+1)*spacersz)
                y = (hidx*patchsize[1])+((hidx+1)*spacersz)
                cv.SetImageROI(lmat,(x,y,w,h))
                cv.Copy(lmat,patch)
                cv.ResetImageROI(lmat)
                retVal = np.vstack((retVal,np.array(patch[:,:]).reshape(length)))
        retVal = retVal[1:,:]
        return retVal                

        
        
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
                x = (widx*self.mPatchSize[0])
                y = (hidx*self.mPatchSize[1])
                cv.SetImageROI(lmat,(x,y,w,h)) 
                cv.EqualizeHist(lmat,patch)
                #cv.Copy(lmat,patch)
                cv.ResetImageROI(lmat)
                
                retVal = np.vstack((retVal,np.array(patch[:,:]).reshape(length)))
                #retVal.append()
        retVal = retVal[1:,:] # pop the fake value we put on top of the stack
        return retVal

        
    
    def load(self,datafile):
        myFile = open(datafile, 'r')
        temp = myFile.readline()
        print(temp)
        self.mNumCodes = int(myFile.readline())
        print(self.mNumCodes)
        w = int(myFile.readline())
        h = int(myFile.readline())
        self.mPatchSize = (w,h)
        print(self.mPatchSize)
        self.mPadding = int(myFile.readline())
        print(self.mPadding)
        w = int(myFile.readline())
        h = int(myFile.readline())
        self.mLayout = (w,h)
        print(self.mLayout)
        imgfname = myFile.readline().strip()
        print(imgfname)
        self.mCodebookImg = Image(imgfname)        
        self.mCodebook = self._img2Codebook(self.mCodebookImg,
                                            self.mPatchSize,
                                            self.mNumCodes,
                                            self.mLayout,
                                            self.mPadding)
        print(self.mCodebook)        
        return
    
    def save(self,imgfname,datafname):
        myFile = open(datafname,'w')
        myFile.write("BOF Codebook Data\n")
        myFile.write(str(self.mNumCodes)+"\n")
        myFile.write(str(self.mPatchSize[0])+"\n")
        myFile.write(str(self.mPatchSize[1])+"\n")
        myFile.write(str(self.mPadding)+"\n")
        myFile.write(str(self.mLayout[0])+"\n")
        myFile.write(str(self.mLayout[1])+"\n")
        myFile.write(imgfname+"\n")
        myFile.close()
        if(self.mCodebookImg is None):
            self._codebook2Img(self.mCodebook,self.mPatchSize,self.mNumCodes,self.mLayout,self.mPadding)
        self.mCodebookImg.save(imgfname)
        return
    
    def extract(self, img):
        """
        Given an image extract the feature vector. The output should be a list
        object of all of the features. These features can be of any interal type
        (string, float, integer) but must contain no sub lists.
        """
        data = self._getPatches(img)
        p = spsd.cdist(data,self.mCodebook)
        codes = np.argmin(p,axis=1)
        [retVal,foo] = np.histogram(codes,self.mNumCodes,normed=True,range=(0,self.mNumCodes-1))
        return retVal
        
    def reconstruct(self,img):
        retVal = cv.CreateImage((img.width,img.height), cv.IPL_DEPTH_8U, 1)
        data = self._getPatches(img)
        p = spsd.cdist(data,self.mCodebook)
        foo = p.shape[0]
        codes = np.argmin(p,axis=1)   
        count = 0
        wsteps = img.width/self.mPatchSize[0]
        hsteps = img.height/self.mPatchSize[1]
        w=self.mPatchSize[0]
        h=self.mPatchSize[1]
        length = w*h
        retVal = Image(retVal)
        for widx in range(wsteps):
            for hidx in range(hsteps):
                x = (widx*self.mPatchSize[0])
                y = (hidx*self.mPatchSize[1])
                p = codes[count]
                temp = Image(self.mCodebook[p,:].reshape(self.mPatchSize[0],self.mPatchSize[1]))    
                retVal.blit(temp,pos=(x,y))
                count = count + 1
        return retVal#Image(retVal)
        
    def getFieldNames(self):
        """
        This method gives the names of each field in the feature vector in the
        order in which they are returned. For example, 'xpos' or 'width'
        """
        retVal = []
        for widx in range(self.mLayout[0]):
            for hidx in range(self.mLayout[1]):
                temp = "CB_R"+str(widx)+"_C"+str(hidx)
                retVal.append(temp)
        return retVal

    
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