'''
This Example uses scikits-learn to do a binary classfication of images
of nuts vs. bolts.  Only the area, height, and width are used to classify
the actual images but data is extracted from the images using blobs.

This is a very crude example and could easily be built upon, but is just
meant to give an introductory example for using machine learning

The data set should auto download, if not you can get it from:
https://github.com/downloads/sightmachine/SimpleCV/nuts_bolts.zip
'''
print __doc__
from SimpleCV import *
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
import numpy as np

#Download the dataset
machine_learning_data_set = 'https://github.com/downloads/sightmachine/SimpleCV/nuts_bolts.zip'
data_path = download_and_extract(machine_learning_data_set)
print 'Test Images Downloaded at:', data_path

display = Display((800,600)) #Display to show the images
target_names = ['bolt', 'nut']

print 'Loading Bolts for Training'
bolts = ImageSet(data_path + '/data/supervised/bolts') #Load Bolts for training
bolt_blobs = [b.findBlobs()[0] for b in bolts] #exact the blobs for our features
tmp_data = [] #array to store data features
tmp_target = [] #array to store targets

for b in bolt_blobs: #Format Data for SVM
    tmp_data.append([b.area(), b.height(), b.width()])
    tmp_target.append(0)

print 'Loading Nuts for Training'
nuts = ImageSet(data_path + '/data/supervised/nuts')
nut_blobs = [n.invert().findBlobs()[0] for n in nuts]
for n in nut_blobs:
    tmp_data.append([n.area(), n.height(), n.width()])
    tmp_target.append(1)

dataset = np.array(tmp_data)
targets = np.array(tmp_target)

print 'Training Machine Learning'
clf = LinearSVC()
clf = clf.fit(dataset, targets)
clf2 = LogisticRegression().fit(dataset, targets)

print 'Running prediction on bolts now'
untrained_bolts = ImageSet(data_path + '/data/unsupervised/bolts')
unbolt_blobs = [b.findBlobs()[0] for b in untrained_bolts]
for b in unbolt_blobs:
    ary = [b.area(), b.height(), b.width()]
    name = target_names[clf.predict(ary)[0]]
    probability = clf2.predict_proba(ary)[0]
    img = b.image
    img.drawText(name)
    img.save(display)
    print "Predicted:",name,", Guess:",probability[0], target_names[0],",", probability[1], target_names[1]

print 'Running prediction on nuts now'
untrained_nuts = ImageSet(data_path + '/data/unsupervised/nuts')
unnut_blobs = [n.invert().findBlobs()[0] for n in untrained_nuts]
for n in unnut_blobs:
    ary = [n.area(), n.height(), n.width()]
    name = target_names[clf.predict(ary)[0]]
    probability = clf2.predict_proba(ary)[0]
    img = n.image
    img.drawText(name)
    img.save(display)
    print "Predicted:",name,", Guess:",probability[0], target_names[0],",", probability[1], target_names[1]
