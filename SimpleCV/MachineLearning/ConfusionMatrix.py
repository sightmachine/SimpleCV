from SimpleCV.base import *
from SimpleCV.ImageClass import Image

class ConfusionMatrix():
    def __init__(self,classList):
        self.classList = classList
        self.classCount = len(classList)
        self.confusionMatrix = np.zeros([self.classCount,self.classCount])
        self.correctCount = 0
        self.incorrectCount = 0
        self.totalCount = 0
        self.nameMap = {}
        idx = 0
        for obj in classList:
            self.nameMap[obj] = idx
            idx = idx + 1
            
    def addDataPoint(self,truth_name,test_name):
        self.confusionMatrix[self.nameMap[truth_name]][self.nameMap[test_name]] += 1
        if( truth_name == test_name ):
            self.correctCount += 1
        else:
            self.incorrectCount +=1

        self.totalCount += 1

    def getCorrectPercent(self):
        return np.around(float(self.correctCount)/float(self.totalCount),2)

    def getIncorrectPercent(self):
        return np.around(float(self.incorrectCount)/float(self.totalCount),2)

    def getClassCorrectPercent(self, className):
        total = float(np.sum(self.confusionMatrix[:,self.nameMap[className]]))
        correct = float(self.confusionMatrix[self.nameMap[className],self.nameMap[className]])
        if( correct == 0 or total == 0 ):
            return 0
        else:
            return np.around(correct/total,2)

    def getClassIncorrectPercent(self, className):
        total = float(np.sum(self.confusionMatrix[:,self.nameMap[className]]))
        correct = float(self.confusionMatrix[self.nameMap[className],self.nameMap[className]])
        incorrect = total-correct
        if( incorrect == 0 or total == 0 ):
            return 0
        else:
            return np.around(incorrect/total,2)

    def getClassCorrect(self, className):
        correct = self.confusionMatrix[self.nameMap[className],self.nameMap[className]]
        return correct

    def getClassIncorrect(self, className):
        total = np.sum(self.confusionMatrix[:,self.nameMap[className]])
        correct = self.confusionMatrix[self.nameMap[className],self.nameMap[className]]
        incorrect = total-correct
        return incorrect

            
    def getClassCount(self,className):
        return np.sum(self.confusionMatrix[:,self.nameMap[className]])

    def getMisclassifiedCount(self,className):
        # if we're class A, this returns the number of class B, C ...
        # that were classified as A
        count = np.sum(self.confusionMatrix[self.nameMap[className],:])
        correct = self.confusionMatrix[[self.nameMap[className]],self.nameMap[className]]
        total = count - correct
        return int(total[0])