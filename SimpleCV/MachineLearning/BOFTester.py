from SimpleCV import *
from numpy import *
from SimpleCV.Features import BOFFeatureExtractor
import os
import glob
import time
cat_path = "./data/cat/truth/"
cheeseburger_path = "./data/cheeseburger/truth/"
paths = [cat_path,cheeseburger_path]
bof = BOFFeatureExtractor()
#bof.load('cbdata.txt')
bof.generate(paths,imgs_per_dir=200,numcodes=256,sz=(11,11),img_layout=(16,16),padding=4 )
bof.save("codebook.png","cbdata.txt")
#count = 0
#test = bof.reconstruct(Image("codebook.png"))
#test.save("anticodebook.jpg")
#for infile in glob.glob( os.path.join(cat_path, '*.jpg') ):
#    print "opening file: " + infile
#    img = Image(infile)
#    oimg = bof.reconstruct(img)
#    fname = infile[0:-4]+"_reconstruction.png"
#    oimg.save(fname)
