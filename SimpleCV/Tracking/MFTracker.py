from copy import copy
import numpy as np
import cv2
import cv2.cv as cv
import math
import time
import numpy as np
import scipy.spatial.distance as spsd

def MFTrack(img, bb, ts, oldimg, **kwargs):
    numM = 10
    numN = 10
    margin = 5
    winsize_ncc = 10
    oldg = oldimg.getGrayNumpyCv2()
    newg = img.getGrayNumpyCv2()
    bb = [bb[0], bb[1], bb[0]+bb[3], bb[1]+bb[3]]
    bb, shift = fbtrack(oldg, newg, bb, numM, numN, margin, winsize_ncc)
    bb = [bb[0], bb[1], bb[2]-bb[0], bb[3]-bb[1]]
    track = MFTracker(img, bb, shift)
    return track

def fbtrack(imgI, imgJ, bb, numM=10, numN=10,margin=5,winsize_ncc=10):

    nPoints = numM*numN
    sizePointsArray = nPoints*2
    #print bb, "passed in fbtrack"
    pt = getFilledBBPoints(bb, numM, numN, margin)
    fb, ncc, status, ptTracked = lktrack(imgI, imgJ, pt, nPoints, winsize_ncc)

    nlkPoints = sum(status)[0]
    
    startPoints = []
    targetPoints = []
    fbLKCleaned = [0.0]*nlkPoints
    nccLKCleaned = [0.0]*nlkPoints
    M = 2
    nRealPoints = 0
    
    for i in range(nPoints):
        if ptTracked[M*i] is not -1:
            startPoints.append((pt[2 * i],pt[2*i+1]))
            targetPoints.append((ptTracked[2 * i], ptTracked[2 * i + 1]))
            fbLKCleaned[nRealPoints]=fb[i]
            nccLKCleaned[nRealPoints]=ncc[i]
            nRealPoints+=1
            
    medFb = getMedian(fbLKCleaned)
    medNcc = getMedian(nccLKCleaned)
    
    nAfterFbUsage = 0
    for i in range(nlkPoints):
        if fbLKCleaned[i] <= medFb and nccLKCleaned[i] >= medNcc:
            startPoints[nAfterFbUsage] = startPoints[i]
            targetPoints[nAfterFbUsage] = targetPoints[i]
            nAfterFbUsage+=1

    newBB, scaleshift = predictBB(bb, startPoints, targetPoints, nAfterFbUsage)
    #print newBB, "fbtrack passing newBB"
    return (newBB, scaleshift)

def getMedianUnmanaged(a):
    if not a:
        return None
    newl = copy(a)
    newl.sort()
    while True:
        try:
            newl.remove(0)
        except ValueError:
            if newl:
                return newl[len(newl)/2]
            return 0

def getMedian(a):
    median = getMedianUnmanaged(a)
    return median

def calculateBBCenter(bb):
    center = (0.5*(bb[0] + bb[2]),0.5*(bb[1]+bb[3]))
    return center
    
def getFilledBBPoints(bb, numM, numN, margin):
    pointDim = 2
    bb_local = (bb[0] + margin, bb[1] + margin, bb[2] - margin, bb[3] - margin)
    if numM == 1 and numN == 1 :
        pts = calculateBBCenter(bb_local)
        return pts
    
    elif numM > 1 and numN == 1:
        divM = numM - 1
        divN = 2
        spaceM = (bb_local[3]-bb_local[1])/divM
        center = calculateBBCenter(bb_local)
        pt = [0.0]*(2*numM*numN)
        for i in range(numN):
            for j in range(numM):
                pt[i * numM * pointDim + j * pointDim + 0] = center[0]
                pt[i * numM * pointDim + j * pointDim + 1] = bb_local[1] + j * spaceM
                
        return pt
        
    elif numM == 1 and numN > 1:
        divM = 2
        divN = numN - 1
        spaceN = (bb_local[2] - bb_local[0]) / divN
        center = calculateBBCenter(bb_local)
        pt = [0.0]*((numN-1)*numM*pointDim+numN*pointDim)
        for i in range(numN):
            for j in range(numN):
                pt[i * numM * pointDim + j * pointDim + 0] = bb_local[0] + i * spaceN
                pt[i * numM * pointDim + j * pointDim + 1] = center[1]
        return pt
        
    elif numM > 1 and numN > 1:
        divM = numM - 1
        divN = numN - 1
    
    spaceN = (bb_local[2] - bb_local[0]) / divN
    spaceM = (bb_local[3] - bb_local[1]) / divM

    pt = [0.0]*((numN-1)*numM*pointDim+numM*pointDim)
    
    for i in range(numN):
        for j in range(numM):
            pt[i * numM * pointDim + j * pointDim + 0] = float(bb_local[0] + i * spaceN)
            pt[i * numM * pointDim + j * pointDim + 1] = float(bb_local[1] + j * spaceM)
    return pt

def getBBWidth(bb):

    return bb[2]-bb[0]+1
    
def getBBHeight(bb):

    return bb[3]-bb[1]+1
    
def predictBB(bb0, pt0, pt1, nPts):
    
    ofx = []
    ofy = []
    for i in range(nPts):
        ofx.append(pt1[i][0]-pt0[i][0])
        ofy.append(pt1[i][1]-pt0[i][1])
    
    dx = getMedianUnmanaged(ofx)
    dy = getMedianUnmanaged(ofy)
    ofx=ofy=0
    
    lenPdist = nPts * (nPts - 1) / 2
    dist0=[]
    for i in range(nPts):
        for j in range(i+1,nPts):
            temp0 = ((pt0[i][0] - pt0[j][0])**2 + (pt0[i][1] - pt0[j][1])**2)**0.5
            temp1 = ((pt1[i][0] - pt1[j][0])**2 + (pt1[i][1] - pt1[j][1])**2)**0.5
            dist0.append(float(temp1)/temp0)
            
    shift = getMedianUnmanaged(dist0)
    
    s0 = 0.5 * (shift - 1) * getBBWidth(bb0)
    s1 = 0.5 * (shift - 1) * getBBHeight(bb0)
    
    if shift == 0:
        shift = 1
    x1 = bb0[0] - s0 + dx
    y1 = bb0[1] - s1 + dy
    x2 = bb0[2] + s0 + dx
    y2 = bb0[3] + s1 + dy
    w = x2-x1
    h = y2-y1
    #print x1,x2,y1,y2,w,h
    if x1 <= 0 or x2 <=0 or y1<=0 or y2 <=0 or w <=20 or h <=20:
        x1 = bb0[0]
        y1 = bb0[1]
        x2 = bb0[2]
        y2 = bb0[3]
        
    bb1 = (int(x1),int(y1),int(x2),int(y2))
              
    return (bb1, shift)
    
def getBB(pt0,pt1):
    xmax = np.max((pt0[0],pt1[0]))
    xmin = np.min((pt0[0],pt1[0]))
    ymax = np.max((pt0[1],pt1[1]))
    ymin = np.min((pt0[1],pt1[1]))
    return xmin,ymin,xmax,ymax
    
def getRectFromBB(bb):
    return bb[0],bb[1],bb[2]-bb[0],bb[3]-bb[1]

def lktrack(img1, img2, ptsI, nPtsI, winsize_ncc=10, win_size_lk=4, method=cv2.cv.CV_TM_CCOEFF_NORMED):
    
    template_pt = []
    target_pt = []
    fb_pt = []
    ptsJ = [-1]*len(ptsI)
    
    for i in range(nPtsI):
        template_pt.append((ptsI[2*i],ptsI[2*i+1]))
        target_pt.append((ptsI[2*i],ptsI[2*i+1]))
        fb_pt.append((ptsI[2*i],ptsI[2*i+1]))
    
    template_pt = np.asarray(template_pt,dtype="float32")
    target_pt = np.asarray(target_pt,dtype="float32")
    fb_pt = np.asarray(fb_pt,dtype="float32")
    
    target_pt, status, track_error = cv2.calcOpticalFlowPyrLK(img1, img2, template_pt, target_pt, 
                                     winSize=(win_size_lk, win_size_lk), flags = cv2.OPTFLOW_USE_INITIAL_FLOW,
                                     criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
                                     
    fb_pt, status_bt, track_error_bt = cv2.calcOpticalFlowPyrLK(img2,img1, target_pt,fb_pt, 
                                       winSize = (win_size_lk,win_size_lk),flags = cv2.OPTFLOW_USE_INITIAL_FLOW,
                                       criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    
    status = status & status_bt
    ncc = normCrossCorrelation(img1, img2, template_pt, target_pt, status, winsize_ncc, method)
    fb = euclideanDistance(template_pt, target_pt)
    
    newfb = -1*np.ones(len(fb))
    newncc = -1*np.ones(len(ncc))
    for i in np.argwhere(status):
        i = i[0]
        ptsJ[2 * i] = target_pt[i][0]
        ptsJ[2 * i + 1] = target_pt[i][1]
        newfb[i] = fb[i]
        newncc[i] = ncc[i]

    return newfb, newncc, status, ptsJ
    
def euclideanDistance(point1,point2):
    
    match = ((point1[:,0]-point2[:,0])**2+(point1[:,1]-point2[:,1])**2)**0.5
    return match

def normCrossCorrelation(img1, img2, pt0, pt1, status, winsize, method=cv2.cv.CV_TM_CCOEFF_NORMED):
    
    nPts = len(pt0)
    match = np.zeros(nPts)
    for i in np.argwhere(status):
        i = i[0]
        patch1 = cv2.getRectSubPix(img1,(winsize,winsize),tuple(pt0[i]))
        patch2 = cv2.getRectSubPix(img2,(winsize,winsize),tuple(pt1[i]))
        match[i] = cv2.matchTemplate(patch1,patch2,method)
    return match

from SimpleCV.Features import MFTracker