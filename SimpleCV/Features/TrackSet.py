from SimpleCV.base import *
from SimpleCV.Color import *
from SimpleCV.Features.Features import Feature, FeatureSet

class TrackSet(FeatureSet):
    """
    **SUMMARY**

    TrackSet is a class extended from FeatureSet which is a class 
    extended from Python's list which has special functions so that 
    it is useful for handling feature metadata on an image.
    
    In general, functions dealing with attributes will return 
    numpy arrays.
    
    This class is specifically made for Tracking.
    
    **EXAMPLE**

    >>> image = Image("/path/to/image.png")
    >>> ts = image.track("camshift", img1=image, bb)  #ts is the track set
    >>> ts.draw()
    >>> ts.x()
    """
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
        f.z = float(ts[-1].area)/float(ts[0].area)
        f.vel = self.__pixelVelocity()
        f.rt_vel = self.__pixleVelocityRealTime()
    
    def z(self):
        """
        **SUMMARY**

        Returns a numpy array of the z coordinate of each feature.
        where z is the ratio of the size of the current bounding box to
        the size of the initial bounding box

        **RETURNS**
        
        A numpy array.

        **EXAMPLE**

        >>> while True:
            ... img1 = cam.getImage()
            ... ts = img1.track("camshift", ts1, img, bb)
            ... img = img1
        >>> print ts.z
        
        """
        return np.array([f.z for f in self])
    
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
    
    def trackImages(self):
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
        ts = self
        imgset = []
        for f in ts:
            imgset.append(f.image)
        return imgset
        
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
        ts = self
        bbset = []
        for f in ts:
            bbset.append(f.bb)
        return bbset
        
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

        Shoe the co-ordinates of the object in text on the current frame.

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
        
    def showZ(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Shoe the "z" co-ordinates of the object in text on the current frame.

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
        text = "z = %f" % (f.z)
        img.drawText(text, pos[0], pos[1], color, size)
    
    def showPixelVelocity(self, pos=None, color=Color.GREEN, size=None):
        """
        **SUMMARY**

        Shoe the Pixel Veloctiy (pixel/frame) of the object in text on the current frame.

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

        Shoe the Pixel Veloctiy (pixels/second) of the object in text on the current frame.

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
