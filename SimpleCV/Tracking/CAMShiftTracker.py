from SimpleCV.base import np
try:
    import cv2
except ImportError:
    pass

def camshiftTracker(img, bb, ts, **kwargs):
    """
    **DESCRIPTION**
    
    (Dev Zone)

    Tracking the object surrounded by the bounding box in the given
    image using CAMshift method.

    Warning: Use this if you know what you are doing. Better have a 
    look at Image.track()

    **PARAMETERS**

    * *img* - Image - Image to be tracked.
    * *bb*  - tuple - Bounding Box tuple (x, y, w, h)
    * *ts*  - TrackSet - SimpleCV.Features.TrackSet.

    Optional PARAMETERS:

    lower      - Lower HSV value for inRange thresholding
                 tuple of (H, S, V)
                
    upper      - Upper HSV value for inRange thresholding
                 tuple of (H, S, V)

    mask       - Mask to calculate Histogram. It's better 
                 if you don't provide one.

    num_frames - number of frames to be backtracked.

    **RETURNS**

    SimpleCV.Features.Tracking.CAMShift

    **HOW TO USE**

    >>> cam = Camera()
    >>> ts = []
    >>> img = cam.getImage()
    >>> bb = (100, 100, 300, 300) # get BB from somewhere
    >>> ts = CAMShiftTracker(img, bb, ts, lower=(40, 120, 120), upper=(80, 200, 200), num_frames=30)
    >>> while (some_condition_here):
        ... img = cam.getImage()
        ... bb = ts[-1].bb
        ... ts = CAMShiftTracker(img, bb, ts, lower=(40, 120, 120), upper=(80, 200, 200), num_frames=30)
        ... ts[-1].drawBB()
        ... img.show()

    This is too much confusing. Better use
    Image.track() method.

    READ MORE:

    CAMShift Tracker:
    Uses meanshift based CAMShift thresholding technique. Blobs and objects with
    single tone or tracked very efficiently. CAMshift should be preferred if you 
    are trying to track faces. It is optimized to track faces.
    """

    lower = np.array((0., 60., 32.))
    upper = np.array((180., 255., 255.))
    mask = None
    num_frames = 40

    if not isinstance(bb, tuple):
        bb = tuple(bb)
    bb = (int(bb[0]), int(bb[1]), int(bb[2]), int(bb[3]))

    for key in kwargs:
        if key == 'lower':
            lower = np.array(tuple(kwargs[key]))
        elif key == 'upper':
            upper = np.array(tuple(kwargs[key]))
        elif key == 'mask':
            mask = kwargs[key]
            mask = mask.getNumpyCv2()
        elif key == 'num_frames':
            num_frames = kwargs[key]

    hsv = cv2.cvtColor(img.getNumpyCv2(), cv2.cv.CV_BGR2HSV)
    if mask is None:
        mask = cv2.inRange(hsv, lower, upper)

    x0, y0, w, h = bb
    x1 = x0 + w -1
    y1 = y0 + h -1
    hsv_roi = hsv[y0:y1, x0:x1]
    mask_roi = mask[y0:y1, x0:x1]

    hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX);
    hist_flat = hist.reshape(-1)
    imgs = [hsv]
    if len(ts) > num_frames and num_frames > 1:
        for feat in ts[-num_frames:]:
            imgs.append(feat.image.toHSV().getNumpyCv2())
    elif len(ts) < num_frames and num_frames > 1:
        for feat in ts:
            imgs.append(feat.image.toHSV().getNumpyCv2())

    prob = cv2.calcBackProject(imgs, [0], hist_flat, [0, 180], 1)
    prob &= mask
    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
    new_ellipse, track_window = cv2.CamShift(prob, bb, term_crit)
    if track_window[2] == 0 or track_window[3] == 0:
        track_window = bb
    track = CAMShiftTrack(img, track_window, new_ellipse)

    return track

from SimpleCV.Tracking import CAMShiftTrack
