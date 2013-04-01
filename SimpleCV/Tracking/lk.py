import cv2
import numpy as np
import itertools

def lk(img, bb, ts, oldimg, **kwargs):
    maxCorners = 4000
    qualityLevel = 0.6
    minDistance = 2
    blockSize = 3
    winSize = (10, 10)
    maxLevel = 10
    for key in kwargs:
        if key == 'maxCorners':
            maxCorners = kwargs[key]
        elif key == 'quality':
            qualityLevel = kwargs[key]
        elif key == 'minDistance':
            minDistance = kwargs[key]
        elif key == 'blockSize':
            blockSize = kwargs[key]
        elif key == 'winSize':
            winSize = kwargs[key]
        elif key == maxLevel:
            maxLevel = kwargs[key]

    bb = (int(bb[0]), int(bb[1]), int(bb[2]), int(bb[3]))
    img1 = img.crop(bb[0],bb[1],bb[2],bb[3])
    g = img1.getGrayNumpyCv2()
    pt = cv2.goodFeaturesToTrack(g, maxCorners = maxCorners, qualityLevel = qualityLevel,
                                minDistance = minDistance, blockSize = blockSize)
    if type(pt) == type(None):
        print "no points"
        track = LK(img, bb, pt)
        return track

    for i in xrange(len(pt)):
        pt[i][0][0] = pt[i][0][0]+bb[0]
        pt[i][0][1] = pt[i][0][1]+bb[1]

    p0 = np.float32(pt).reshape(-1, 1, 2)
    oldg = oldimg.getGrayNumpyCv2()
    newg = img.getGrayNumpyCv2()
    p1, st, err = cv2.calcOpticalFlowPyrLK(oldg, newg, p0, None, winSize  = winSize,
                                           maxLevel = maxLevel,
                                           criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    p0r, st, err = cv2.calcOpticalFlowPyrLK(newg, oldg, p1, None, winSize  = winSize,
                                            maxLevel = maxLevel,
                                            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    d = abs(p0-p0r).reshape(-1, 2).max(-1)
    good = d < 1
    new_pts=[]
    for pts, val in itertools.izip(p1, good):
        if val:
            new_pts.append([pts[0][0], pts[0][1]])
    if ts[-1:]:
        old_pts = ts[-1].pts
        if type(old_pts) == type(None):
            old_pts = new_pts
    else:
        old_pts = new_pts
    dx=[]
    dy=[]
    for p1, p2 in itertools.izip(old_pts, new_pts):
        dx.append(p2[0]-p1[0])
        dy.append(p2[1]-p1[1])

    if not dx or not dy:
        track = LK(img, bb, new_pts)
        return track

    cen_dx = round(sum(dx)/len(dx))/3
    cen_dy = round(sum(dy)/len(dy))/3

    bb1 = [bb[0]+cen_dx, bb[1]+cen_dy, bb[2], bb[3]]
    if bb1[0] <= 0:
        bb1[0] = 1
    if bb1[0]+bb1[2] >= img.width:
        bb1[0] = img.width - bb1[2] - 1
    if bb1[1]+bb1[3] >= img.height:
        bb1[1] = img.height - bb1[3] - 1
    if bb1[1] <= 0:
        bb1[1] = 1

    track = LK(img, bb1, new_pts)    
    return track

from SimpleCV.Features import LK
