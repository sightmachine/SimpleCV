from SimpleCV import *

print ""
print "This program runs a list of test for machine learning on"
print "the SimpleCV library. Not all scores will be high, this"
print "is just to ensure that the libraries are functioning correctly"
print "on your system"
print ""
print "***** WARNING *****"
print "This program is about to download a large data set to run it's test"


inp = raw_input("Do you want to continue [Y/n]")
if not (inp == "" or inp.lower() == "y"):
    print "Exiting the program"
    sys.exit()


machine_learning_data_set = "https://github.com/downloads/sightmachine/SimpleCV/machine_learning_dataset.zip"
data_path = download_and_extract(machine_learning_data_set)

w = 800
h = 600
n=50

display = Display(resolution = (w,h))

hue = HueHistogramFeatureExtractor(mNBins=16)
edge = EdgeHistogramFeatureExtractor()
bof = BOFFeatureExtractor()
bof.load('../Features/cbdata.txt')
haar = HaarLikeFeatureExtractor(fname="../Features/haar.txt")
morph = MorphologyFeatureExtractor()

spath = data_path + "/data/structured/"
upath = data_path + "/data/unstructured/"
ball_path = spath+"ball/"
basket_path = spath+"basket/"
boat_path = spath+"boat/"
cactus_path = spath +"cactus/"
cup_path = spath+"cup/"
duck_path = spath+"duck/"
gb_path = spath+"greenblock/"
match_path = spath+"matches/"
rb_path = spath+"redblock/"
s1_path = spath+"stuffed/"
s2_path = spath+"stuffed2/"
s3_path = spath+"stuffed3/"

arbor_path = upath+"arborgreens/"
football_path = upath+"football/"
sanjuan_path = upath+"sanjuans/"



print('SVMPoly')
#Set up am SVM with a poly kernel
extractors = [hue]
path = [cactus_path,cup_path,basket_path]
classes = ['cactus','cup','basket']
props ={
        'KernelType':'Poly', #default is a RBF Kernel
        'SVMType':'C',     #default is C
        'nu':None,          # NU for SVM NU
        'c':None,           #C for SVM C - the slack variable
        'degree':3,      #degree for poly kernels - defaults to 3
        'coef':None,        #coef for Poly/Sigmoid defaults to 0
        'gamma':None,       #kernel param for poly/rbf/sigma - default is 1/#samples
    }
print('Train')
classifierSVMP = SVMClassifier(extractors,props)
data = []
for p in path:
    data.append(ImageSet(p))
classifierSVMP.train(data,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierSVMP.test(data,classes,disp=display,subset=n)
files = []
for ext in IMAGE_FORMATS:
    files.extend(glob.glob( os.path.join(path[0], ext)))
for i in range(10):
    img = Image(files[i])
    cname = classifierSVMP.classify(img)
    print(files[i]+' -> '+cname)
classifierSVMP.save('PolySVM.pkl')
print('Reloading from file')
testSVM = SVMClassifier.load('PolySVM.pkl')
#testSVM.setFeatureExtractors(extractors)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = testSVM.classify(img)
    print(files[i]+' -> '+cname)

print('###############################################################################')
print('SVMRBF   ')
# now try an RBF kernel
extractors = [hue,edge]
path = [cactus_path,cup_path,basket_path]
classes = ['cactus','cup','basket']
props ={
        'KernelType':'RBF', #default is a RBF Kernel
        'SVMType':'NU',     #default is C
        'nu':None,          # NU for SVM NU
        'c':None,           #C for SVM C - the slack variable
        'degree':None,      #degree for poly kernels - defaults to 3
        'coef':None,        #coef for Poly/Sigmoid defaults to 0
        'gamma':None,       #kernel param for poly/rbf/sigma
    }
print('Train')
classifierSVMRBF = SVMClassifier(extractors,props)
data = []
for p in path:
    data.append(ImageSet(p))

classifierSVMRBF.train(data,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierSVMRBF.test(data,classes,disp=display,subset=n)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = classifierSVMRBF.classify(img)
    print(files[i]+' -> '+cname)
classifierSVMRBF.save('RBFSVM.pkl')
print('Reloading from file')
testSVMRBF = SVMClassifier.load('RBFSVM.pkl')
#testSVMRBF.setFeatureExtractors(extractors)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = testSVMRBF.classify(img)
    print(files[i]+' -> '+cname)


print('###############################################################################')
print('Bayes')
extractors = [haar]
classifierBayes = NaiveBayesClassifier(extractors)#
print('Train')
path = [arbor_path,football_path,sanjuan_path]
classes = ['arbor','football','sanjuan']
classifierBayes.train(path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierBayes.test(path,classes,disp=display,subset=n)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = classifierBayes.classify(img)
    print(files[i]+' -> '+cname)
classifierBayes.save('Bayes.pkl')
print('Reloading from file')
testBayes = NaiveBayesClassifier.load('Bayes.pkl')
testBayes.setFeatureExtractors(extractors)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = testBayes.classify(img)
    print(files[i]+' -> '+cname)

print('###############################################################################')


print('###############################################################################')
print('Forest')
extractors = [morph]
classifierForest = TreeClassifier(extractors,flavor='Forest')#
print('Train')
path = [s1_path,s2_path,s3_path]
classes = ['s1','s2','s3']
classifierForest.train(path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierForest.test(path,classes,disp=display,subset=n)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = classifierForest.classify(img)
    print(files[i]+' -> '+cname)

classifierForest.save('forest.pkl')
print('Reloading from file')
testForest = TreeClassifier.load('forest.pkl')
testForest.setFeatureExtractors(extractors)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = testForest.classify(img)
    print(files[i]+' -> '+cname)

print('###############################################################################')
print('Bagged Tree')
extractors = [haar]
classifierBagTree = TreeClassifier(extractors,flavor='Bagged')#
print('Train')
path = [s1_path,s2_path,s3_path]
classes = ['s1','s2','s3']
classifierBagTree.train(path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierBagTree.test(path,classes,disp=display,subset=n)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = classifierBagTree.classify(img)
    print(files[i]+' -> '+cname)

classifierBagTree.save('bagtree.pkl')
print('Reloading from file')
testBagTree = TreeClassifier.load('bagtree.pkl')
testBagTree.setFeatureExtractors(extractors)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = testBagTree.classify(img)
    print(files[i]+' -> '+cname)



print('###############################################################################')
print('Vanilla Tree')
extractors = [haar]
classifierTree = TreeClassifier(featureExtractors=extractors)
print('Train')
path = [s1_path,s2_path,s3_path]
classes = ['s1','s2','s3']
classifierTree.train(path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierTree.test(path,classes,disp=display,subset=n)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = classifierTree.classify(img)
    print(files[i]+' -> '+cname)
print('Reloading from file')
classifierTree.save('tree.pkl')
testTree = TreeClassifier.load('tree.pkl')
testTree.setFeatureExtractors(extractors)
for i in range(10):
    img = Image(files[i])
    cname = testTree.classify(img)
    print(files[i]+' -> '+cname)

print('###############################################################################')
print('Boosted Tree')
extractors = [haar]
classifierBTree = TreeClassifier(extractors,flavor='Boosted')#
print('Train')
path = [s1_path,s2_path,s3_path]
classes = ['s1','s2','s3']
classifierBTree.train(path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierBTree.test(path,classes,disp=display,subset=n)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = classifierBTree.classify(img)
    print(files[i]+' -> '+cname)

classifierBTree.save('btree.pkl')
print('Reloading from file')

testBoostTree = TreeClassifier.load('btree.pkl')
testBoostTree.setFeatureExtractors(extractors)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = testBoostTree.classify(img)
    print(files[i]+' -> '+cname)




print('###############################################################################')
print('KNN')
extractors = [hue,edge]
classifierKNN = KNNClassifier(extractors)#
print('Train')
path = [s1_path,s2_path,s3_path]
classes = ['s1','s2','s3']
classifierKNN.train(path,classes,disp=display,subset=n) #train
print('Test')
[pos,neg,confuse] = classifierKNN.test(path,classes,disp=display,subset=n)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = classifierKNN.classify(img)
    print(files[i]+' -> '+cname)

classifierKNN.save('knn.pkl')
print('Reloading from file')
testKNN = KNNClassifier.load('knn.pkl')
testKNN.setFeatureExtractors(extractors)
files = glob.glob( os.path.join(path[0], '*.jpg'))
for i in range(10):
    img = Image(files[i])
    cname = testKNN.classify(img)
    print(files[i]+' -> '+cname)


print ""
print "All the machine learning test have ran correctly"
