from SimpleCV.Color import Color
from SimpleCV.base import time, cv, np
from SimpleCV.Features.Features import Feature, FeatureSet
from SimpleCV.ImageClass import Image


class TrackSet(FeatureSet):
    """
    **SUMMARY**

    TrackSet is a class extended from FeatureSet which is a class
    extended from Python's list. So, TrackSet has all the properties
    of a list as well as all the properties of FeatureSet.

    In general, functions dealing with attributes will return
    numpy arrays.

    This class is specifically made for Tracking.

    **EXAMPLE**

    >>> image = Image("/path/to/image.png")
    >>> ts = image.track("camshift", img1=image, bb)  #ts is the track set
    >>> ts.draw()
    >>> ts.x()
    """
    try:
        import cv2
    except ImportError:
        warnings.warn("OpenCV >= 2.3.1 required.")
    
    def __init__(self):
        self.kalman = None
        self.predict_pt = (0,0)
        self.__kalman()

    def append(self, f):
        """
        **SUMMARY**

        This is a substitute function for append. This is used in
        Image.track(). To get z, vel, etc I have to use this.
        This sets few parameters up and appends Tracking object to
        TrackSet list.
        Users are discouraged to use this function.

        **RETURNS**
            Nothing.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> ts.append(CAMShift(img,bb,ellipse))
        """
        list.append(self,f)
        ts = self
        if ts[0].area <= 0:
            return
        f.sizeRatio = float(ts[-1].area)/float(ts[0].area)
        f.vel = self.__pixelVelocity()
        f.rt_vel = self.__pixleVelocityRealTime()
        self.__setKalman()
        self.__predictKalman()
        self.__changeMeasure()
        self.__correctKalman()
        f.predict_pt = self.predict_pt
        f.state_pt = self.state_pt

    # Issue #256 - (Bug) Memory management issue due to too many number of images.
    def trimList(self, num):
        """
        **SUMMARY**

        Trims the TrackSet(lists of all the saved objects) to save memory. It is implemented in
        Image.track() by default, but if you want to trim the list manually, use this.

        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... if len(ts) > 30:
                ... ts.trimList(10)
            ... img = img1
        """
        ts = self
        for i in range(num):
            ts.pop(0)

    def areaRatio(self):
        """
        **SUMMARY**

        Returns a numpy array of the areaRatio of each feature.
        where areaRatio is the ratio of the size of the current bounding box to
        the size of the initial bounding box

        **RETURNS**

        A numpy array.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.areaRatio

        """
        return np.array([f.areaRatio for f in self])

    def drawPath(self, color=Color.GREEN, thickness=2):
        """
        **SUMMARY**

        Draw the complete path traced by the center of the object on current frame

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *thickness* - Thickness of the tracing path.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... ts.drawPath() # For continuous tracing
            ... img = img1
        >>> ts.drawPath() # draw the path at the end of tracking
        """

        ts = self
        img = self[-1].image
        for i in range(len(ts)-1):
            img.drawLine((ts[i].center),(ts[i+1].center), color=color, thickness=thickness)

    def draw(self, color=Color.GREEN, rad=1, thickness=1):
        """
        **SUMMARY**

        Draw the center of the object on the current frame.

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *rad* - Radius of the circle to be plotted on the center of the object.
        * *thickness* - Thickness of the boundary of the center circle.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... ts.draw() # For continuous tracking of the center
            ... img = img1
        """
        f = self[-1]
        f.image.drawCircle(f.center, rad, color, thickness)

    def drawBB(self, color=Color.GREEN, thickness=3):
        """
        **SUMMARY**

        Draw the bounding box over the object on the current frame.

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *thickness* - Thickness of the boundary of the bounding box.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... ts.drawBB() # For continuous bounding box
            ... img = img1
        """
        f = self[-1]
        f.image.drawRectangle(f.bb_x, f.bb_y, f.w, f.h, color, thickness)

    def trackLength(self):
        """
        **SUMMARY**

        Get total number of tracked frames.

        **PARAMETERS**

        No Parameters required.

        **RETURNS**

        * *int* * -Number of tracked image frames

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.trackLength()
        """
        return len(self)

    def trackImages(self, cv2_numpy=False):
        """
        **SUMMARY**

        Get all the tracked images in a list

        **PARAMETERS**

        No Parameters required.

        **RETURNS**

        * *list* * - A list of all the tracked SimpleCV.ImageClass.Image

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> imgset = ts.trackImages()
        """
        if cv2_numpy:
            return [f.cv2numpy for f in self]
        return [f.image for f in self]

    def BBTrack(self):
        """
        **SUMMARY**

        Get all the bounding box in a list

        **PARAMETERS**

        No Parameters required.

        **RETURNS**

        * *list* * - All the bounding box co-ordinates in a list

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.BBTrack()
        """
        return [f.bb for f in self]

    def __pixelVelocity(self):
        """
        **SUMMARY**

        Get Pixel Velocity of the tracked object in pixel/frame.

        **PARAMETERS**

        No Parameters required.

        **RETURNS**

        * *tuple* * - (Velocity of x, Velocity of y)

        """
        ts = self
        if len(ts) < 2:
            return (0,0)
        dx = ts[-1].x - ts[-2].x
        dy = ts[-1].y - ts[-2].y
        return (dx, dy)

    def pixelVelocity(self):
        """
        **SUMMARY**

        Get each Pixel Velocity of the tracked object in pixel/frames.

        **PARAMETERS**

        No Parameters required.

        **RETURNS**

        * *numpy array* * - array of pixel velocity tuple.

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.pixelVelocity()
        """
        return np.array([f.vel for f in self])

    def __pixleVelocityRealTime(self):
        """
        **SUMMARY**

        Get each Pixel Velocity of the tracked object in pixel/second.

        **PARAMETERS**

        No Parameters required.

        **RETURNS**

        * *tuple* * - velocity tuple
        """
        ts = self
        if len(ts) < 2:
            return (0,0)
        dx = ts[-1].x - ts[-2].x
        dy = ts[-1].y - ts[-2].y
        dt = ts[-1].time - ts[-2].time
        return (float(dx)/dt, float(dy)/dt)

    def pixleVelocityRealTime(self):
        """
        **SUMMARY**

        Get each Pixel Velocity of the tracked object in pixel/frames.

        **PARAMETERS**

        No Parameters required.

        **RETURNS**

        * *numpy array* * - array of pixel velocity tuple.

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.pixelVelocityRealTime()
        """
        return np.array([f.rt_vel for f in self])

    def showCoordinates(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Show the co-ordinates of the object in text on the current frame.

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
            ... ts.showCoordinates() # For continuous bounding box
            ... img = img1
        """
        ts = self
        f = ts[-1]
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

        Show the sizeRatio of the object in text on the current frame.

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
            ... ts.showZ() # For continuous bounding box
            ... img = img1
        """
        ts = self
        f = ts[-1]
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

        show the Pixel Veloctiy (pixel/frame) of the object in text on the current frame.

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
            ... ts.showPixelVelocity() # For continuous bounding box
            ... img = img1
        """
        ts = self
        f = ts[-1]
        img = f.image
        vel = f.vel
        if not pos:
            imgsize = img.size()
            pos = (imgsize[0]-120, 50)
        if not size:
            size = 16
        text = "Vx = %.2f Vy = %.2f" % (vel[0], vel[1])
        img.drawText(text, pos[0], pos[1], color, size)
        img.drawText("in pixels/frame", pos[0], pos[1]+size, color, size)

    def showPixelVelocityRT(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        show the Pixel Veloctiy (pixels/second) of the object in text on the current frame.

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
            ... ts.showPixelVelocityRT() # For continuous bounding box
            ... img = img1
        """
        ts = self
        f = ts[-1]
        img = f.image
        vel_rt = f.rt_vel
        if not pos:
            imgsize = img.size()
            pos = (imgsize[0]-120, 90)
        if not size:
            size = 16
        text = "Vx = %.2f Vy = %.2f" % (vel_rt[0], vel_rt[1])
        img.drawText(text, pos[0], pos[1], color, size)
        img.drawText("in pixels/second", pos[0], pos[1]+size, color, size)

    def processTrack(self, func):
        """
        **SUMMARY**

        This method lets you use your own function on the entire imageset.

        **PARAMETERS**
        * *func* - some user defined function for SimpleCV.ImageClass.Image object

        **RETURNS**

        * *list* - list of the values returned by the function when applied on all the images

        **EXAMPLE**

        >>> def foo(img):
            ... return img.meanColor()
        >>> mean_color_list = ts.processTrack(foo)
        """
        return [func(f.image) for f in self]

    def getBackground(self):
        """
        **SUMMARY**

        Get Background of the Image. For more info read
        http://opencvpython.blogspot.in/2012/07/background-extraction-using-running.html

        **PARAMETERS**
        No Parameters

        **RETURNS**

        Image - SimpleCV.ImageClass.Image

        **EXAMPLE**

        >>> while (some_condition):
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> ts.getBackground().show()
        """
        imgs = self.trackImages(cv2_numpy=True)
        f = imgs[0]
        avg = np.float32(f)
        for img in imgs[1:]:
            f = img
            cv2.accumulateWeighted(f,avg,0.01)
            res = cv2.convertScaleAbs(avg)
        return Image(res, cv2image=True)

    def __kalman(self):
        self.kalman = cv.CreateKalman(4, 2, 0)
        self.kalman_state = cv.CreateMat(4, 1, cv.CV_32FC1)  # (phi, delta_phi)
        self.kalman_process_noise = cv.CreateMat(4, 1, cv.CV_32FC1)
        self.kalman_measurement = cv.CreateMat(2, 1, cv.CV_32FC1)

    def __setKalman(self):
        ts = self
        if len(ts) < 2:
            self.kalman_x = ts[-1].x
            self.kalman_y = ts[-1].y
        else:
            self.kalman_x = ts[-2].x
            self.kalman_y = ts[-2].y

        self.kalman.state_pre[0,0]  = self.kalman_x
        self.kalman.state_pre[1,0]  = self.kalman_y
        self.kalman.state_pre[2,0]  = self.predict_pt[0]
        self.kalman.state_pre[3,0]  = self.predict_pt[1]

        self.kalman.transition_matrix[0,0] = 1
        self.kalman.transition_matrix[0,1] = 0
        self.kalman.transition_matrix[0,2] = 1
        self.kalman.transition_matrix[0,3] = 0
        self.kalman.transition_matrix[1,0] = 0
        self.kalman.transition_matrix[1,1] = 1
        self.kalman.transition_matrix[1,2] = 0
        self.kalman.transition_matrix[1,3] = 1
        self.kalman.transition_matrix[2,0] = 0
        self.kalman.transition_matrix[2,1] = 0
        self.kalman.transition_matrix[2,2] = 1
        self.kalman.transition_matrix[2,3] = 0
        self.kalman.transition_matrix[3,0] = 0
        self.kalman.transition_matrix[3,1] = 0
        self.kalman.transition_matrix[3,2] = 0
        self.kalman.transition_matrix[3,3] = 1

        cv.SetIdentity(self.kalman.measurement_matrix, cv.RealScalar(1))
        cv.SetIdentity(self.kalman.process_noise_cov, cv.RealScalar(1e-5))
        cv.SetIdentity(self.kalman.measurement_noise_cov, cv.RealScalar(1e-1))
        cv.SetIdentity(self.kalman.error_cov_post, cv.RealScalar(1))

    def __predictKalman(self):
        self.kalman_prediction = cv.KalmanPredict(self.kalman)
        self.predict_pt  = (self.kalman_prediction[0,0], self.kalman_prediction[1,0])

    def __correctKalman(self):
        self.kalman_estimated = cv.KalmanCorrect(self.kalman, self.kalman_measurement)
        self.state_pt = (self.kalman_estimated[0,0], self.kalman_estimated[1,0])

    def __changeMeasure(self):
        ts = self
        self.kalman_measurement[0, 0] = ts[-1].x
        self.kalman_measurement[1, 0] = ts[-1].y

    def predictedCoordinates(self):
        """
        **SUMMARY**

        Returns a numpy array of the predicted coordinates of each feature.

        **RETURNS**

        A numpy array.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.predictedCoordinates()

        """
        return np.array([f.predict_pt for f in self])

    def predictX(self):
        """
        **SUMMARY**

        Returns a numpy array of the predicted x (vertical) coordinate of each feature.

        **RETURNS**

        A numpy array.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.predictX()

        """
        return np.array([f.predict_pt[0] for f in self])

    def predictY(self):
        """
        **SUMMARY**

        Returns a numpy array of the predicted y (vertical) coordinate of each feature.

        **RETURNS**

        A numpy array.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.predictY()

        """
        return np.array([f.predict_pt[1] for f in self])

    def drawPredicted(self, color=Color.GREEN, rad=1, thickness=1):
        """
        **SUMMARY**

        Draw the predcited center of the object on the current frame.

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *rad* - Radius of the circle to be plotted on the center of the object.
        * *thickness* - Thickness of the boundary of the center circle.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... ts.drawPredicted() # For continuous tracking of the center
            ... img = img1
        """
        f = self[-1]
        f.image.drawCircle(f.predict_pt, rad, color, thickness)

    def drawCorrected(self, color=Color.GREEN, rad=1, thickness=1):
        """
        **SUMMARY**

        Draw the predcited center of the object on the current frame.

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *rad* - Radius of the circle to be plotted on the center of the object.
        * *thickness* - Thickness of the boundary of the center circle.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... ts.drawPredicted() # For continuous tracking of the center
            ... img = img1
        """
        f = self[-1]
        f.image.drawCircle(f.state_pt, rad, color, thickness)

    def drawPredictedPath(self, color=Color.GREEN, thickness=2):
        """
        **SUMMARY**

        Draw the complete predicted path of the center of the object on current frame

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *thickness* - Thickness of the tracing path.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... ts.drawPredictedPath() # For continuous tracing
            ... img = img1
        >>> ts.drawPredictedPath() # draw the path at the end of tracking
        """

        ts = self
        img = self[-1].image
        for i in range(1, len(ts)-1):
            img.drawLine((ts[i].predict_pt),(ts[i+1].predict_pt), color=color, thickness=thickness)

    def showPredictedCoordinates(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Show the co-ordinates of the object in text on the current frame.

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
            ... ts.showPredictedCoordinates() # For continuous bounding box
            ... img = img1
        """
        ts = self
        f = ts[-1]
        img = f.image
        if not pos:
            imgsize = img.size()
            pos = (5, 10)
        if not size:
            size = 16
        text = "Predicted: x = %d  y = %d" % (f.predict_pt[0], f.predict_pt[1])
        img.drawText(text, pos[0], pos[1], color, size)

    def showCorrectedCoordinates(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Show the co-ordinates of the object in text on the current frame.

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
            ... ts.showCorrectedCoordinates() # For continuous bounding box
            ... img = img1
        """
        ts = self
        f = ts[-1]
        img = f.image
        if not pos:
            imgsize = img.size()
            pos = (5, 40)
        if not size:
            size = 16
        text = "Corrected: x = %d  y = %d" % (f.state_pt[0], f.state_pt[1])
        img.drawText(text, pos[0], pos[1], color, size)

    def correctX(self):
        """
        **SUMMARY**

        Returns a numpy array of the corrected x coordinate of each feature.

        **RETURNS**

        A numpy array.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.correctX()

        """
        return np.array([f.state_pt[0] for f in self])

    def correctY(self):
        """
        **SUMMARY**

        Returns a numpy array of the corrected y coordinate of each feature.

        **RETURNS**

        A numpy array.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.correctY()

        """
        return np.array([f.state_pt[1] for f in self])

    def correctedCoordinates(self):
        """
        **SUMMARY**

        Returns a numpy array of the corrected coordinates of each feature.

        **RETURNS**

        A numpy array.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.predictedCoordinates()

        """
        return np.array([f.state_pt for f in self])

    def drawCorrectedPath(self, color=Color.GREEN, thickness=2):
        """
        **SUMMARY**

        Draw the complete corrected path of the center of the object on current frame

        **PARAMETERS**

        * *color* - The color to draw the object. Either an BGR tuple or a member of the :py:class:`Color` class.
        * *thickness* - Thickness of the tracing path.

        **RETURNS**

        Nada. Nothing. Zilch.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... ts.drawCorrectedPath() # For continuous tracing
            ... img = img1
        >>> ts.drawPredictedPath() # draw the path at the end of tracking
        """

        ts = self
        img = self[-1].image
        for i in range(len(ts)-1):
            img.drawLine((ts[i].state_pt),(ts[i+1].state_pt), color=color, thickness=thickness)
