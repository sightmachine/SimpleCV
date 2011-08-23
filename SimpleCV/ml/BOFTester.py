from SimpleCV import *
from numpy import *
from SimpleCV.Display import Display, pg
from SimpleCV.BOFFeatureExtractor import *
cat_path = "./data/cat/truth/"
cheeseburger_path = "./data/cheeseburger/truth/"
paths = [cat_path,cheeseburger_path]
bof = BOFFeatureExtractor()
bof.generate(paths,imgs_per_dir=50)
