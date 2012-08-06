from SimpleCV.base import *
from SimpleCV.ImageClass import Image
from SimpleCV.DrawingLayer import *
from SimpleCV.Features import FeatureExtractorBase


"""
This class is encapsulates almost everything needed to train, test, and deploy a
multiclass decision tree / forest image classifier. Training data should
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
class TreeClassifier:
    """
    This method encapsulates a number of tree-based machine learning approaches
    and associated meta algorithms. 
    
    Decision trees:
    http://en.wikipedia.org/wiki/Decision_trees
    
    boosted adpative decision trees
    http://en.wikipedia.org/wiki/Adaboost
    
    random forrests
    http://en.wikipedia.org/wiki/Random_forest
    
    bagging (bootstrap aggregating)
    http://en.wikipedia.org/wiki/Bootstrap_aggregating
    """
    mClassNames = []
    mDataSetRaw = []
    mDataSetOrange = []
    mClassifier = None
    mLearner = None
    mTree = None
    mFeatureExtractors = None
    mOrangeDomain = None
    mFlavorParams = None

    mTreeTypeDict = {
        "Tree":0,    # A vanilla classification tree
        "Bagged":1, # Bootstrap aggregating aka bagging - make new data sets and test on them
        "Forest":2, # Lots of little trees
        "Boosted":3 # Highly optimized trees. 
    }
    
    mforestFlavorDict = {
        "NTrees":100, #number of trees in our forest
        "NAttributes":None # number of attributes per split sqrt(features) is default
     }
    mBoostedFlavorDict = {
        "NClassifiers":10, #number of learners 
    }
    mBaggedFlavorDict = {
        "NClassifiers":10, #numbers of classifiers / tree splits
    }

    def __init__(self,featureExtractors=[],flavor='Tree',flavorDict=None):
        """
        dist = distance algorithm
        k = number of nearest neighbors
        """
        if not ORANGE_ENABLED:
            logger.warning("I'm sorry, but you need the orange machine learning library installed to use this")
            return None
        
        self.mClassNames = []
        self.mDataSetRaw = []
        self.mDataSetOrange = []
        self.mClassifier = None
        self.mLearner = None
        self.mTree = None
        self.mFeatureExtractors = None
        self.mOrangeDomain = None
        self.mFlavorParams = None        
        self.mFlavor = self.mTreeTypeDict[flavor]
        if(flavorDict is None):
            if(self.mFlavor == self.mTreeTypeDict["Bagged"]):
                self.mFlavorParams = self.mBaggedFlavorDict 
            elif(self.mFlavor == self.mTreeTypeDict["Forest"]):
                self.mFlavorParams = self.mforestFlavorDict #mmmm tastes like   pinecones and squirrels 
            elif(self.mFlavor == self.mTreeTypeDict["Boosted"]):
                self.mFlavorParams = self.mBoostedFlavorDict
        else:
            self.mFlavorParams = flavorDict
        self.mFeatureExtractors =  featureExtractors

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
        self.mLearner = None
        del mydict['mLearner']
        self.mTree = None
        del mydict['mTree']        
        return mydict
    
    def __setstate__(self, mydict):
        self.__dict__ = mydict
        colNames = []
        for extractor in self.mFeatureExtractors:
            colNames.extend(extractor.getFieldNames())
        self.mOrangeDomain = orange.Domain(map(orange.FloatVariable,colNames),orange.EnumVariable("type",values=self.mClassNames))
        self.mDataSetOrange = orange.ExampleTable(self.mOrangeDomain,self.mDataSetRaw)
        if(self.mFlavor == 0):
            self.mLearner =  orange.TreeLearner()      
            self.mClassifier = self.mLearner(self.mDataSetOrange)            
        elif(self.mFlavor == 1): #bagged
            self.mTree =  orange.TreeLearner()
            self.mLearner = orngEnsemble.BaggedLearner(self.mTree,t=self.mFlavorParams["NClassifiers"])
            self.mClassifier = self.mLearner(self.mDataSetOrange) 
        elif(self.mFlavor == 2):#forest
            self.mTree =  orange.TreeLearner()
            self.mLearner =  orngEnsemble.RandomForestLearner(trees=self.mFlavorParams["NTrees"], attributes=self.mFlavorParams["NAttributes"])
            self.mClassifier = self.mLearner(self.mDataSetOrange) 
        elif(self.mFlavor == 3):#boosted
            self.mTree =  orange.TreeLearner()
            self.mLearner = orngEnsemble.BoostedLearner(self.mTree,t=self.mFlavorParams["NClassifiers"])
            self.mClassifier = self.mLearner(self.mDataSetOrange)   
        
    
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
                print "Opening file: " + infile
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
        
    def train(self,paths,classNames,disp=None,subset=-1,savedata=None,verbose=True):
        """
        Train the classifier.
        paths the order of the paths in the same order as the class type 
        
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
        #if( (self.mFlavor == 1 or self.mFlavor == 3) and len(classNames) > 2):
        #    logger.warning("Boosting / Bagging only works for binary classification tasks!!!")
            
        count = 0
        self.mClassNames = classNames
        # for each class, get all of the data in the path and train
        for i in range(len(classNames)):
            count = count + self._trainPath(paths[i],classNames[i],subset,disp,verbose)
           
        colNames = []
        for extractor in self.mFeatureExtractors:
            colNames.extend(extractor.getFieldNames())
        
        if(count <= 0):
            logger.warning("No features extracted - bailing")
            return None
        
        self.mOrangeDomain = orange.Domain(map(orange.FloatVariable,colNames),orange.EnumVariable("type",values=self.mClassNames))
        self.mDataSetOrange = orange.ExampleTable(self.mOrangeDomain,self.mDataSetRaw)
        if(savedata is not None):
            orange.saveTabDelimited (savedata, self.mDataSetOrange)
        
        if(self.mFlavor == 0):
            self.mLearner =  orange.TreeLearner()      
            self.mClassifier = self.mLearner(self.mDataSetOrange)            
        elif(self.mFlavor == 1): #bagged
            self.mTree =  orange.TreeLearner()
            self.mLearner = orngEnsemble.BaggedLearner(self.mTree,t=self.mFlavorParams["NClassifiers"])
            self.mClassifier = self.mLearner(self.mDataSetOrange) 
        elif(self.mFlavor == 2):#forest
            self.mTree =  orange.TreeLearner()
            self.mLearner =  orngEnsemble.RandomForestLearner(trees=self.mFlavorParams["NTrees"], attributes=self.mFlavorParams["NAttributes"])
            self.mClassifier = self.mLearner(self.mDataSetOrange) 
        elif(self.mFlavor == 3):#boosted
            self.mTree =  orange.TreeLearner()
            self.mLearner = orngEnsemble.BoostedLearner(self.mTree,t=self.mFlavorParams["NClassifiers"])
            self.mClassifier = self.mLearner(self.mDataSetOrange)     

        correct = 0
        incorrect = 0
        for i in range(count):
            c = self.mClassifier(self.mDataSetOrange[i])
            test = self.mDataSetOrange[i].getclass()
            if verbose:
                print "original", test, "classified as", c 
            if(test==c):
                correct = correct + 1
            else:
                incorrect = incorrect + 1
                
        good = 100*(float(correct)/float(count))
        bad = 100*(float(incorrect)/float(count))

        confusion = 0
        if( len(self.mClassNames) > 2 ):
            crossValidator = orngTest.learnAndTestOnLearnData([self.mLearner],self.mDataSetOrange)
            confusion = orngStat.confusionMatrices(crossValidator)[0]

        if verbose:
            print("Correct: "+str(good))
            print("Incorrect: "+str(bad))
            if( confusion != 0 ):
                classes = self.mDataSetOrange.domain.classVar.values
                print "\t"+"\t".join(classes)
                for className, classConfusions in zip(classes, confusion):
                    print ("%s" + ("\t%i" * len(classes))) % ((className, ) + tuple(    classConfusions))
                    
        if(self.mFlavor == 0):
            self._PrintTree(self.mClassifier)

        return [good, bad, confusion]


    
    
    def test(self,paths,classNames,disp=None,subset=-1,savedata=None,verbose=True):
        """
        Train the classifier.
        paths the order of the paths in the same order as the class type 
        
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
            if(self.mOrangeDomain is None):
                self.mOrangeDomain = orange.Domain(map(orange.FloatVariable,colNames),orange.EnumVariable("type",values=self.mClassNames))
        
        dataset = []
        for i in range(len(classNames)):
            [dataset,cnt,crct] =self._testPath(paths[i],classNames[i],dataset,subset,disp,verbose)
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
            print("Correct: "+str(good))
            print("Incorrect: "+str(bad))
            if( confusion != 0 ):
                classes = self.mDataSetOrange.domain.classVar.values
                print "\t"+"\t".join(classes)
                for className, classConfusions in zip(classes, confusion):
                    print ("%s" + ("\t%i" * len(classes))) % ((className, ) + tuple(    classConfusions))
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
                print "Opening file: " + infile
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
            
    def _PrintTree(self,x):
        #adapted from the orange documentation
        if type(x) == orange.TreeClassifier:
            self._PrintTree0(x.tree, 0)
        elif type(x) == orange.TreeNode:
            self._PrintTree0(x, 0)
        else:
            raise TypeError, "invalid parameter"

    def _PrintTree0(self,node,level):
        #adapted from the orange documentation
        if not node:
            print " "*level + "<null node>"
            return

        if node.branchSelector:
            nodeDesc = node.branchSelector.classVar.name
            nodeCont = node.distribution
            print "\n" + "   "*level + "%s (%s)" % (nodeDesc, nodeCont),
            for i in range(len(node.branches)):
                print "\n" + "   "*level + ": %s" % node.branchDescriptions[i],
                self._PrintTree0(node.branches[i], level+1)
        else:
            nodeCont = node.distribution
            majorClass = node.nodeClassifier.defaultValue
            print "--> %s (%s) " % (majorClass, nodeCont)
    
