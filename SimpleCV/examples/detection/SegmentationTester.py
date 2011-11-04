import time
from SimpleCV import *

def runSegmentor(segmentor,nframes,display):
    count = 0
    while(count < nframes):
        segmentor.addImage(cam.getImage())
        if(segmentor.isReady()):
            count = count + 1
            img = segmentor.getSegmentedImage()
            img.save(display)
            fs = segmentor.getSegmentedBlobs()

w = 800
h = 600
nframes = 25
display = Display(resolution = (w,h)) #create a new display to draw images on
cam = Camera(1)

count = 0
while( count < nframes ):
    img = cam.getImage()
    img.save(display)
    count = count + 1
    
segmentor = DiffSegmentation()
print('Running diff segmentation.')
runSegmentor(segmentor,nframes,display )
sname = 'diffsegmentation.pkl'
segmentor.save(sname)
segmentor = None
segmentor = DiffSegmentation().load(sname)
print('Running diff segmentation from file.')
runSegmentor(segmentor,nframes,display )
segmentor = None

segmentor = RunningSegmentation()
print('Running segmentation.')
runSegmentor(segmentor,nframes,display )
sname = 'runsegmentation.pkl'
segmentor.save(sname)
segmentor = None
segmentor = RunningSegmentation().load(sname)
print('Running  segmentation from file.')
runSegmentor(segmentor,nframes,display )
segmentor = None

segmentor = ColorSegmentation()
img = cam.getImage();
segmentor.addToModel(img)
print('Color segmentation.')
runSegmentor(segmentor,nframes,display )
sname = 'colorsegmentation.pkl'
segmentor.save(sname)
segmentor = None
segmentor = ColorSegmentation().load(sname)
print('Color  segmentation from file.')
runSegmentor(segmentor,nframes,display )
segmentor = None
