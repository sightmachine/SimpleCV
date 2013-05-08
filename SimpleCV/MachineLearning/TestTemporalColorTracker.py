from SimpleCV import Camera, Image, Color, TemporalColorTracker, ROI, Display
import matplotlib.pyplot as plt

cam = Camera(1)
tct = TemporalColorTracker()
img = cam.getImage()
roi = ROI(img.width*0.45,img.height*0.45,img.width*0.1,img.height*0.1,img)
tct.train(cam,roi=roi,maxFrames=250,pkWndw=20)

# Matplot Lib example plotting
plotc = {'r':'r','g':'g','b':'b','i':'m','h':'y'}
for key in tct.data.keys():
    plt.plot(tct.data[key],plotc[key])
    for pt in tct.peaks[key]:
        plt.plot(pt[0],pt[1],'r*')
    for pt in tct.valleys[key]:
        plt.plot(pt[0],pt[1],'b*')
    plt.grid()
plt.show()

disp = Display((800,600))
while disp.isNotDone():
    img = cam.getImage()
    result = tct.recognize(img)
    plt.plot(tct._rtData,'r-')
    plt.grid()
    plt.savefig('temp.png')
    plt.clf()
    plotImg = Image('temp.png')    
    
    roi = ROI(img.width*0.45,img.height*0.45,img.width*0.1,img.height*0.1,img)
    roi.draw(width=3)
    img.drawText(str(result),20,20,color=Color.RED,fontsize=32)
    img = img.applyLayers()
    img = img.blit(plotImg.resize(w=img.width,h=img.height),pos=(0,0),alpha=0.5)
    img.save(disp)
