from SimpleCV import Image, ROI, VirtualCamera, TemporalColorTracker, Color, Display
import matplotlib.pyplot as plt
import pickle

cam = VirtualCamera(s='fakedata.avi',st='video')
img = cam.getImage()
w = img.width
h = img.height
disp = Display((1024,768))
data = []
roi = ROI(w*0.45,h*0.45,w*0.1,h*0.1,img)
tct = TemporalColorTracker()
tct.train(cam, roi,maxFrames=1000)
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
        plt.plot(pt[0],pt[1],'r.')
    plt.grid()
plt.show()

