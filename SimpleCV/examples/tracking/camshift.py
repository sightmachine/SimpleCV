from SimpleCV import *

def foo(image):
    return image.meanColor()

def camshift():
    cam = Camera()
    img = cam.getImage()
    d = Display(img.size())
    bb1 = getBBFromUser(cam,d)
    fs1=[]
    while True:
        try:
            img1 = cam.getImage()
            fs1 = img1.track("camshift",fs1,img,bb1,num_frames=5)
            fs1.drawBB()
            fs1.drawPath()
            fs1.showCoordinates()
            fs1.showSizeRatio()
            fs1.showPixelVelocity()
            fs1.showPixelVelocityRT()
            img1.show()
        except KeyboardInterrupt:
            print "Total number of frames tracked",
            print fs1.trackLength()
            print fs1.processTrack(foo)
            break

def getBBFromUser(cam, d):
    p1 = None
    p2 = None
    img = cam.getImage()
    while d.isNotDone():
        try:
            img = cam.getImage()
            img.save(d)
            dwn = d.leftButtonDownPosition()
            up = d.leftButtonUpPosition()
            
            if dwn:
                p1 = dwn
            if up:
                p2 = up
                break

            time.sleep(0.05)
        except KeyboardInterrupt:
            break
    if not p1 or not p2:
        return None
    
    xmax = np.max((p1[0],p2[0]))
    xmin = np.min((p1[0],p2[0]))
    ymax = np.max((p1[1],p2[1]))
    ymin = np.min((p1[1],p2[1]))
    return (xmin,ymin,xmax-xmin,ymax-ymin)
    
camshift()
