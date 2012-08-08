from SimpleCV.base import *
from SimpleCV.ImageClass import *
from SimpleCV.Features.Features import Feature, FeatureSet


class Tracking(Feature):
    """
    **SUMMARY**
 
    Tracking class is the base of tracking. All different tracking algorithm
    return different classes but they all belong to Tracking class. All the 
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
        
        SimpleCV.Features.Tracking.Tracking object
        
        **EXAMPLE**
        
        >>> track = Tracking(image, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
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

        >>> track = Tracking(img, bb)
        >>> track.drawCorrected()
        >>> img.show()
        """
        f = self
        f.image.drawCircle(f.state_pt, rad, color, thickness)

class CAMShift(Tracking):
    """
    **SUMMARY**
    
    CAMShift Class is returned by track when CAMShift tracking is required.
    This class is a superset of Tracking Class. And all of Tracking class'
    attributes can be accessed.
    
    CAMShift class has "ellipse" attribute which is not present in Tracking
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
        
        SimpleCV.Features.Tracking.CAMShift object
        
        **EXAMPLE**
        
        >>> track = CAMShift(image, bb, ellipse)
        """
        self = Tracking.__init__(self, img, bb)
        self.ellipse = ellipse

    def getEllipse(self):
        """
        **SUMMARY**
        
        Returns the ellipse.
        
        **RETURNS**
        
        A tuple
        
        **EXAMPLE**
        
        >>> track = CAMShift(image, bb, ellipse)
        >>> e = track.getEllipse()
        """
        return self.ellipse
