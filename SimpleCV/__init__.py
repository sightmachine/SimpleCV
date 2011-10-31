__version__ = '1.1.0'

from SimpleCV.base import *
from SimpleCV.Camera import *
from SimpleCV.Color import *
from SimpleCV.Detection import *   
from SimpleCV.Features import *
from SimpleCV.ImageClass import *
from SimpleCV.Stream import *
from SimpleCV.Font import *
from SimpleCV.ColorModel import *
from SimpleCV.DrawingLayer import *
from SimpleCV.BlobMaker import *
from SimpleCV.Segmentation.SegmentationBase import *
#from SimpleCV.Segmentation.ColorSegmentation import *
#from SimpleCV.Segmentation.DiffSegmentation import *
#from SimpleCV.Segmentation.RunningSegmentation import *
#from SimpleCV.analysis.BOFFeatureExtractor import *
#from SimpleCV.analysis.CodebookSegmentation import *
#from SimpleCV.analysis.FeatureExtractorBase import *
#from SimpleCV.analysis.HueHistogramFeatureExtractor import *
#from SimpleCV.analysis.EdgeHistogramFeatureExtractor import *
#from SimpleCV.analysis.HaarLikeFeatureExtractor import *
#from SimpleCV.analysis.HaarLikeFeature import *
#from SimpleCV.ml.BinarySVMClassifier import *
#from SimpleCV.ml.TreeClassifier import *
#from SimpleCV.ml.KNNClassifier import *
#from SimpleCV.ml.NaiveBayesClassifier import *

if (__name__ == '__main__'):
    from SimpleCV.Shell import *
    main()
