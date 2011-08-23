from SimpleCV import *
from numpy import *
from SimpleCV.Display import Display, pg
from SimpleCV.EdgeHistogramFeatureExtractor import *
from SimpleCV.HueHistogramFeatureExtractor import *
import Orange
from SimpleBinaryClassifier import *

w = 800
h = 600
display = Display(resolution = (w,h))
hue_extractor = HueHistogramFeatureExtractor()
edge_extractor = EdgeHistogramFeatureExtractor()
classifier = SimpleBinaryClassifier('cat','cheeseburger',[hue_extractor])#,edge_extractor])
cat_train_path = "./data/cat/truth/"
cheeseburger_train_path = "./data/cheeseburger/truth/"
cat_test_path = "./data/cat/test/"
cheeseburger_test_path = "./data/cheeseburger/test/"
classifier.train(cat_train_path,cheeseburger_train_path,disp=display)
classifier.test(cat_test_path,cheeseburger_test_path,disp=display)