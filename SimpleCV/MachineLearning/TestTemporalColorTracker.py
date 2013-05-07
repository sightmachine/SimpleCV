from SimpleCV import Image, ROI, VirtualCamera, TemporalColorTracker, Color, Display, VideoStream, Camera
import matplotlib.pyplot as plt
import pickle
from subprocess import call # to run command line programs
outTemp = 'test.avi'
outname = 'output.mp4'
tags = 'SimpleCV, Computer Vision, Python'
title = "SimpleCV Output"
summary = "See http://simplecv.org for more info."
access = "private" # Options are "public" "private" "protected"

# def testFunc(img):
#     w = img.width
#     h = img.height
#     x1 = int(w*0.5)
#     x2 = int(w*0.5)
#     y1 = int(h*0.45)
#     y2 = int(h*0.55)
#     lsb = img.getLineScan(pt1=(x1,y1),pt2=(x2,y2),cnhannel=0)
#     lsg = img.getLineScan(pt1=(x1,y1),pt2=(x2,y2),channel=1)
#     lsr = img.getLineScan(pt1=(x1,y1),pt2=(x2,y2),channel=2)
#     return [lsr.mean(),lsg.mean(),lsb.mean()]
        
fname = 'bottles.flv' #vials0.MP4'
cam = VirtualCamera(s=fname,st='video')
img = cam.getImage()
w = img.width
h = img.height
data = []
roi = ROI(w*0.25,h*0.3,w*0.05,h*0.1,img)
disp = Display((1024,768))
    
tct = TemporalColorTracker()
tct.train(cam,roi=roi,maxFrames=5000,pkWndw=10,ssWndw=0.1,doCorr=True,forceChannel='g')
plotc = {'r':'r','g':'g','b':'b','i':'m','h':'y'}
l = len(tct.data['r'])
pickle.dump(tct,open('tct.pkl','wb'))
for key in tct.data.keys():
    plt.plot(tct.data[key],plotc[key])
    mu,s = tct._steadyState[key]
    plt.plot([0,l],[mu+3*s,mu+3*s],plotc[key]+'--')
    plt.plot([0,l],[mu-3*s,mu-3*s],plotc[key]+'--')
    for pt in tct.peaks[key]:
        plt.plot(pt[0],pt[1],'r*')
    for pt in tct.valleys[key]:
        plt.plot(pt[0],pt[1],'b*')
    plt.grid()
plt.show()

for sig in tct.corrTemplates:
    plt.plot(sig,'b--')
plt.plot(tct._template, 'r-')
plt.grid()
plt.show()

#cam = None
cam = VirtualCamera(s=fname,st='video')
vs = VideoStream(fps=30,filename=outTemp,framefill=False)
count = 0
frame = 0
show = True
disp.done = False
while disp.isNotDone():
    img = cam.getImage()
    if( img is None ):
        if( count < 1000 ):
            cam.rewind()
        else:
            break
    else:
        roi = ROI(w*0.25,h*0.3,w*0.05,h*0.1,img)
        result = tct.recognize(img)
        if( result ):
            count = count + 1

        if( show ):
            myStr = "{0}".format(count)
            frame = frame + 1
            img.drawText(myStr,100,30,color=Color.RED,fontsize=90)
            roi.draw(width=2)
            img = img.applyLayers()
            img.save(disp)
            vs.writeFrame(img)
# construct the encoding arguments
params = " -i {0} {1}".format(outTemp,outname)
# run ffmpeg to compress your video.
call('ffmpeg'+params,shell=True)
# construct the command line arguments for google command line
params = "{0} --title \"{1}\" --tags \"{2}\" --category \"Education\" --summary \"{3}\" --access \"{4}\" ".format(outname,title,tags,summary,access)
print params
# call the command line
#call('google youtube post '+params,shell=True)
