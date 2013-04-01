"""
Example of Lucas Kanade Tracker
"""

from SimpleCV import *

def lktest():
    cam = Camera()
    img = cam.getImage()
    d = Display(img.size())
    img, bb1 = getBBFromUser(cam,d)
    fs1=[]
    while True:
        try:
            img1 = cam.getImage()
            fs1 = img1.track("lk",fs1,img,bb1, maxCorners = 5000, qualityLevel = 0.08, winSize = (15, 15))
            fs1.drawBB(color=Color.RED)
            print fs1[-1].getBB()
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
    if not p1 or not p2:
        return None

    xmax = np.max((p1[0],p2[0]))
    xmin = np.min((p1[0],p2[0]))
    ymax = np.max((p1[1],p2[1]))
    ymin = np.min((p1[1],p2[1]))
    return (img,(xmin,ymin,xmax-xmin,ymax-ymin))

lktest()
