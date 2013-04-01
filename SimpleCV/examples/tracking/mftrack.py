from SimpleCV import *
# Example for Media Flow Tracker.
def foo(image):
    return image.meanColor()

def mftest():
    cam = Camera()
    img = cam.getImage()
    d = Display(img.size())
    bb1 = getBBFromUser(cam,d)
    fs1=[]
    img = cam.getImage()
    while True:
        try:
            img1 = cam.getImage()
            fs1 = img1.track("mftrack",fs1,img,bb1, numM=10, numN=10, winsize=10)
            print fs1[-1].shift, "shift"
            fs1.drawBB(color=(255,0,0))
            fs1.drawPath()
            img1.show()
        except KeyboardInterrupt:
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
    print p1,p2
    if not p1 or not p2:
        return None

    xmax = np.max((p1[0],p2[0]))
    xmin = np.min((p1[0],p2[0]))
    ymax = np.max((p1[1],p2[1]))
    ymin = np.min((p1[1],p2[1]))
    print xmin,ymin,xmax,ymax
    return (xmin,ymin,xmax-xmin,ymax-ymin)

mftest()
