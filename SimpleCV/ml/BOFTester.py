from SimpleCV import *
from numpy import *
from SimpleCV.Display import Display, pg
from SimpleCV.BOFFeatureExtractor import *
import os
import glob
import time
cat_path = "./data/cat/truth/"
cheeseburger_path = "./data/cheeseburger/truth/"
paths = [cat_path,cheeseburger_path]
bof = BOFFeatureExtractor()
bof.load('cbdata.txt')
bof.generate(paths,imgs_per_dir=3)
bof.save("codebook.png","cbdata.txt")
#for infile in glob.glob( os.path.join(cat_path, '*.jpg') ):
#    print "opening file: " + infile
#    img = Image(infile)
#    hist = bof.extract(img)
