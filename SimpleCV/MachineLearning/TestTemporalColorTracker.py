from SimpleCV import Image, ROI, VirtualCamera, TemporalColorTracker, Color, Display, VideoStream, Camera
import matplotlib.pyplot as plt
import pickle

def testFunc(img):
    w = img.width
    h = img.height
    x1 = int(w*0.5)
    x2 = int(w*0.5)
    y1 = int(h*0.45)
    y2 = int(h*0.55)
    lsb = img.getLineScan(pt1=(x1,y1),pt2=(x2,y2),channel=0)
    lsg = img.getLineScan(pt1=(x1,y1),pt2=(x2,y2),channel=1)
    lsr = img.getLineScan(pt1=(x1,y1),pt2=(x2,y2),channel=2)
    return [lsr.mean(),lsg.mean(),lsb.mean()]
        
fname = 'vials0.MP4'
cam = VirtualCamera(s=fname,st='video')
img = cam.getImage()
w = img.width
h = img.height
data = []
#roi = ROI(w*0.45,h*0.45,w*0.1,h*0.1,img)
roi = ROI(w*0.45,h*0.45,w*0.05,h*0.1,img)
disp = Display((1024,768))
# buffer the camera
#while disp.isNotDone():
#    cam.getImage().save(disp)
    
tct = TemporalColorTracker()
tct.train(cam,extractor=testFunc,maxFrames=5000,pkWndw=5,ssWndw=0.01)
plotc = {'r':'r','g':'g','b':'b','i':'m','h':'y'}
l = len(tct.data['r'])
pickle.dump(tct,open('tct.pkl','wb'))
print l
print tct.steadyState
for key in tct.data.keys():
    plt.plot(tct.data[key],plotc[key])
    mu,s = tct.steadyState[key]
    plt.plot([0,l],[mu+3*s,mu+3*s],plotc[key]+'--')
    plt.plot([0,l],[mu-3*s,mu-3*s],plotc[key]+'--')
    for pt in tct.peaks[key]:
        plt.plot(pt[0],pt[1],'r*')
    for pt in tct.valleys[key]:
        plt.plot(pt[0],pt[1],'b*')

    plt.grid()
plt.show()
#cam = None
cam = VirtualCamera(s=fname,st='video')
vs = VideoStream(fps=60,filename="test.avi",framefill=False)
count = 0
frame = 0
show = True
disp.done = False
while disp.isNotDone():
    img = cam.getImage()
    if( img is None ):
        break
    roi = ROI(w*0.45,h*0.45,w*0.05,h*0.1,img)
    result = tct.recognize(img)
    if( result ):
        count = count + 1
        print count

    if( show ):
        myStr = "Count: {0} Frame: {1}".format(count,frame)
        frame = frame + 1
        # plt.plot(tct._rtData,'m-')
        # plt.grid()
        # plt.ylim([0,255])
        # plt.savefig('temp.png')
        # plotImg = Image('temp.png')
        # plt.clf()
        # plotImg = plotImg.scale(0.5)
        # img = img.blit(plotImg,pos=(0,img.height-plotImg.height))
        img.drawText(myStr,30,30,color=Color.RED,fontsize=64)
        roi.draw(width=5)
        img = img.applyLayers()
        img.save(disp)
        vs.writeFrame(img)
