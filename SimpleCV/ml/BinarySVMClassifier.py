from SimpleCV.base import *
from SimpleCV.ImageClass import Image
from SimpleCV.DrawingLayer import *
from SimpleCV.FeatureExtractorBase import *
import orange
import os
import glob
import time
"""
This is more or less a hack space right now so I can do a proof of concept
on some of the ML stuff
"""
#KAS - we need a way to save and load the feature extractors from file
class BinarySVMClassifier:
    mClassAName = "A"
    mClassBName = "B"
    mDataSetRaw = [] 
    mDataSetOrange = []
    mClassifier = None
    mFeatureExtractors = None
    mOrangeDomain = None
    mClassVals = None
    
    def __init__(self,classAName,classBName,featureExtractors):
        self.mClassAName = classAName
        self.mClassBName = classBName
        self.mFeatureExtractors =  featureExtractors
    
    def load(self, fname):
        """
        Load the classifier from file
        """
        return None
    
    def save(self, fname):
        """
        Save the classifier to file
        """
        return False
    
    def classify(self, image, feature_extractors=None):
        return None
    
    def setFeatureExtractors(self, extractors):
        self.mFeatureExtractors = extractors
        return None
    
    def _trainPath(self,path,className,subset,disp):
        count = 0
        files = glob.glob( os.path.join(path, '*.jpg'))
        if(subset > 0):
            nfiles = min(subset,len(files))
        else:
            nfiles = len(files)
        badFeat = False   
        for i in range(nfiles):
            infile = files[i]
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
        
    def train(self,pathA,pathB,disp=None,subset=-1,savedata=None):
        count = 0
        count = self._trainPath(pathA,self.mClassAName,subset,disp)
        count = count + self._trainPath(pathB,self.mClassBName,subset,disp)
           
        colNames = []
        for extractor in self.mFeatureExtractors:
            colNames.extend(extractor.getFieldNames())
            
        if(count <= 0):
            warnings.warn("No features extracted - bailing")
            return None
        
        self.mClassVals = [self.mClassAName,self.mClassBName]
        self.mOrangeDomain = orange.Domain(map(orange.FloatVariable,colNames),orange.EnumVariable("type",values=self.mClassVals))
        self.mDataSetOrange = orange.ExampleTable(self.mOrangeDomain,self.mDataSetRaw)
        if(savedata is not None):
            orange.saveTabDelimited (savedata, self.mDataSetOrange)

        #self.mClassifier = orange.BayesLearner(self.mDataSetOrange)
        svmProto = orange.SVMLearner()
        svmProto.kernel_type = orange.SVMLearner.Linear
        svmProto.svm_type = orange.SVMLearner.Nu_SVC
        #svmProto.probability = True
        svmProto.nu = 0.5
        self.mClassifier = svmProto(self.mDataSetOrange)
        correct = 0
        incorrect = 0
        for i in range(count):
            
            c = self.mClassifier(self.mDataSetOrange[i])
            test = self.mDataSetOrange[i].getclass()
            print "original", test, "classified as", c 
            if(test==c):
                correct = correct + 1
            else:
                incorrect = incorrect + 1
        print(correct)
        print(incorrect)
        good = 100*(float(correct)/float(count))
        bad = 100*(float(incorrect)/float(count))
        print("Correct: "+str(good))
        print("Incorrect: "+str(bad))
    
    def _testPath(self,path,className,subset,disp):
        count = 0
        correct = 0
        badFeat = False
        files = glob.glob( os.path.join(path, '*.jpg'))
        if(subset > 0):
            nfiles = min(subset,len(files))
        else:
            nfiles = len(files)
        
        for i in range(nfiles):
            infile = files[i]
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
            self.mDataSetRaw.append(featureVector)
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
            
        return([count,correct])

    def test(self,pathA,pathB,disp=None,subset=-1,savedata=None):
        count = 0
        totalC = 0
        subcount = 0
        correct = 0
        incorrect = 0
        confusion = []
        names = []
        (cnt,crct) = self._testPath(pathA,self.mClassAName,subset,disp)
        count = count + cnt
        correct = correct + crct
        t = 100*(float(cnt-crct)/float(cnt))
        confusion.append([t,100.00-t])
        (cnt,crct) = self._testPath(pathB,self.mClassBName,subset,disp)
        count = count + cnt
        correct = correct + crct
        t = 100*(float(cnt-crct)/float(cnt))
        confusion.append([t,100.00-t])

        print(confusion)
        total_correct = 100*float(correct)/float(count)
        print("OVERALL ACCURACY: "+str(total_correct))
        if savedata is not None:
            colNames = []
            for extractor in self.mFeatureExtractors:
                colNames.extend(extractor.getFieldNames())
            self.mClassVals = [self.mClassAName,self.mClassBName]
            self.mOrangeDomain = orange.Domain(map(orange.FloatVariable,colNames),orange.EnumVariable("type",values=self.mClassVals))
            self.mDataSetOrange = orange.ExampleTable(self.mOrangeDomain,self.mDataSetRaw)
            orange.saveTabDelimited (savedata, self.mDataSetOrange)

    
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
    