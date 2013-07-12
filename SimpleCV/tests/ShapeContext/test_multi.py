from SimpleCV import *
import string
import pickle
color = Color()

subset = 5
iset = ImageSet()
iset.load("./dataset/model/",sort_by="name")
iset = iset[0:subset]
testset = ImageSet()
testset.load("./dataset/test/",sort_by="name")
testset = testset[0:subset]
# fix featureset standardize to include fname
#iset = iset.standardize(400,400) # this should deal with some of the point issues
#testset = testset.standardize(400,400)
names = []
for i in iset:
    names.append(i.filename)

print names
names = names[0:subset]

scc = None
fname = 'classifier.pkl'
load_from_file = False
if( load_from_file ):
    scc = pickle.load( open( fname, "rb" ) )
else:
    scc = ShapeContextClassifier(iset,names) #this needs to be pickled.
    pickle.dump(scc, open( fname, "wb" ) )

print "--------------------------"
print "--------------------------"
print "Performing Analysis!"
print "--------------------------"
print "--------------------------"
classifications = []

i = 0
for test in testset:
    print "--------------------------"
    best, value, result = scc.classify(test)
    print "Total points in result " + str(len(scc.ptMap[best]))
    print "Testing: " + test.filename
    print "Best Result: " + best
    words = string.split(best,'/')
    words2 = string.split(test.filename,'/')
    test = test.resize(h=400)
    true_match = iset[i].resize(h=400)
    # test image, actual match, truth match
    test2 = scc.imgMap[best].resize(h=400)
    matchImg = test.sideBySide(test2)
    matchImg = matchImg.sideBySide(true_match)
    matchImg = matchImg.resize(w=1200)
    label = "Matched " + words2[-1] + " with " +  words[-1]
    matchImg.drawText(label,10,10,color=Color.RED,fontsize=30)
    label = "MatchVal: " + str(np.around(value,4))
    matchImg.drawText(label,10,45,color=Color.RED,fontsize=30)
    matchImg.show()
    fname = "match"+str(i)+".png"
    i = i + 1
    matchImg.save(fname)
    classifications.append((test.filename,result))
    print result
pickle.dump(classifications, open( "classifications.pkl", "wb" ) )
