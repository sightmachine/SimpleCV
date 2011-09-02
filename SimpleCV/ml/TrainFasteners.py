from SimpleCV import *
from numpy import *
from SimpleCV.Display import Display, pg
from SimpleCV.EdgeHistogramFeatureExtractor import *
from SimpleCV.HueHistogramFeatureExtractor import *
from SimpleCV.BOFFeatureExtractor import *
from SimpleCV.MorphologyFeatureExtractor import *
import Orange
from SimpleBinaryClassifier import *
from BinarySVMClassifier import *

w = 800
h = 600
display = Display(resolution = (w,h))

edge_extractor = EdgeHistogramFeatureExtractor()
morph_extractor = MorphologyFeatureExtractor()
classifier = BinarySVMClassifier('nut','bolt',[edge_extractor,morph_extractor])
nut_path = "./data/nuts/"
bolt_path = "./data/bolts/"
classifier.train(nut_path,bolt_path,disp=display)
classifier.test(nut_path,bolt_path,disp=display)