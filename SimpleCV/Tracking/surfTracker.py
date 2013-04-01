import cv2
import numpy as np
import itertools

def surfTracker(img, bb, ts, **kwargs):
    eps_val = 0.69
    min_samples = 5
    distance = 100

    for key in kwargs:
        if key == 'eps_val':
            eps_val = kwargs[key]
        elif key == 'min_samples':
            min_samples = kwargs[key]
        elif key == 'dist':
            distance = kwargs[key]

    from scipy.spatial import distance as Dis
    from sklearn.cluster import DBSCAN

    if len(ts) == 0:
        # Get template keypoints
        bb = (int(bb[0]), int(bb[1]), int(bb[2]), int(bb[3]))
        templateImg = img
        detector = cv2.FeatureDetector_create("SURF")
        descriptor = cv2.DescriptorExtractor_create("SURF")

        templateImg_cv2 = templateImg.getNumpyCv2()[bb[1]:bb[1]+bb[3], bb[0]:bb[0]+bb[2]]
        tkp = detector.detect(templateImg_cv2)
        tkp, td = descriptor.compute(templateImg_cv2, tkp)

    else:
        templateImg = ts[-1].templateImg
        tkp = ts[-1].tkp
        td = ts[-1].td
        detector = ts[-1].detector
        descriptor = ts[-1].descriptor

    newimg = img.getNumpyCv2()

    # Get image keypoints
    skp = detector.detect(newimg)
    skp, sd = descriptor.compute(newimg, skp)

    if td is None:
        print "Descriptors are Empty"
        return None

    if sd is None:
        track = SURFTracker(img, skp, detector, descriptor, templateImg, skp, sd, tkp, td)
        return track

    # flann based matcher
    flann_params = dict(algorithm=1, trees=4)
    flann = cv2.flann_Index(sd, flann_params)
    idx, dist = flann.knnSearch(td, 1, params={})
    del flann

    # filter points using distnace criteria
    dist = (dist[:,0]/2500.0).reshape(-1,).tolist()
    idx = idx.reshape(-1).tolist()
    indices = sorted(range(len(dist)), key=lambda i: dist[i])

    dist = [dist[i] for i in indices]
    idx = [idx[i] for i in indices]
    skp_final = []
    skp_final_labelled=[]
    data_cluster=[]
    
    for i, dis in itertools.izip(idx, dist):
        if dis < distance:
            skp_final.append(skp[i])
            data_cluster.append((skp[i].pt[0], skp[i].pt[1]))

    #Use Denstiy based clustering to further fitler out keypoints
    n_data = np.asarray(data_cluster)
    D = Dis.squareform(Dis.pdist(n_data))
    S = 1 - (D/np.max(D))
    
    db = DBSCAN(eps=eps_val, min_samples=min_samples).fit(S)
    core_samples = db.core_sample_indices_
    labels = db.labels_
    for label, i in zip(labels, range(len(labels))):
        if label==0:
            skp_final_labelled.append(skp_final[i])

    track = SURFTracker(img, skp_final_labelled, detector, descriptor, templateImg, skp, sd, tkp, td)

    return track

from SimpleCV.Features import SURFTracker