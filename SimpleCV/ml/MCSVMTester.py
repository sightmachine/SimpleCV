from numpy import *
from SimpleCV.Display import Display, pg
from SimpleCV.EdgeHistogramFeatureExtractor import *
from SimpleCV.HueHistogramFeatureExtractor import *
from SimpleCV.BOFFeatureExtractor import *
import Orange
import os
import glob
import pickle
from SVMClassifier import *
from NaiveBayesClassifier import *
from KNNClassifier import *
from TreeClassifier import *

w = 800
h = 600
n=50

display = Display(resolution = (w,h))
hue_extractor = HueHistogramFeatureExtractor(mNBins=16)
edge_extractor = EdgeHistogramFeatureExtractor()
bof_extractor = BOFFeatureExtractor()
cat_train_path = "./data/cat/truth/"
cheeseburger_train_path = "./data/cheeseburger/truth/"
empire_train_path = "./data/empire/truth/"
cat_test_path = "./data/cat/test/"
cheeseburger_test_path = "./data/cheeseburger/test/"
data_test_path = "./data/empire/test/"
train_path = [cat_train_path,cheeseburger_train_path,empire_train_path]
test_path = [cat_test_path,cheeseburger_test_path,empire_train_path]
classes = ['cat','burger','empire']
##bof_extractor.generate(train_path)
##bof_extractor.save('codebook.png','cbdata.txt')
bof_extractor.load('cbdata.txt')
print('###############################################################################')
print('KNN')
classifierKNN = KNNClassifier([hue_extractor])#
print('Train')
classifierKNN.train(train_path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierKNN.test(test_path,classes,disp=display,subset=n)
classifierKNN.save('knn.pkl')
print('###############################################################################')
print('Vanilla Tree')
classifierTree = TreeClassifier([hue_extractor])#
print('Train')
classifierTree.train(train_path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierTree.test(test_path,classes,disp=display,subset=n)
classifierTree.save('tree.pkl')
print('###############################################################################')
print('Boosted Tree')
classifierBoostedTree = TreeClassifier([hue_extractor],flavor='Boosted')#
print('Train')
classifierBoostedTree.train(train_path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierBoostedTree.test(test_path,classes,disp=display,subset=n)
classifierBoostedTree.save('boosted.pkl')
print('###############################################################################')
print('Bagged Tree')
classifierBaggedTree = TreeClassifier([hue_extractor],flavor='Bagged')#
print('Train')
classifierBaggedTree.train([cat_train_path,cheeseburger_train_path],['cat','burger'],disp=display,subset=n)
[pos,neg,confuse] = classifierBaggedTree.test([cat_test_path,cheeseburger_test_path],['cat','burger'],disp=display,subset=n)
classifierBaggedTree.save('bagged.pkl')
print('###############################################################################')
print('Forest')
classifierForest = TreeClassifier([hue_extractor],flavor='Forest')#
print('Train')
classifierForest.train(train_path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierForest.test(test_path,classes,disp=display,subset=n)
classifierForest.save('forest.pkl')

print('###############################################################################')
print('Bayes')
classifierBayes = NaiveBayesClassifier([hue_extractor])#,edge_extractor])
print('Train')
classifierBayes.train(train_path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierBayes.test(test_path,classes,disp=display,subset=n)
classifierBayes.save('bayes.pkl')
print('###############################################################################')
print('SVMPoly')
#Set up am SVM with a poly kernel
props ={
        'KernelType':'Poly', #default is a RBF Kernel
        'SVMType':'C',     #default is C 
        'nu':None,          # NU for SVM NU
        'c':None,           #C for SVM C - the slack variable
        'degree':3,      #degree for poly kernels - defaults to 3
        'coef':None,        #coef for Poly/Sigmoid defaults to 0
        'gamma':None,       #kernel param for poly/rbf/sigma - default is 1/#samples       
    }
classifier = SVMClassifier([hue_extractor],props)#,edge_extractor])
classifier.train(train_path,classes,disp=display,subset=n) #train
[pos,neg,confuse] = classifier.test(test_path,classes,disp=display,subset=n)
classifier.save('PolySVM.pkl')
print('###############################################################################')
print('SVMRBG')
# now try an RBF kernel
props ={
        'KernelType':'RBF', #default is a RBF Kernel
        'SVMType':'NU',     #default is C 
        'nu':None,          # NU for SVM NU
        'c':None,           #C for SVM C - the slack variable
        'degree':None,      #degree for poly kernels - defaults to 3
        'coef':None,        #coef for Poly/Sigmoid defaults to 0
        'gamma':None,       #kernel param for poly/rbf/sigma - default is 1/#samples       
    }
classifier.setProperties(props)
classifier.train(train_path,classes,disp=display,subset=n)
[pos,neg,confuse] = classifier.test(test_path,classes,disp=display,subset=n)
classifier.save('RBFSVM.pkl')




