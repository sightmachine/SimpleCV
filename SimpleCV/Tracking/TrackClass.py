from SimpleCV.Color import Color
from SimpleCV.base import time, np
from SimpleCV.Features.Features import Feature, FeatureSet
try:
    import cv2
except ImportError:
    pass

class Track(Feature):
    """
    **SUMMARY**

    Track class is the base of tracking. All different tracking algorithm
    return different classes but they all belong to Track class. All the
    common attributes are kept in this class

    """
    def __init__(self, img, bb):
        """
        **SUMMARY**

        Initializes all the required parameters and attributes of the class.

        **PARAMETERS**

        * *img* - SimpleCV.ImageClass.Image
        * *bb* - A tuple consisting of (x, y, w, h) of the bounding box

        **RETURNS**

        SimpleCV.Tracking.TrackClass.Track object

        **EXAMPLE**

        >>> track = Track(image, bb)
        """
        self.bb = bb
        self.image = img
        self.bb_x, self.bb_y, self.w, self.h = self.bb
        self.x, self.y = self.center = self.getCenter()
        self.sizeRatio = 1
        self.vel = (0,0)
        self.rt_vel = (0,0)
        self.area = self.getArea()
        self.time = time.time()
        self.cv2numpy = self.image.getNumpyCv2()
        return self

    def getCenter(self):
        """
        **SUMMARY**

        Get the center of the bounding box

        **RETURNS**

        * *tuple* - center of the bounding box (x, y)

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> cen = track.getCenter()
        """
        return (self.bb_x+self.w/2,self.bb_y+self.h/2)

    def getArea(self):
        """
        **SUMMARY**

        Get the area of the bounding box

        **RETURNS**

        Area of the bounding box

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> area = track.getArea()
        """
        return self.w*self.h

    def getImage(self):
        """
        **SUMMARY**

        Get the Image

        **RETURNS**

        SimpleCV.ImageClass.Image

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> i = track.getImage()
        """
        return self.image

    def getBB(self):
        """
        **SUMMARY**

        Get the bounding box

        **RETURNS**

        A tuple  - (x, y, w, h)

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> print track.getBB()
        """
        return self.bb

    def draw(self, color=Color.GREEN, rad=1, thickness=1):
        """
        **SUMMARY**

        Draw the center of the object on the image.

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *rad* - Radius of the circle to be plotted on the center of the object.
        * *thickness* - Thickness of the boundary of the center circle.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> track.draw()
        >>> img.show()
        """
        f = self
        f.image.drawCircle(f.center, rad, color, thickness)

    def drawBB(self, color=Color.GREEN, thickness=3):
        """
        **SUMMARY**

        Draw the bounding box over the object on the image.

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *thickness* - Thickness of the boundary of the bounding box.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> track.drawBB()
        >>> img.show()
        """
        f = self
        f.image.drawRectangle(f.bb_x, f.bb_y, f.w, f.h, color, thickness)

    def showCoordinates(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Show the co-ordinates of the object in text on the Image.

        **PARAMETERS**
        * *pos* - A tuple consisting of x, y values. where to put to the text
        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *size* - Fontsize of the text

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> track.showCoordinates()
        >>> img.show()
        """
        f = self
        img = f.image
        if not pos:
            imgsize = img.size()
            pos = (imgsize[0]-120, 10)
        if not size:
            size = 16
        text = "x = %d  y = %d" % (f.x, f.y)
        img.drawText(text, pos[0], pos[1], color, size)

    def showSizeRatio(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Show the sizeRatio of the object in text on the image.

        **PARAMETERS**
        * *pos* - A tuple consisting of x, y values. where to put to the text
        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *size* - Fontsize of the text

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... ts[-1].showSizeRatio() # For continuous bounding box
            ... img = img1
        """
        f = self
        img = f.image
        if not pos:
            imgsize = img.size()
            pos = (imgsize[0]-120, 30)
        if not size:
            size = 16
        text = "size = %f" % (f.sizeRatio)
        img.drawText(text, pos[0], pos[1], color, size)

    def showPixelVelocity(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Show the Pixel Veloctiy (pixel/frame) of the object in text on the image.

        **PARAMETERS**
        * *pos* - A tuple consisting of x, y values. where to put to the text
        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *size* - Fontsize of the text

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... ts[-1].showPixelVelocity() # For continuous bounding box
            ... img = img1
        """
        f = self
        img = f.image
        vel = f.vel
        if not pos:
            imgsize = img.size()
            pos = (imgsize[0]-120, 90)
        if not size:
            size = 16
        text = "Vx = %.2f Vy = %.2f" % (vel[0], vel[1])
        img.drawText(text, pos[0], pos[1], color, size)
        img.drawText("in pixels/frame", pos[0], pos[1]+size, color, size)

    def showPixelVelocityRT(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Show the Pixel Veloctiy (pixels/second) of the object in text on the image.

        **PARAMETERS**
        * *pos* - A tuple consisting of x, y values. where to put to the text
        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *size* - Fontsize of the text

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... ts[-1].showPixelVelocityRT() # For continuous bounding box
            ... img = img1
        """
        f = self
        img = f.image
        vel_rt = f.vel_rt
        if not pos:
            imgsize = img.size()
            pos = (imgsize[0]-120, 50)
        if not size:
            size = 16
        text = "Vx = %.2f Vy = %.2f" % (vel_rt[0], vel_rt[1])
        img.drawText(text, pos[0], pos[1], color, size)
        img.drawText("in pixels/second", pos[0], pos[1]+size, color, size)

    def processTrack(self, func):
        """
        **SUMMARY**

        This method lets you use your own function on the current image.

        **PARAMETERS**
        * *func* - some user defined function for SimpleCV.ImageClass.Image object

        **RETURNS**

        the value returned by the user defined function

        **EXAMPLE**

        >>> def foo(img):
            ... return img.meanColor()
        >>> mean_color = ts[-1].processTrack(foo)
        """
        return func(self.image)

    def getPredictionPoints(self):
        """
        **SUMMARY**

        get predicted Co-ordinates of the center of the object

        **PARAMETERS**
        None

        **RETURNS**

        * *tuple*

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> track.getPredictedCoordinates()
        """
        return self.predict_pt

    def drawPredicted(self, color=Color.GREEN, rad=1, thickness=1):
        """
        **SUMMARY**

        Draw the center of the object on the image.

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *rad* - Radius of the circle to be plotted on the center of the object.
        * *thickness* - Thickness of the boundary of the center circle.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> track.drawPredicted()
        >>> img.show()
        """
        f = self
        f.image.drawCircle(f.predict_pt, rad, color, thickness)

    def showPredictedCoordinates(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Show the co-ordinates of the object in text on the Image.

        **PARAMETERS**
        * *pos* - A tuple consisting of x, y values. where to put to the text
        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *size* - Fontsize of the text

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> track.showPredictedCoordinates()
        >>> img.show()
        """
        f = self
        img = f.image
        if not pos:
            imgsize = img.size()
            pos = (5, 10)
        if not size:
            size = 16
        text = "Predicted: x = %d  y = %d" % (f.predict_pt[0], f.predict_pt[1])
        img.drawText(text, pos[0], pos[1], color, size)

    def getCorrectedPoints(self):
        """
        **SUMMARY**

        Corrected Co-ordinates of the center of the object

        **PARAMETERS**
        None

        **RETURNS**

        * *tuple*

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> track.getCorrectedCoordinates()
        """
        return self.state_pt

    def showCorrectedCoordinates(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Show the co-ordinates of the object in text on the Image.

        **PARAMETERS**
        * *pos* - A tuple consisting of x, y values. where to put to the text
        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *size* - Fontsize of the text

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> track.showCorrectedCoordinates()
        >>> img.show()
        """
        f = self
        img = f.image
        if not pos:
            imgsize = img.size()
            pos = (5, 40)
        if not size:
            size = 16
        text = "Corrected: x = %d  y = %d" % (f.state_pt[0], f.state_pt[1])
        img.drawText(text, pos[0], pos[1], color, size)

    def drawCorrected(self, color=Color.GREEN, rad=1, thickness=1):
        """
        **SUMMARY**

        Draw the center of the object on the image.

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *rad* - Radius of the circle to be plotted on the center of the object.
        * *thickness* - Thickness of the boundary of the center circle.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> track = Track(img, bb)
        >>> track.drawCorrected()
        >>> img.show()
        """
        f = self
        f.image.drawCircle(f.state_pt, rad, color, thickness)

class CAMShiftTrack(Track):
    """
    **SUMMARY**

    CAMShift Class is returned by track when CAMShift tracking is required.
    This class is a superset of Track Class. And all of Track class'
    attributes can be accessed.

    CAMShift class has "ellipse" attribute which is not present in Track
    """
    def __init__(self, img, bb, ellipse):
        """
        **SUMMARY**

        Initializes all the required parameters and attributes of the CAMShift class.

        **PARAMETERS**

        * *img* - SimpleCV.ImageClass.Image
        * *bb* - A tuple consisting of (x, y, w, h) of the bounding box
        * ellipse* - A tuple

        **RETURNS**

        SimpleCV.Tracking.TrackClass.CAMShiftTrack object

        **EXAMPLE**

        >>> track = CAMShiftTrack(image, bb, ellipse)
        """
        self = Track.__init__(self, img, bb)
        self.ellipse = ellipse

    def getEllipse(self):
        """
        **SUMMARY**

        Returns the ellipse.

        **RETURNS**

        A tuple

        **EXAMPLE**

        >>> track = CAMShiftTrack(image, bb, ellipse)
        >>> e = track.getEllipse()
        """
        return self.ellipse

class LKTrack(Track):
    """
    **SUMMARY**

    LK Tracking class is used for Lucas-Kanade Track algorithm. It's
    derived from Track Class. Apart from all the properties of Track class,
    LK has few other properties. Since in LK tracking method, we obtain tracking
    points, we have functionalities to draw those points on the image.

    """

    def __init__(self, img, bb, pts):
        """
        **SUMMARY**

        Initializes all the required parameters and attributes of the class.

        **PARAMETERS**

        * *img* - SimpleCV.ImageClass.Image
        * *bb* - A tuple consisting of (x, y, w, h) of the bounding box
        * *pts* - List of all the tracking points

        **RETURNS**

        SimpleCV.Tracking.TrackClass.LKTrack object

        **EXAMPLE**

        >>> track = LKTrack(image, bb, pts)
        """

        self = Track.__init__(self, img, bb)
        self.pts = pts

    def getTrackedPoints(self):
        """
        **SUMMARY**

        Returns all the points which are being tracked.

        **RETURNS**

        A list

        **EXAMPLE**

        >>> track = LKTrack(image, bb, pts)
        >>> pts = track.getTrackedPoints()
        """
        return self.pts

    def drawTrackerPoints(self, color=Color.GREEN, radius=1, thickness=1):
        """
        **SUMMARY**

        Draw all the points which are being tracked.

        **PARAMETERS**
        * *color* - Color of the point
        * *radius* - Radius of the point
        *thickness* - thickness of the circle point

        **RETURNS**

        Nothing

        **EXAMPLE**

        >>> track = LKTrack(image, bb, pts)
        >>> track.drawTrackerPoints()
        """
        if type(self.pts) is not type(None):
            for pt in self.pts:
                self.image.drawCircle(ctr=pt, rad=radius, thickness=thickness, color=color)

class SURFTrack(Track):
    """
    **SUMMARY**

    SURFTracker class is used for SURF Based keypoints matching tracking algorithm.
    It's derived from Track Class. Apart from all the properties of Track class SURFTracker
    has few other properties.

    Matches keypoints from the template image and the current frame.
    flann based matcher is used to match the keypoints.
    Density based clustering is used classify points as in-region (of bounding box)
    and out-region points. Using in-region points, new bounding box is predicted using
    k-means.
    """
    def __init__(self, img, new_pts, detector, descriptor, templateImg, skp, sd, tkp, td):
        """
        **SUMMARY**

        Initializes all the required parameters and attributes of the class.

        **PARAMETERS**

        * *img* - SimpleCV.Image
        * *new_pts* - List of all the tracking points found in the image. - list of cv2.KeyPoint
        * *detector* - SURF detector - cv2.FeatureDetector
        * *descriptor* - SURF descriptor - cv2.DescriptorExtractor
        * *templateImg* - Template Image (First image) - SimpleCV.Image
        * *skp* - image keypoints - list of cv2.KeyPoint
        * *sd* - image descriptor - numpy.ndarray
        * *tkp* - Template Imaeg keypoints - list of cv2.KeyPoint
        * *td* - Template image descriptor - numpy.ndarray

        **RETURNS**

        SimpleCV.Tracking.TrackClass.SURFTrack object

        **EXAMPLE**
        >>> track = SURFTracker(image, pts, detector, descriptor, temp, skp, sd, tkp, td)
        """
        if td is None:
            bb = (1, 1, 1, 1)
            self = Track.__init__(self, img, bb)
            return
        if len(new_pts) < 1:
            bb = (1, 1, 1, 1)
            self = Track.__init__(self, img, bb)
            self.pts = None
            self.templateImg = templateImg
            self.skp = skp
            self.sd = sd
            self.tkp = tkp
            self.td = td
            self.detector = detector
            self.descriptor = descriptor
            return
        if sd is None:
            bb = (1, 1, 1, 1)
            self = Track.__init__(self, img, bb)
            self.pts = None
            self.templateImg = templateImg
            self.skp = skp
            self.sd = sd
            self.tkp = tkp
            self.td = td
            self.detector = detector
            self.descriptor = descriptor
            return

        np_pts = np.asarray([kp.pt for kp in new_pts])
        t, pts, center = cv2.kmeans(np.asarray(np_pts, dtype=np.float32), K=1, bestLabels=None,
                            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER, 1, 10), attempts=1,
                            flags=cv2.KMEANS_RANDOM_CENTERS)
        max_x = int(max(np_pts[:, 0]))
        min_x = int(min(np_pts[:, 0]))
        max_y = int(max(np_pts[:, 1]))
        min_y = int(min(np_pts[:, 1]))

        bb =  (min_x-5, min_y-5, max_x-min_x+5, max_y-min_y+5)

        self = Track.__init__(self, img, bb)
        self.templateImg = templateImg
        self.skp = skp
        self.sd = sd
        self.tkp = tkp
        self.td = td
        self.pts = np_pts
        self.detector = detector
        self.descriptor = descriptor

    def getTrackedPoints(self):
        """
        **SUMMARY**

        Returns all the points which are being tracked.

        **RETURNS**

        A list of points.

        **EXAMPLE**

        >>> track = SURFTrack(image, pts, detector, descriptor, temp, skp, sd, tkp, td)
        >>> pts = track.getTrackedPoints()
        """
        return self.pts

    def drawTrackerPoints(self, color=Color.GREEN, radius=1, thickness=1):
        """
        **SUMMARY**

        Draw all the points which are being tracked.

        **PARAMETERS**
        * *color* - Color of the point
        * *radius* - Radius of the point
        *thickness* - thickness of the circle point

        **RETURNS**

        Nothing

        **EXAMPLE**

        >>> track = SURFTrack(image, pts, detector, descriptor, temp, skp, sd, tkp, td)
        >>> track.drawTrackerPoints()
        """
        if type(self.pts) is not type(None):
            for pt in self.pts:
                self.image.drawCircle(ctr=pt, rad=radius, thickness=thickness, color=color)

    def getDetector(self):
        """
        **SUMMARY**

        Returns SURF detector which is being used.

        **RETURNS**

        detector - cv2.Detctor

        **EXAMPLE**

        >>> track = SURFTrack(image, pts, detector, descriptor, temp, skp, sd, tkp, td)
        >>> detector = track.getDetector()
        """
        return self.detector

    def getDescriptor(self):
        """
        **SUMMARY**

        Returns SURF descriptor extractor which is being used.

        **RETURNS**

        detector - cv2.DescriptorExtractor

        **EXAMPLE**

        >>> track = SURFTrack(image, pts, detector, descriptor, temp, skp, sd, tkp, td)
        >>> descriptor= track.getDescriptor()
        """
        return self.descriptor

    def getImageKeyPoints(self):
        """
        **SUMMARY**

        Returns all the keypoints which are found on the image.

        **RETURNS**

        A list of points.

        **EXAMPLE**

        >>> track = SURFTrack(image, pts, detector, descriptor, temp, skp, sd, tkp, td)
        >>> skp = track.getImageKeyPoints()
        """
        return self.skp

    def getImageDescriptor(self):
        """
        **SUMMARY**

        Returns the image descriptor.

        **RETURNS**

        Image descriptor - numpy.ndarray

        **EXAMPLE**

        >>> track = SURFTrack(image, pts, detector, descriptor, temp, skp, sd, tkp, td)
        >>> sd = track.getImageDescriptor()
        """
        return self.sd

    def getTemplateKeyPoints(self):
        """
        **SUMMARY**

        Returns all the keypoints which are found on the template Image.

        **RETURNS**

        A list of points.

        **EXAMPLE**

        >>> track = SURFTrack(image, pts, detector, descriptor, temp, skp, sd, tkp, td)
        >>> tkp = track.getTemplateKeyPoints()
        """
        return self.tkp

    def getTemplateDescriptor(self):
        """
        **SUMMARY**

        Returns the template image descriptor.

        **RETURNS**

        Image descriptor - numpy.ndarray

        **EXAMPLE**

        >>> track = SURFTrack(image, pts, detector, descriptor, temp, skp, sd, tkp, td)
        >>> td = track.getTemplateDescriptor()
        """
        return self.td

    def getTemplateImage(self):
        """
        **SUMMARY**

        Returns Template Image.

        **RETURNS**

        Template Image - SimpleCV.Image

        **EXAMPLE**

        >>> track = SURFTrack(image, pts, detector, descriptor, temp, skp, sd, tkp, td)
        >>> templateImg = track.getTemplateImage()
        """
        return self.templateImg

class MFTrack(Track):
    """
    **SUMMARY**

    MFTracker class is used for Median Flow Tracking algorithm. It's
    derived from Track Class. Apart from all the properties of Track class,
    MFTracker has few other properties.

    Media Flow Tracker is the base tracker that is used in OpenTLD. It is based on
    Optical Flow. It calculates optical flow of the points in the bounding box from
    frame 1 to frame 2 and from frame 2 to frame 1 and using back track error, removes
    false positives. As the name suggests, it takes the median of the flow, and eliminates
    points.


    """
    def __init__(self, img, bb, shift):
        """
        **SUMMARY**

        Initializes all the required parameters and attributes of the class.

        **PARAMETERS**

        * *img* - SimpleCV.ImageClass.Image
        * *bb* - A tuple consisting of (x, y, w, h) of the bounding box
        * *shift* - Object Shift calcluated in Median Flow

        **RETURNS**

        SimpleCV.Tracking.TrackClass.MFTrack object

        **EXAMPLE**

        >>> track = MFTrack(image, bb, shift)
        """
        self = Track.__init__(self, img, bb)
        self.shift = shift

    def getShift(self):
        """
        **SUMMARY**

        Returns object shift that was calcluated in Median Flow.

        **RETURNS**

        float

        **EXAMPLE**

        >>> track = MFTrack(image, bb, pts)
        >>> pts = track.getShift()
        """
        return self.shift

    def showShift(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Show the Pixel Veloctiy (pixels/second) of the object in text on the image.

        **PARAMETERS**
        * *pos* - A tuple consisting of x, y values. where to put to the text
        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *size* - Fontsize of the text

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**
        >>> ts = []
        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("mftrack", ts, img, bb)
            ... ts[-1].showShift()
            ... img1.show()
        """
        f = self
        img = f.image
        shift = f.shift
        if not pos:
            imgsize = img.size()
            pos = (imgsize[0]-120, 50)
        if not size:
            size = 16
        text = "Shift = %.2f" % (shift)
        img.drawText(text, pos[0], pos[1], color, size)
        img.drawText("in pixels/second", pos[0], pos[1]+size, color, size)
