from SimpleCV.base import np, cv, math, time, spsd
from copy import copy
try:
    import cv2
except ImportError:
    pass

def mfTracker(img, bb, ts, oldimg, **kwargs):
    """
    **DESCRIPTION**
    
    (Dev Zone)

    Tracking the object surrounded by the bounding box in the given
    image using SURF keypoints.

    Warning: Use this if you know what you are doing. Better have a 
    look at Image.track()

    **PARAMETERS**

    * *img* - Image - Image to be tracked.
    * *bb*  - tuple - Bounding Box tuple (x, y, w, h)
    * *oldimg* - Image - Previous Image
    * *ts*  - TrackSet - SimpleCV.Features.TrackSet.

    Optional PARAMETERS:

    numM     - Number of points to be tracked in the bounding box
               in height direction. 
                
    numN     - Number of points to be tracked in the bounding box
               in width direction. 
                  
    margin   - Margin around the bounding box.

    winsize_lk  - Optical Flow search window size.

    winsize - Size of quadratic area around the point which is compared.

    **RETURNS**

    SimpleCV.Features.Tracking.MFTracker

    **HOW TO USE**

    >>> cam = Camera()
    >>> ts = []
    >>> img = cam.getImage()
    >>> bb = (100, 100, 300, 300) # get BB from somewhere
    >>> ts = MFTracker(img, bb, ts, img, numM=15, numN=15, winsize=12)
    >>> while (some_condition_here):
        ... img = cam.getImage()
        ... bb = ts[-1].bb
        ... prevImg = img
        ... ts = MFTracker(img, bb, ts, img, numM=15, numN=15, winsize=12)
        ... ts[-1].drawBB()
        ... img.show()

    This is too much confusing. Better use
    Image.track() method.

    READ MORE:

    Median Flow Tracker:
    
    Media Flow Tracker is the base tracker that is used in OpenTLD. It is based on
    Optical Flow. It calculates optical flow of the points in the bounding box from
    frame 1 to frame 2 and from frame 2 to frame 1 and using back track error, removes
    false positives. As the name suggests, it takes the median of the flow, and eliminates
    points.
    """
    numM = 10
    numN = 10
    margin = 5
    winsize_ncc = 10
    winsize_lk = 4

    for key in kwargs:
        if key == 'numM':
            numM = kwargs[key]
        elif key == 'numN':
            numN = kwargs[key]
        elif key == 'margin':
            margin = kwargs[key]
        elif key == 'winsize':
            winsize_ncc = kwargs[key]
        elif key == 'winsize_lk':
            winsize_lk = kwargs[key]

    oldg = oldimg.getGrayNumpyCv2()
    newg = img.getGrayNumpyCv2()
    bb = [bb[0], bb[1], bb[0]+bb[2], bb[1]+bb[3]]
    bb, shift = fbtrack(oldg, newg, bb, numM, numN, margin, winsize_ncc, winsize_lk)
    bb = [bb[0], bb[1], bb[2]-bb[0], bb[3]-bb[1]]
    track = MFTrack(img, bb, shift)
    return track

def fbtrack(imgI, imgJ, bb, numM=10, numN=10,margin=5,winsize_ncc=10, winsize_lk=4):
    """
    **SUMMARY**
    (Dev Zone)
    Forward-Backward tracking using Lucas-Kanade Tracker
    
    **PARAMETERS**
    
    imgI - Image contain Object with known BoundingBox (Numpy array)
    imgJ - Following image (Numpy array)
    bb - Bounding box represented through 2 points (x1,y1,x2,y2)
    numM - Number of points in height direction.
    numN - Number of points in width direction.
    margin - margin (in pixel)
    winsize_ncc - Size of quadratic area around the point which is compared.
    
    **RETURNS**
    
    newbb - Bounding box of object in track in imgJ
    scaleshift - relative scale change of bb
    
    """

    nPoints = numM*numN
    sizePointsArray = nPoints*2
    #print bb, "passed in fbtrack"
    pt = getFilledBBPoints(bb, numM, numN, margin)
    fb, ncc, status, ptTracked = lktrack(imgI, imgJ, pt, nPoints, winsize_ncc, winsize_lk)

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

def lktrack(img1, img2, ptsI, nPtsI, winsize_ncc=10, win_size_lk=4, method=cv2.cv.CV_TM_CCOEFF_NORMED):
    """
    **SUMMARY**
    (Dev Zone)
    Lucas-Kanede Tracker with pyramids
    
    **PARAMETERS**
    
    img1 - Previous image or image containing the known bounding box (Numpy array)
    img2 - Current image
    ptsI - Points to track from the first image
           Format ptsI[0] - x1, ptsI[1] - y1, ptsI[2] - x2, ..
    nPtsI - Number of points to track from the first image
    winsize_ncc - size of the search window at each pyramid level in LK tracker (in int)
    method - Paramete specifying the comparison method for normalized cross correlation 
             (see http://opencv.itseez.com/modules/imgproc/doc/object_detection.html?highlight=matchtemplate#cv2.matchTemplate)
    
    **RETURNS**
    
    fb - forward-backward confidence value. (corresponds to euclidean distance between).
    ncc - normCrossCorrelation values
    status - Indicates positive tracks. 1 = PosTrack 0 = NegTrack
    ptsJ - Calculated Points of second image
    
    """ 
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
    """
    
    **SUMMARY**
    (Dev Zone)
    Calculates the center of the given bounding box
    
    **PARAMETERS**
    
    bb - Bounding Box represented through 2 points (x1,y1,x2,y2)
    
    **RETURNS**
    
    center - A tuple of two floating points
    
    """
    center = (0.5*(bb[0] + bb[2]),0.5*(bb[1]+bb[3]))
    return center
    
def getFilledBBPoints(bb, numM, numN, margin):
    """
    
    **SUMMARY**
    (Dev Zone)
    Creates numM x numN points grid on Bounding Box
    
    **PARAMETERS**
    
    bb - Bounding Box represented through 2 points (x1,y1,x2,y2)
    numM - Number of points in height direction.
    numN - Number of points in width direction.
    margin - margin (in pixel)
    
    **RETURNS**
    
    pt - A list of points (pt[0] - x1, pt[1] - y1, pt[2] - x2, ..)
    
    """
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
    """
    
    **SUMMARY**
    (Dev Zone)
    Get width of the bounding box
    
    **PARAMETERS**
    
    bb - Bounding Box represented through 2 points (x1,y1,x2,y2)
    
    **RETURNS**
    
    width of the bounding box
    
    """
    return bb[2]-bb[0]+1
    
def getBBHeight(bb):
    """
    
    **SUMMARY**
    (Dev Zone)
    Get height of the bounding box
    
    **PARAMETERS**
    
    bb - Bounding Box represented through 2 points (x1,y1,x2,y2)
    
    **RETURNS**
    
    height of the bounding box
    """
    return bb[3]-bb[1]+1
    
def predictBB(bb0, pt0, pt1, nPts):
    """
    
    **SUMMARY**
    (Dev Zone)
    Calculates the new (moved and resized) Bounding box.
    Calculation based on all relative distance changes of all points
    to every point. Then the Median of the relative Values is used.
    
    **PARAMETERS**
    
    bb0 - Bounding Box represented through 2 points (x1,y1,x2,y2)
    pt0 - Starting Points
    pt1 - Target Points
    nPts - Total number of points (eg. len(pt0))
    
    **RETURNS**
    
    bb1 - new bounding box
    shift - relative scale change of bb0
    
    """
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
            if temp0 != 0:
                dist0.append(float(temp1)/temp0)
            else:
                dist0.append(1.0)
            
    shift = getMedianUnmanaged(dist0)
    if shift is None:
        return(bb0, 1.0)

    # too much variation in shift is due to some errors
    if shift > 1.1 or shift < 0.9:
        shift = 1
    s0 = 0.5 * (shift - 1) * getBBWidth(bb0)
    s1 = 0.5 * (shift - 1) * getBBHeight(bb0)
    
    
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
    
def euclideanDistance(point1,point2):
    """
    (Dev Zone)
    **SUMMARY**
    
    Calculates eculidean distance between two points
    
    **PARAMETERS**
    
    point1 - vector of points
    point2 - vector of points with same length
    
    **RETURNS**
    
    match = returns a vector of eculidean distance
    """
    match = ((point1[:,0]-point2[:,0])**2+(point1[:,1]-point2[:,1])**2)**0.5
    return match

def normCrossCorrelation(img1, img2, pt0, pt1, status, winsize, method=cv2.cv.CV_TM_CCOEFF_NORMED):
    """
    **SUMMARY**
    (Dev Zone)
    Calculates normalized cross correlation for every point.
    
    **PARAMETERS**
    
    img1 - Image 1.
    img2 - Image 2.
    pt0 - vector of points of img1
    pt1 - vector of points of img2
    status - Switch which point pairs should be calculated.
             if status[i] == 1 => match[i] is calculated.
             else match[i] = 0.0
    winsize- Size of quadratic area around the point
             which is compared.
    method - Specifies the way how image regions are compared. see cv2.matchTemplate
    
    **RETURNS**
    
    match - Output: Array will contain ncc values.
            0.0 if not calculated.
 
    """
    nPts = len(pt0)
    match = np.zeros(nPts)
    for i in np.argwhere(status):
        i = i[0]
        patch1 = cv2.getRectSubPix(img1,(winsize,winsize),tuple(pt0[i]))
        patch2 = cv2.getRectSubPix(img2,(winsize,winsize),tuple(pt1[i]))
        match[i] = cv2.matchTemplate(patch1,patch2,method)
    return match

from SimpleCV.Tracking import MFTrack
