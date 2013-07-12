from SimpleCV import Image, Features, Color, ImageSet, Display
from SimpleCV.MachineLearning import TurkingModule
# This example shows how to use the turking module.
# by turking we mean manually sorting and classifying images
# ostensibly for supervised learning

# return images of all the big blobs in our source images
def preprocess(img):
    blobs = img.findBlobs(minsize=200)
    blobs = blobs.sortArea()
    return [b.mImg for b in blobs]

# once we are done invert them
def postprocess(img):
    return img.invert()

# we are going to turk two things junk and stuff
classes = ['junk','stuff']
# press j for junk and s for stuff
key_bind = ['j','s']
# put stuff right here
outdir = './'
# use the sample images directory for our sources
input = ['../sampleimages/']

# set everything up
turker = TurkingModule(input,outdir,classes,key_bind,preprocess,postprocess)

# run the turking, the display window must have focus
turker.turk(font_size=16, color = Color.BLUE, spacing=18)

# show what we got
print "="*30
print "TURKING DONE!"
for c in classes:
    print "="*30
    print "Showing " + c
    iset = turker.getClass(c)
    iset.show(0.1)

# save the results
turker.save('junkAndStuff.pkl')
