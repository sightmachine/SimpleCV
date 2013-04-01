import cv2
import numpy as np
def CamShift(img, bb, ts, **kwargs):

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
    track = CAMShift(img, track_window, new_ellipse)

    return track

from SimpleCV.Features import CAMShift