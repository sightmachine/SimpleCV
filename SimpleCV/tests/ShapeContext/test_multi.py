from SimpleCV import *
import string
color = Color()

subset = 5
iset = ImageSet()
iset.load("./dataset/model/",sort_by="name")
iset = iset[0:subset]
testset = ImageSet()
testset.load("./dataset/test/",sort_by="name")
testset = testset[0:subset]
names = []
for i in iset:
    names.append(i.filename)

print names
names = names[0:subset]

scc = ShapeContextClassifier(iset,names)

print "--------------------------"
print "--------------------------"
print "Performing Analysis!"
print "--------------------------"
print "--------------------------"
classifications = []

i = 0
for test in testset:
    best, value, result = scc.classify(test)
    print "--------------------------"
    print "testing " + test.filename
    #print "srcimg                        : value "
    #for k,v in result.items():
    #    print k+": "+str(v)
    #print "--------------------------"
    print "Best Result: " + best
    words = string.split(best,'/')
    words2 = string.split(test.filename,'/')
    matchImg = test.sideBySide(scc.imgMap[best])
    matchImg = matchImg.resize(w=800)
    label = "Matched " + words[-1] + " with " + words[-1]
    matchImg.drawText(label,10,10,color=Color.RED,fontsize=30)
    label = "MatchVal: " + str(np.around(value,4))
    matchImg.drawText(label,10,45,color=Color.RED,fontsize=30)

    matchImg.show()
    fname = "match"+str(i)+".png"
    i = i + 1 
    matchImg.save(fname)
    classifications.append(result)
    print result
