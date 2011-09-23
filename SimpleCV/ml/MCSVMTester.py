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

w = 800
h = 600
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
classes = ['cat','cheeseburger','empire']
##bof_extractor.generate(train_path)
##bof_extractor.save('codebook.png','cbdata.txt')
bof_extractor.load('cbdata.txt')

#
#classifier = SVMClassifier(classes,[hue_extractor,bof_extractor])#,edge_extractor])
#
#
#classifier.train(train_path,classes,disp=display,subset=10)
##classifier.test(test_path,classes,disp=display,subset=50)
#bof_extractor.mCodebookImg = None
#classifier.save('test.pkl')
#print 'pickled'
#classifier2 = SVMClassifier(classes,[hue_extractor,bof_extractor])#,edge_extractor])
classifier2 = SVMClassifier.load('test.pkl')
#input = open('data.pkl', 'rb')
#print 'starting load'
#classifier2 = pickle.load(input)
#input.close()
#print 'let us give this a shot'
print(classifier2)
classifier2.test(test_path,classes,disp=display,subset=5)
#print('whoa! that worked')




