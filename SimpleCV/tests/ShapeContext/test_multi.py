from SimpleCV import *

color = Color()


iset = ImageSet("./dataset/model/")
iset = iset[0:3]
testset = ImageSet("./dataset/test/")
testset = testset[0:3]
names = []
for i in iset:
    names.append(i.filename)

print names
names = names[0:3]

scc = ShapeContextClassifier(iset,names)

classifications = []
for test in testset:
    print "--------------------------"
    print "testing " + test.filename
    best, result = scc.classify(test)
    print "srcimg       : value "
    for k,v in result.items():
        print k+": "+str(v)
    print "Best Result: " + best 
    classifications.append(result)
    print result
