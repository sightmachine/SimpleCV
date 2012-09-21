from SimpleCV import Image, Display,Camera,Color,ImageSet
from SimpleCV.base import *
from SimpleCV.Features import * 
from SimpleCV.Features.Features import Feature, FeatureSet
from SimpleCV.Features.PlayingCards.PlayingCard import *
from SimpleCV.MachineLearning import *

count = -1
v = False
def thresholdOp(img):
    return(img.threshold(1))

rpath = "./train/ranks/"
ranks = ['2','3','4','5','69','7','8','0','10','J','Q','K','A']
paths = []
for r in ranks:
    paths.append((rpath+r))
print paths
mfe = MorphologyFeatureExtractor(thresholdOperation=thresholdOp)
feature_extractors = [mfe]
tc_rank = TreeClassifier(feature_extractors)
disp = Display((640,480))
correct,incorrect,confuse = tc_rank.train(paths,ranks,disp,subset=count,verbose=v)
print correct
print incorrect
print confuse
# correct,incorrect,confuse = tc_rank.test(paths,ranks,disp,verbose=v)
# print correct
# print incorrect
# print confuse
tc_rank.save("rank.pkl")

spath = "./train/"
suits = ['c','d','h','s']
for s in suits:
    paths.append((spath+s))
print paths
hhfe = HueHistogramFeatureExtractor(mNBins=6)
mfe = MorphologyFeatureExtractor(thresholdOperation=thresholdOp)
feature_extractors = [hhfe,mfe]
tc_suit = TreeClassifier(feature_extractors)
disp = Display((640,480))
correct,incorrect,confuse = tc_suit.train(paths,suits,disp,subset=count,verbose=v)
print correct
print incorrect
print confuse
# correct,incorrect,confuse = tc_suit.test(paths,ranks,disp,verbose=v)
# print correct
# print incorrect
# print confuse
tc_suit.save("suit.pkl")

rpath = "./train/"
ranks2 = ['A','K','Q','J','T','9','8','7','6','5','4','3','2']
paths = []
for r in ranks2:
    paths.append((rpath+r))
print paths
haarfe = HaarLikeFeatureExtractor("../haar.txt",do45=True)
feature_extractors = [haarfe]
tc_rank2 = TreeClassifier(feature_extractors)
disp = Display((640,480))
correct,incorrect,confuse = tc_rank2.train(paths,ranks2,disp,subset=count,verbose=v)
print correct
print incorrect
print confuse
# correct,incorrect,confuse = tc_rank2.test(paths,ranks2,disp,verbose=v)
# print correct
# print incorrect
# print confuse
tc_rank2.save("rank2.pkl")


