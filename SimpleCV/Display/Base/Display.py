from abc import ABCMeta,abstractmethod,abstractproperty

#good ol flags, I think only these would be valid for all platforms
DEFAULT = 0
FULLSCREEN = 1

#Display size doesn't change, come what may !
FIXED = 2 

#what to do with a bigger image when display size is fixed
RESIZE = 0
SCROLL = 1

class DisplayNotFoundException(Exception):
    def __init__(self,display):
        self.display = display
    def __str__(self):
        return "I'm Sorry to say this but uhhhh' !! The display at %d was closed, choose a different one" % id(self.display)


class DisplayBase:
    
    __metaclass__ = ABCMeta
    
    #TODO add text for adjusting image size to fit
    """
    **SUMMARY**
    
    The Base class for all Displays in SimpleCV. Inheriting classes 
    
    All coordinates specified or returned are a (x,y) tuple . The top left is
    (0,0) with Left -> Right and Up -> Down being positive
    
    **NOTES**
    
    While inheriting , ensure that the original doc string is prepended to the 
    inherited methods docstring wherever necessary
    
    **EXAMPLE**
    
    >>> display = Display(type_ = FULLSCREEN)
    >>> image = Image('lenna')
    >>> image.save(display)
    
    """
    
    #The last display initialized, to be used for img.show()
    screen = None
    
    #A short string that should indicate the type of dislay
    @abstractmethod
    def name():
        """
        **SUMMARY**
        Returns a description of the display
        
        **REUTRNS**
        A string.
        
        """
        pass
    
    @abstractmethod
    def __init__(self,size ,type_ ,title ,fit):
        """
        **SUMMARY**
        
        Opens up a display in a window. 
        
        d = Display(type_ = FULLSCREEN,fit = SCROLL)
        
        **PARAMETERS**
        
        * *size* - the size of the diplay in pixels.
        
        * *type_* - Control how the diplay behaves, either FULSCREEN,FIXED or 
            DEFAULT ( by default ).FIXED keeps the display size as intialized.
            FULLSCREEN makes the display fullscreened. 
            
        * *title* - the title bar on the display, if there exists onw.
        
        * *fit* - How to display the image if the image and display size does 
            not match. Either SCROLL or RESIZE. SCROLL adds scroll bars
            to the display. RESIZE, resizes the image to fit the display
        
        
        **EXAMPLE**
        
        >>> display = Display(type_ = FULLSCREEN,fit = SCROLL)
        >>> img = Image('lenna')
        >>> img.save(dispay)
        
        """
        
        screen = self
        self.size = size
        self.type_ = type_
        self.fit = fit
        self.imgSize = None
        self.xScale = 1.0
        self.yScale = 1.0
        self.image = None
        
    
    def __repr__(self):
        return "<SimpleCV %s resolution:(%s), at memory location: (%s)>" % (self.name(),self.size, hex(id(self)))
    
    
    @abstractproperty
    def mousePosition(self):
        """
        **SUMMARY**
        
        Reutrns the mouse pointer potion as a tuple of (x,y), with respect to
        the image coordinates

        **RETURNS**
        
        An (x,y) mouse postion tuple .
        
        """
        pass
        
    @abstractproperty
    def mousePositionRaw(self):
        """
        **SUMMARY**
        
        Reutrns the mouse pointer potion as a tuple of (x,y), with respect to
        the display coordinates
        
        **RETURNS**
        
        An (x,y) mouse postion tuple .
        
        """
        pass

    @abstractmethod
    def leftDown(self):
        """
        **SUMMARY**
        
        Reutrns the position where the left mouse button last went down,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the left mouse button went down.
        
        """

    @abstractmethod
    def leftUp(self):
        """
        **SUMMARY**
        
        Reutrns the position where the left mouse button last went up,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the left mouse button went up.
        
        """

    @abstractmethod
    def rightDown(self):
        """
        **SUMMARY**
        
        Reutrns the position where the right mouse button last went down,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the right mouse button went down.
        
        """
        
    @abstractmethod
    def rightUp(self):
        """
        **SUMMARY**
        
        Reutrns the position where the right mouse button last went up,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the right mouse button went up.
        
        """
        
    @abstractmethod
    def middleDown(self):
        """
        **SUMMARY**
        
        Reutrns the position where the middle mouse button last went down,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the middle mouse button went down.
        
        """
        
    @abstractmethod
    def middleUp(self):
        """
        **SUMMARY**
        
        Reutrns the position where the middle mouse button last went up,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the middle mouse button went up.
        
        """
        
    @abstractmethod
    def showImage(self, image):
        """
        **SUMMARY**
        
        Shows the Image given on the Display. This method may raise a 
        DisplayNotFoundException if the display desired was closed
        
        **PARAMETERS**
        
        * *image* -  the SimpleCV image to save to the display.
        
        **RETURNS**
        
        Nothing.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> disp = Display((512,512))
        >>> disp.showImage(img)
        """
        
        self.image = img
        
    @abstractmethod
    def close(self):
        """
        **SUMMARY**
        
        Closes the display window
        
        **RETURNS**
        
        Nothing.
        
        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> disp = Display((512,512))
        >>> disp.showImage(img)
        >>> disp.close()
        """
        if(screen == self):
            screen = None

