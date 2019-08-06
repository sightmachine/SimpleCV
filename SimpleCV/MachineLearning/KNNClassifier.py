from SimpleCV.base import *
from SimpleCV.ImageClass import Image, ImageSet
from SimpleCV.DrawingLayer import *
from SimpleCV.Features import FeatureExtractorBase
"""
This class is encapsulates almost everything needed to train, test, and deploy a
multiclass k-nearest neighbors image classifier. Training data should
be stored in separate directories for each class. This class uses the feature
extractor base class to  convert images into a feature vector. The basic workflow
is as follows.
1. Get data.
2. Setup Feature Extractors (roll your own or use the ones I have written).
3. Train the classifier.
4. Test the classifier.
5. Tweak parameters as necessary.
6. Repeat until you reach the desired accuracy.
7. Save the classifier.
8. Deploy using the classify method.
"""
class KNNClassifier:
    """
    This class encapsulates a K- Nearest Neighbor Classifier.

    See http://en.wikipedia.org/wiki/K-nearest_neighbor_algorithm
    """
    mClassNames = []
    mDataSetRaw = []
    mK=1
    mDistType = None
    mDataSetOrange = []
    mClassifier = None
    mLearner = None
    mFeatureExtractors = None
    mOrangeDomain = None

    mDistDict = {}

    def __init__(self,featureExtractors,k=1,dist=None):
        """
        dist = distance algorithm
        k = number of nearest neighbors
        """
        if not ORANGE_ENABLED:
            logger.warning("The required orange machine learning library is not installed")
            return None

        self.mDistDict = {
            'Hamming': orange.ExamplesDistanceConstructor_Hamming(), # Hamming - only good for discrete variables
            'Maximal': orange.ExamplesDistance_Maximal(),
            'Manhattan':orange.ExamplesDistanceConstructor_Manhattan(),
            'Euclidean':orange.ExamplesDistanceConstructor_Euclidean(),
            'Normalized':None
        }


        self.mFeatureExtractors =  featureExtractors
        if( dist is not None ):
            self.mDistType = self.mDistDict[dist];
        self.mK = k;
        self.mLearner = None
        self.mClassNames = []
        self.mDataSetRaw = []
        self.mDataSetOrange = []
        self.mClassifier = None
        self.mOrangeDomain = None

    def setK(self,k):
        """
        Note that training and testing will need to be redone.
        """
        self.mK = k

    def setDistanceMetric(self,dist):
        """
        Note that training and testing will need to be redone.
        """
        self.mDistType = self.mDistDict[dist]

    def load(cls, fname):
        """
        Load the classifier from file
        """
        return pickle.load(file(fname))
    load = classmethod(load)


    def save(self, fname):
        """
        Save the classifier to file
        """
        output = open(fname, 'wb')
        pickle.dump(self,output,2) # use two otherwise it w
        output.close()

    def __getstate__(self):
        mydict = self.__dict__.copy()
        self.mDataSetOrange = None
        del mydict['mDataSetOrange']
        self.mOrangeDomain = None
        del mydict['mOrangeDomain']
        return mydict

    def __setstate__(self, mydict):
        self.__dict__ = mydict
        colNames = []
        for extractor in self.mFeatureExtractors:
            colNames.extend(extractor.getFieldNames())
        self.mOrangeDomain = orange.Domain(list(map(orange.FloatVariable,colNames)),orange.EnumVariable("type",values=self.mClassNames))
        self.mDataSetOrange = orange.ExampleTable(self.mOrangeDomain,self.mDataSetRaw)


    def classify(self, image):
        """
        Classify a single image. Takes in an image and returns the string
        of the classification.

        Make sure you haved loaded the feauture extractors and the training data.

        """
        featureVector = []
        for extractor in self.mFeatureExtractors: #get the features
            feats = extractor.extract(image)
            if( feats is not None ):
                featureVector.extend(feats)
        featureVector.extend([self.mClassNames[0]])
        test = orange.ExampleTable(self.mOrangeDomain,[featureVector])
        c = self.mClassifier(test[0]) #classify
        return str(c) #return to class name


    def setFeatureExtractors(self, extractors):
        """
        Add a list of feature extractors to the classifier. These feature extractors
        must match the ones used to train the classifier. If the classifier is already
        trained then this method will require that you retrain the data.
        """
        self.mFeatureExtractors = extractors
        return None

    def _trainPath(self,path,className,subset,disp,verbose):
        count = 0
        files = []
        for ext in IMAGE_FORMATS:
            files.extend(glob.glob( os.path.join(path, ext)))
        if(subset > 0):
            nfiles = min(subset,len(files))
        else:
            nfiles = len(files)
        badFeat = False
        for i in range(nfiles):
            infile = files[i]
            if verbose:
                print("Opening file: " + infile)
            img = Image(infile)
            featureVector = []
            for extractor in self.mFeatureExtractors:
                feats = extractor.extract(img)
                if( feats is not None ):
                    featureVector.extend(feats)
                else:
                    badFeat = True

            if(badFeat):
                badFeat = False
                continue

            featureVector.extend([className])
            self.mDataSetRaw.append(featureVector)
            text = 'Training: ' + className
            self._WriteText(disp,img,text,Color.WHITE)
            count = count + 1
            del img
        return count

    def _trainImageSet(self,imageset,className,subset,disp,verbose):
        count = 0
        badFeat = False
        if (subset>0):
            imageset = imageset[0:subset]   
        for img in imageset:
            if verbose:
                print("Opening file: " + img.filename)
            featureVector = []
            for extractor in self.mFeatureExtractors:
                feats = extractor.extract(img)
                if( feats is not None ):
                    featureVector.extend(feats)
                else:
                    badFeat = True
                    
            if(badFeat):
                badFeat = False
                continue
            
            featureVector.extend([className])
            self.mDataSetRaw.append(featureVector)
            text = 'Training: ' + className
            self._WriteText(disp,img,text,Color.WHITE)
            count = count + 1
            del img
        return count

    def train(self,images,classNames,disp=None,subset=-1,savedata=None,verbose=True):
        """
        Train the classifier.
        images paramater can take in a list of paths or a list of imagesets
        images - the order of the paths or imagesets must be in the same order as the class type

        - Note all image classes must be in seperate directories
        - The class names must also align to the directories

        disp - if display is a display we show images and class label,
        otherwise nothing is done.

        subset - if subset = -1 we use the whole dataset. If subset = # then we
        use min(#images,subset)

        savedata - if save data is None nothing is saved. If savedata is a file
        name we save the data to a tab delimited file.

        verbose - print confusion matrix and file names
        returns [%Correct %Incorrect Confusion_Matrix]
        """
        count = 0
        self.mClassNames = classNames
        # fore each class, get all of the data in the path and train
        for i in range(len(classNames)):
            if ( isinstance(images[i], str) ):
                count = count + self._trainPath(images[i],classNames[i],subset,disp,verbose)
            else:
                count = count + self._trainImageSet(images[i],classNames[i],subset,disp,verbose)

        colNames = []
        for extractor in self.mFeatureExtractors:
            colNames.extend(extractor.getFieldNames())

        if(count <= 0):
            logger.warning("No features extracted - bailing")
            return None

        # push our data into an orange example table
        self.mOrangeDomain = orange.Domain(list(map(orange.FloatVariable,colNames)),orange.EnumVariable("type",values=self.mClassNames))
        self.mDataSetOrange = orange.ExampleTable(self.mOrangeDomain,self.mDataSetRaw)
        if(savedata is not None):
            orange.saveTabDelimited (savedata, self.mDataSetOrange)

        self.mLearner =  orange.kNNLearner()
        self.mLearner.k = self.mK
        if(self.mDistType is not None):
            self.mClassifier.distanceConstructor = self.mDistType
        self.mClassifier = self.mLearner(self.mDataSetOrange)
        correct = 0
        incorrect = 0
        for i in range(count):
            c = self.mClassifier(self.mDataSetOrange[i])
            test = self.mDataSetOrange[i].getclass()
            if verbose:
                print("original", test, "classified as", c)
            if(test==c):
                correct = correct + 1
            else:
                incorrect = incorrect + 1

        good = 100*(float(correct)/float(count))
        bad = 100*(float(incorrect)/float(count))

        confusion = 0
        if( len(self.mClassNames) > 2 ):
            crossValidator = orngTest.learnAndTestOnLearnData([self.mLearner],self. mDataSetOrange)
            confusion = orngStat.confusionMatrices(crossValidator)[0]

        if verbose:
            print(("Correct: "+str(good)))
            print(("Incorrect: "+str(bad)))
            classes = self.mDataSetOrange.domain.classVar.values
            print("\t"+"\t".join(classes))
            for className, classConfusions in zip(classes, confusion):
                print(("%s" + ("\t%i" * len(classes))) % ((className, ) + tuple(classConfusions)))
        return [good, bad, confusion]




    def test(self,images,classNames,disp=None,subset=-1,savedata=None,verbose=True):
        """
        Test the classifier.
        images paramater can take in a list of paths or a list of imagesets
        images - the order of the paths or imagesets must be in the same order as the class type

        - Note all image classes must be in seperate directories
        - The class names must also align to the directories

        disp - if display is a display we show images and class label,
        otherwise nothing is done.

        subset - if subset = -1 we use the whole dataset. If subset = # then we
        use min(#images,subset)

        savedata - if save data is None nothing is saved. If savedata is a file
        name we save the data to a tab delimited file.

        verbose - print confusion matrix and file names
        returns [%Correct %Incorrect Confusion_Matrix]
        """
        count = 0
        correct = 0
        self.mClassNames = classNames
        colNames = []
        for extractor in self.mFeatureExtractors:
            colNames.extend(extractor.getFieldNames())
            self.mOrangeDomain = orange.Domain(list(map(orange.FloatVariable,colNames)),orange.EnumVariable("type",values=self.mClassNames))

        dataset = []
        for i in range(len(classNames)):
            if ( isinstance(images[i],str) ):
                [dataset,cnt,crct] =self._testPath(images[i],classNames[i],dataset,subset,disp,verbose)
                count = count + cnt
                correct = correct + crct
            else:
                [dataset,cnt,crct] =self._testImageSet(images[i],classNames[i],dataset,subset,disp,verbose)
                count = count + cnt
                correct = correct + crct


        testData = orange.ExampleTable(self.mOrangeDomain,dataset)

        if savedata is not None:
            orange.saveTabDelimited (savedata, testData)

        confusion = 0
        if( len(self.mClassNames) > 2 ):
            crossValidator = orngTest.learnAndTestOnTestData([self.mLearner],self.mDataSetOrange,testData)
            confusion = orngStat.confusionMatrices(crossValidator)[0]

        good = 100*(float(correct)/float(count))
        bad = 100*(float(count-correct)/float(count))
        if verbose:
            print(("Correct: "+str(good)))
            print(("Incorrect: "+str(bad)))
            classes = self.mDataSetOrange.domain.classVar.values
            print("\t"+"\t".join(classes))
            for className, classConfusions in zip(classes, confusion):
                print(("%s" + ("\t%i" * len(classes))) % ((className, ) + tuple(classConfusions)))

        return [good, bad, confusion]

    def _testPath(self,path,className,dataset,subset,disp,verbose):
        count = 0
        correct = 0
        badFeat = False
        files = []
        for ext in IMAGE_FORMATS:
            files.extend(glob.glob( os.path.join(path, ext)))
        if(subset > 0):
            nfiles = min(subset,len(files))
        else:
            nfiles = len(files)
        for i in range(nfiles):
            infile = files[i]
            if verbose:
                print("Opening file: " + infile)
            img = Image(infile)
            featureVector = []
            for extractor in self.mFeatureExtractors:
                feats = extractor.extract(img)
                if( feats is not None ):
                    featureVector.extend(feats)
                else:
                    badFeat = True
            if( badFeat ):
                del img
                badFeat = False
                continue
            featureVector.extend([className])
            dataset.append(featureVector)
            test = orange.ExampleTable(self.mOrangeDomain,[featureVector])
            c = self.mClassifier(test[0])
            testClass = test[0].getclass()
            if(testClass==c):
                text =  "Classified as " + str(c)
                self._WriteText(disp,img,text, Color.GREEN)
                correct = correct + 1
            else:
                text =  "Mislassified as " + str(c)
                self._WriteText(disp,img,text, Color.RED)
            count = count + 1
            del img

        return([dataset,count,correct])

    def _testImageSet(self,imageset,className,dataset,subset,disp,verbose):
        count = 0
        correct = 0
        badFeat = False
        if(subset > 0):
            imageset = imageset[0:subset]
        for img in imageset:
            if verbose:
                print("Opening file: " + img.filename)
            featureVector = []
            for extractor in self.mFeatureExtractors:
                feats = extractor.extract(img)
                if( feats is not None ):
                    featureVector.extend(feats)
                else:
                    badFeat = True
            if( badFeat ):
                del img
                badFeat = False
                continue 
            featureVector.extend([className])
            dataset.append(featureVector)
            test = orange.ExampleTable(self.mOrangeDomain,[featureVector])
            c = self.mClassifier(test[0])
            testClass = test[0].getclass()
            if(testClass==c):
                text =  "Classified as " + str(c)
                self._WriteText(disp,img,text, Color.GREEN)
                correct = correct + 1
            else:   
                text =  "Mislassified as " + str(c)
                self._WriteText(disp,img,text, Color.RED)
            count = count + 1
            del img
            
        return([dataset,count,correct])

    def _WriteText(self, disp, img, txt,color):
        if(disp is not None):
            txt = ' ' + txt + ' '
            img = img.adaptiveScale(disp.resolution)
            layer = DrawingLayer((img.width,img.height))
            layer.setFontSize(60)
            layer.ezViewText(txt,(20,20),fgcolor=color)
            img.addDrawingLayer(layer)
            img.applyLayers()
            img.save(disp)
