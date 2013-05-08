from SimpleCV.base import np, itertools
try:
    import cv2
except ImportError:
    pass

def lkTracker(img, bb, ts, oldimg, **kwargs):
    """
    **DESCRIPTION**
    
    (Dev Zone)

    Tracking the object surrounded by the bounding box in the given
    image using Lucas Kanade based Optical Flow method.

    Warning: Use this if you know what you are doing. Better have a 
    look at Image.track()

    **PARAMETERS**

    * *img* - Image - Image to be tracked.
    * *bb*  - tuple - Bounding Box tuple (x, y, w, h)
    * *ts*  - TrackSet - SimpleCV.Features.TrackSet.
    * *oldimg* - Image - Previous Image.

    Optional PARAMETERS:
    (docs from http://docs.opencv.org/)

    maxCorners    - Maximum number of corners to return in goodFeaturesToTrack. 
                    If there are more corners than are found, the strongest of 
                    them is returned.
                
    qualityLevel  - Parameter characterizing the minimal accepted quality of image corners. 
                    The parameter value is multiplied by the best corner quality measure, 
                    which is the minimal eigenvalue or the Harris function response. 
                    The corners with the quality measure less than the product are rejected.
                    For example, if the best corner has the quality measure = 1500, 
                    and the qualityLevel=0.01 , then all the corners with the quality measure 
                    less than 15 are rejected. 
                  
    minDistance   - Minimum possible Euclidean distance between the returned corners.

    blockSize     - Size of an average block for computing a derivative covariation matrix over each pixel neighborhood.

    winSize       - size of the search window at each pyramid level.

    maxLevel      - 0-based maximal pyramid level number; if set to 0, pyramids are not used (single level), 
                    if set to 1, two levels are used, and so on

    **RETURNS**

    SimpleCV.Features.Tracking.LKTracker

    **HOW TO USE**

    >>> cam = Camera()
    >>> ts = []
    >>> img = cam.getImage()
    >>> bb = (100, 100, 300, 300) # get BB from somewhere
    >>> ts = lkTracker(img, bb, ts, img, maxCorners=4000, qualityLevel=0.5, winSize=(12,12))
    >>> while (some_condition_here):
        ... img = cam.getImage()
        ... bb = ts[-1].bb
        ... prevImg = img
        ... ts = lkTracker(img, bb, ts, prevImg, maxCorners=4000, qualityLevel=0.5, winSize=(12,12))
        ... ts[-1].drawBB()
        ... img.show()

    This is too much confusing. Better use
    Image.track() method.

    READ MORE:

    LK (Lucas Kanade) Tracker:
    It is based on LK Optical Flow. It calculates Optical flow in frame1 to frame2 
    and also in frame2 to frame1 and using back track error, filters out false
    positives.
    """
    maxCorners = 4000
    qualityLevel = 0.08
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

    track = LKTrack(img, bb1, new_pts)    
    return track

from SimpleCV.Tracking import LKTrack
