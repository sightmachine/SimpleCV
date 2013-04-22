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
        if( self.totalCount > 0 and self.correctCount ):
            return np.around(float(self.correctCount)/float(self.totalCount),4)
        else:
            return 0.00

    def getIncorrectPercent(self):
        if( self.totalCount > 0 and self.correctCount ):
            return np.around(float(self.incorrectCount)/float(self.totalCount),4)
        else:
            return 0.00

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

    def toString(self,pad_sz=7):
        retVal = 50*'#'
        retVal += "\n"
        retVal += "Total Data Points " + str(self.totalCount) + "\n"
        retVal += "Correct Data Points " + str(self.correctCount) + "\n"
        retVal += "Incorrect Data Points " + str(self.incorrectCount) + "\n"
        retVal += "\n"
        retVal += "Correct " + str(100.00*self.getCorrectPercent()) + "%\n"
        retVal += "Incorrect " + str(100.00*self.getIncorrectPercent()) + "% \n"
        retVal += 50*'#'
        retVal += '\n'
        wrdLen = 0
        sz = pad_sz
        for c in self.classList:
            if( len(c) > wrdLen ):
                wrdLen = len(c)

        top=(wrdLen+1)* " "
        for c in self.classList:
            top = top + c[0:np.min([len(c),sz])].rjust(sz," ")+"|"
        retVal += top+"\n"
        for i in range(0,len(self.classList)):
            line = self.classList[i].rjust(wrdLen," ")+"|"
            nums = self.confusionMatrix[i]
            for n in nums:
                line += str(n).rjust(sz," ") + "|"
            retVal += line+"\n"
        retVal += 50*'#'
        retVal += "\n"
        return retVal
