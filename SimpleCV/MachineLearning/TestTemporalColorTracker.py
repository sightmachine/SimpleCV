from SimpleCV import Image, ROI, VirtualCamera, TemporalColorTracker, Color, Display
import matplotlib.pyplot as plt
import pickle

cam = VirtualCamera(s='fakedata.avi',st='video')
img = cam.getImage()
w = img.width
h = img.height
data = []
roi = ROI(w*0.45,h*0.45,w*0.1,h*0.1,img)
tct = TemporalColorTracker()
tct.train(cam, roi,maxFrames=1200)
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
cam = None
cam = VirtualCamera(s='fakedata.avi',st='video')
disp = Display((1024,768))
count = 0
while disp.isNotDone():
    img = cam.getImage()
    result = tct.recognize(img)
    if( result ):
        count = count + 1
        img = img.invert()
    myStr = "Count: {0}".format(count)
    plt.plot(tct._rtData,'m-')
    plt.grid()
    plt.ylim([0,255])
    plt.savefig('temp.png')
    plotImg = Image('temp.png')
    plt.clf()
    plotImg = plotImg.scale(0.5)
    img = img.blit(plotImg,pos=(0,img.height-plotImg.height))
    img.drawText(myStr,30,30,color=Color.RED,fontsize=64)
    img = img.applyLayers()
    img.save(disp)
