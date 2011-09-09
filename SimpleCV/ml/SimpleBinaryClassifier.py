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

class SimpleBinaryClassifier:
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
        
    def train(self,pathA,pathB,disp=None,subset=-1):
        count = 0
        files = glob.glob( os.path.join(pathA, '*.jpg'))
        if(subset > 0):
            nfiles = min(subset,len(files))
        else:
            nfiles = len(files)
            
        for i in range(nfiles):
            infile = files[i]
            print "Class A opening file: " + infile
            img = Image(infile)
            featureVector = []
            for extractor in self.mFeatureExtractors:
                featureVector.extend(extractor.extract(img))
            featureVector.extend([self.mClassAName])
            self.mDataSetRaw.append(featureVector)
            text = 'Training: ' + self.mClassAName
            self._WriteText(disp,img,text,Color.WHITE)
            del img
            count = count + 1
            
        files = glob.glob( os.path.join(pathB, '*.jpg'))
        if(subset > 0):
            nfiles = min(subset,len(files))
        else:
            nfiles = len(files)
            
        for i in range(nfiles):
            infile = files[i]
            print "Class B opening file: " + infile
            img = Image(infile)
            featureVector = []
            for extractor in self.mFeatureExtractors:
                featureVector.extend(extractor.extract(img))
            featureVector.extend([self.mClassBName])
            self.mDataSetRaw.append(featureVector)
            text = 'Training: ' + self.mClassBName
            self._WriteText(disp,img,text,Color.WHITE)
            del img
            count = count + 1
        
        colNames = []
        for extractor in self.mFeatureExtractors:
            colNames.extend(extractor.getFieldNames())
        
        self.mClassVals = [self.mClassAName,self.mClassBName]
        self.mOrangeDomain = orange.Domain(map(orange.FloatVariable,colNames),orange.EnumVariable("type",values=self.mClassVals))
        self.mDataSetOrange = orange.ExampleTable(self.mOrangeDomain,self.mDataSetRaw)
        orange.saveTabDelimited ("image_data.tab", self.mDataSetOrange)

        self.mClassifier = orange.BayesLearner(self.mDataSetOrange)
        #svmProto = orange.SVMLearner()
        #svmProto.kernel_type = orange.SVMLearner.Linear
        #svmProto.svm_type = orange.SVMLearner.Nu_SVC
        #svmProto.probability = True
        #svmProto.nu = 0.5
        #self.mClassifier = svmProto(self.mDataSetOrange)
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
        
    def load(self,path):
        self.mDataSetOrange = orange.ExampleTable(path)
        if(self.mDataSetOrange is not None):
            print('Loading '+path)
            self.mClassifier = orange.BayesLearner(self.mDataSetOrange)
            colNames = []
            for extractor in self.mFeatureExtractors:
                colNames.extend(extractor.getFieldNames())
            self.mClassVals = [self.mClassAName,self.mClassBName]
            self.mOrangeDomain = self.mClassifier.domain


    
    def test(self,pathA,pathB,disp=None,subset=-1):
        count = 0
        totalC = 0
        subcount = 0
        correct = 0
        incorrect = 0
        confusion = []
        names = []
        files = glob.glob( os.path.join(pathA, '*.jpg'))
        if(subset > 0):
            nfiles = min(subset,len(files))
        else:
            nfiles = len(files)
            
        for i in range(nfiles):
            infile = files[i]
            print "Class A opening file: " + infile
            img = Image(infile)
            names.append(infile)
            featureVector = []
            for extractor in self.mFeatureExtractors:
                featureVector.extend(extractor.extract(img))
            featureVector.extend([self.mClassAName])
            self.mDataSetRaw.append(featureVector)
            test = orange.ExampleTable(self.mOrangeDomain,[featureVector])
            c = self.mClassifier(test[0])
            testClass = test[0].getclass()
            if(testClass==c):
                text =  "Classified as " + str(c)
                self._WriteText(disp,img,text, Color.GREEN)
                correct = correct + 1
                totalC = totalC + 1 
            else:
                text =  "Misclassified as " + str(c)
                self._WriteText(disp,img,text, Color.RED)
                incorrect = incorrect + 1
            count = count + 1
            subcount = subcount + 1
        t = 100*(float(incorrect)/float(subcount))
        confusion.append([t,100.00-t])
            #time.sleep(1)

        correct = 0
        incorrect = 0
        subcount = 0
        files = glob.glob( os.path.join(pathB, '*.jpg'))
        if(subset > 0):
            nfiles = min(subset,len(files))
        else:
            nfiles = len(files)
            
        for i in range(nfiles):
            infile = files[i]
            print "Class B opening file: " + infile
            img = Image(infile)
            names.append(infile)
            featureVector = []
            for extractor in self.mFeatureExtractors:
                featureVector.extend(extractor.extract(img))
            featureVector.extend([self.mClassBName])
            self.mDataSetRaw.append(featureVector)
            test = orange.ExampleTable(self.mOrangeDomain,[featureVector])
            c = self.mClassifier(test[0])
            testClass = test[0].getclass()
            if(testClass==c):
                text =  "Classified as " + str(c)
                self._WriteText(disp,img,text,Color.GREEN)
                correct = correct + 1
                totalC = totalC + 1
            else:
                text =  "Misclassified as " + str(c)
                self._WriteText(disp,img,text,Color.RED)
                incorrect = incorrect + 1
            count = count + 1
            subcount = subcount + 1
        t = 100*(float(incorrect)/float(subcount))
        confusion.append([t,100.00-t])
            #time.sleep(1)
            
        print(confusion)
        total_correct = 100*float(totalC)/float(count)
        print("OVERALL ACCURACY: "+str(total_correct))
        colNames = []
        for extractor in self.mFeatureExtractors:
            colNames.extend(extractor.getFieldNames())
        self.mClassVals = [self.mClassAName,self.mClassBName]
        self.mOrangeDomain = orange.Domain(map(orange.FloatVariable,colNames),orange.EnumVariable("type",values=self.mClassVals))
        self.mDataSetOrange = orange.ExampleTable(self.mOrangeDomain,self.mDataSetRaw)
        orange.saveTabDelimited ("image_data.tab", self.mDataSetOrange)

    
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
    