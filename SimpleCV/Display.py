from SimpleCV.base import *
import SimpleCV.ImageClass
import Queue
from base import *


PYGAME_INITIALIZED = False

class Display:
    """
    **SUMMARY**

    WindowStream opens a window (Pygame Display Surface) to which you can write
    images.  The default resolution is 640, 480 -- but you can also specify 0,0
    which will maximize the display.  Flags are pygame constants, including:


    By default display will attempt to scale the input image to fit neatly on the
    screen with minimal distorition. This means that if the aspect ratio matches
    the screen it will scale cleanly. If your image does not match the screen aspect
    ratio we will scale it to fit nicely while maintining its natural aspect ratio.

    Because SimpleCV performs this scaling there are two sets of input mouse coordinates,
    the (mousex,mousey) which scale to the image, and (mouseRawX, mouseRawY) which
    do are the actual screen coordinates. 

    * pygame.FULLSCREEN: create a fullscreen display.
    * pygame.DOUBLEBUF: recommended for HWSURFACE or OPENGL.
    * pygame.HWSURFACE: hardware accelerated, only in FULLSCREEN.
    * pygame.OPENGL: create an opengl renderable display.
    * pygame.RESIZABLE: display window should be sizeable.
    * pygame.NOFRAME: display window will have no border or controls.

    Display should be used in a while loop with the isDone() method, which
    checks events and sets the following internal state controls:

    * mouseX: the x position of the mouse cursor on the input image.
    * mouseY: the y position of the mouse curson on the input image.
    * mouseRawX: The position of the mouse on the screen.
    * mouseRawY: The position of the mouse on the screen.

    **NOTES**

    The mouse position on the screen is not the mouse position on the image. If you
    are trying to draw on the image or take in coordinates use mousex and mousey
    as these values are scaled along with the image.

    * mouseLeft: the state of the left button.
    * mouseRight: the state of the right button.
    * mouseMiddle: the state of the middle button.
    * mouseWheelUp: scroll wheel has been moved up.
    * mouseWheelDown: the wheel has been clicked towards the bottom of the mouse.
    
    **EXAMPLE**
    
    >>> display = Display(resolution = (800, 600)) #create a new display to draw images on
    >>> cam = Camera() #initialize the camera
    >>> done = False # setup boolean to stop the program
    >>> while not display.isDone():
    >>>  cam.getImage().flipHorizontal().save(display) # get image, flip it so it looks mirrored, save to display
    >>>  time.sleep(0.01) # Let the program sleep for 1 millisecond so the computer can do other things
    >>>  if display.mouseLeft:
    >>>      display.done = True

    """
    
    resolution = ''
    sourceresolution = ''
    sourceoffset = ''
    screen = ''
    eventhandler = ''
    mq = ''
    done = False
    mouseX = 0 # These are the scaled mouse values. If you want to do image manipulation use these. 
    mouseY = 0
    mouseRawX = 0 # Raw x and y are the actual position on the screen
    mouseRawY = 0 # versus the position on the image. 
    mouseLeft = 0
    mouseMiddle = 0
    mouseRight = 0
    mouseWheelUp = 0
    mouseWheelDown = 0
    xscale = 1.0
    yscale = 1.0
    xoffset = 0
    yoffset = 0
    imgw = 0
    imgh = 0
    lastLeftButton = 0
    lastRightButton = 0
    leftButtonDown = None
    leftButtonUp = None
    rightButtonDown = None
    rightButtonUp = None
    displaytype = None

    def __repr__(self):
        return "<SimpleCV.Display Object resolution:(%s), Image Resolution: (%d, %d) at memory location: (%s)>" % (self.resolution, self.imgw, self.imgh, hex(id(self)))
    
    def __init__(self, resolution = (640, 480), flags = 0, title = "SimpleCV", displaytype='standard', headless = False):
        """
        **SUMMARY**

        This is the generic display object.  You are able to set the display type.
        The standard display type will pop up a window
        The notebook display type is to be used in conjunction with IPython Notebooks
        this is so it is web based.  If you have IPython Notebooks installed
        you just need to start IPython Notebooks and open in your browser.

        **PARAMETERS**
        
        * *resolution* - the size of the diplay in pixels. 
        * *flags* - ???
        * *title* - the title bar on the display. 
        * *displaytype* - The type of display. Options are as follows:
        
          * 'standard' - A pygame window.
          * 'notebook' - Ipython Web Notebook output
       
        * *headless* - If False we ignore healess mode. If true all rendering is suspended. 

        **EXAMPLE**

        Once in IPython you can do the following:

        >>> from SimpleCV import *
        >>> disp = Display(displaytype='notebook')
        >>> img = Image('simplecv')
        >>> img.save(disp)
        
        """
        global PYGAME_INITIALIZED

        if headless:
          os.environ["SDL_VIDEODRIVER"] = "dummy"
        
        if not PYGAME_INITIALIZED:
            if not displaytype == 'notebook':
                pg.init()
            PYGAME_INITIALIZED = True
        self.xscale = 1.0
        self.yscale = 1.0
        self.xoffset = 0
        self.yoffset = 0
        self.lastLeftButton = 0
        self.lastRightButton = 0
        self.leftButtonDown = None
        self.leftButtonUp = None
        self.rightButtonDown = None
        self.rightButtonUp = None
        self.displaytype = displaytype

        self.mouseRawX = 0 # Raw x and y are the actual position on the screen
        self.mouseRawY = 0 # versus the position on the image. 
        self.resolution = resolution
        if not displaytype == 'notebook':
            self.screen = pg.display.set_mode(resolution, flags)
        scvLogo = SimpleCV.Image("simplecv").scale(32,32)
        pg.display.set_icon(scvLogo.getPGSurface())
        if flags != pg.FULLSCREEN and flags != pg.NOFRAME:
            pg.display.set_caption(title)
          
    def leftButtonUpPosition(self):
        """
        **SUMMARY**
        
        Returns the position where the left mouse button went up.

        .. warning::
          You must call :py:meth:`checkEvents` or :py:meth:`isDone` 
          in your main display loop for this method to work. 

        **RETURNS**
        
        An (x,y) mouse postion tuple where the mouse went up.
        
        **EXAMPLE**

        >>> disp = Display((600,800))
        >>> cam = Camera()
        >>> while(disp.isNotDone()):
        >>>   img = cam.getImage()
        >>>   dwn = disp.leftButtonDownPosition()
        >>>   up = disp.leftButtonUpPosition()
        >>>   if( up is not None and dwn is not None):
        >>>     bb = disp.pointsToBoundingBox(up,dwn)
        >>>     img.drawRectangle(bb[0],bb[1],bb[2],bb[3])
        >>>   img.save(disp)

        **SEE ALSO**

        :py:meth:`rightButtonUpPostion`
        :py:meth:`leftButtonDownPostion`
        :py:meth:`rightButtonDownPostion`
        :py:meth:`pointsToBoundingBox`

      
        """
        return self.leftButtonUp

    def leftButtonDownPosition(self):
        """
        **SUMMARY**
        
        Returns the position where the left mouse button went down.

        .. warning::
          You must call :py:meth:`checkEvents` or :py:meth:`isDone` 
          in your main display loop for this method to work. 


        **RETURNS**
        
        An (x,y) mouse postion tuple where the mouse went up.
        
        **EXAMPLE**
        
        >>> disp = Display((600,800))
        >>> cam = Camera()
        >>> while(disp.isNotDone()):
        >>>   img = cam.getImage()
        >>>   dwn = disp.leftButtonDownPosition()
        >>>   up = disp.leftButtonUpPosition()
        >>>   if( up is not None and dwn is not None):
        >>>     bb = disp.pointsToBoundingBox(up,dwn)
        >>>     img.drawRectangle(bb[0],bb[1],bb[2],bb[3])
        >>>   img.save(disp)

        **SEE ALSO**

        :py:meth:`leftButtonUpPostion`
        :py:meth:`rightButtonUpPostion`
        :py:meth:`rightButtonDownPostion`
        :py:meth:`pointsToBoundingBox`
        :py:meth:`checkEvents`

        
        """

        return self.leftButtonDown

    def rightButtonUpPosition(self):
        """
        **SUMMARY**
        
        Returns the position where the right mouse button went up.

        .. warning::
          You must call :py:meth:`checkEvents` or :py:meth:`isDone` 
          in your main display loop for this method to work. 


        **RETURNS**
        
        An (x,y) mouse postion tuple where the mouse went up.
        
        **EXAMPLE**
        
        >>> disp = Display((600,800))
        >>> cam = Camera()
        >>> while(disp.isNotDone()):
        >>>   img = cam.getImage()
        >>>   dwn = disp.rightButtonDownPosition()
        >>>   up = disp.rightButtonUpPosition()
        >>>   if( up is not None and dwn is not None):
        >>>     bb = disp.pointsToBoundingBox(up,dwn)
        >>>     img.drawRectangle(bb[0],bb[1],bb[2],bb[3])
        >>>   img.save(disp)


        >>> disp = Display((600,800))
        >>> dwn = disp.rightButtonDownPosition()
        >>> up = disp.rightButtonUpPosition()
        >>> bb = disp.pointsToBoundingBox(up,dwn)
        >>> #draw bb

        **SEE ALSO**

        :py:meth:`leftButtonUpPostion`
        :py:meth:`leftButtonDownPostion`
        :py:meth:`rightButtonDownPostion`
        :py:meth:`pointsToBoundingBox`
        :py:meth:`checkEvents`
        """
        return self.rightButtonUp

    def rightButtonDownPosition(self):
        """
        **SUMMARY**
        
        Returns the position where the right mouse button went down.

        .. warning::
          You must call :py:meth:`checkEvents` or :py:meth:`isDone` 
          in your main display loop for this method to work. 

        **RETURNS**
        
        An (x,y) mouse postion tuple where the mopuse went down.
        
        **EXAMPLE**

        >>> disp = Display((600,800))
        >>> cam = Camera()
        >>> while(disp.isNotDone()):
        >>>   img = cam.getImage()
        >>>   dwn = disp.rightButtonDownPosition()
        >>>   up = disp.rightButtonUpPosition()
        >>>   if( up is not None and dwn is not None):
        >>>     bb = disp.pointsToBoundingBox(up,dwn)
        >>>     img.drawRectangle(bb[0],bb[1],bb[2],bb[3])
        >>>   img.save(disp)

        **SEE ALSO**

        :py:meth:`leftButtonUpPostion`
        :py:meth:`leftButtonDownPostion`
        :py:meth:`rightButtonDownPostion`
        :py:meth:`pointsToBoundingBox`
        :py:meth:`checkEvents`
        """

        return self.rightButtonDown

    def pointsToBoundingBox(self, pt0, pt1):
        """
        **SUMMARY**

        Given two screen cooridnates return the bounding box in x,y,w,h format.         
        This is helpful for drawing regions on the display.

        **RETURNS**
        
        The bounding box from two coordinates as a ( x,y,w,h) tuple.
        
        **EXAMPLE**

        >>> disp = Display((600,800))
        >>> cam = Camera()
        >>> while(disp.isNotDone()):
        >>>   img = cam.getImage()
        >>>   dwn = disp.leftButtonDownPosition()
        >>>   up = disp.leftButtonUpPosition()
        >>>   if( up is not None and dwn is not None):
        >>>     bb = disp.pointsToBoundingBox(up,dwn)
        >>>     img.drawRectangle(bb[0],bb[1],bb[2],bb[3])
        >>>   img.save(disp)
        

        **SEE ALSO**

        :py:meth:`leftButtonUpPostion`
        :py:meth:`leftButtonDownPostion`
        :py:meth:`rightButtonDownPostion`
        :py:meth:`rightButtonUpPostion`
        :py:meth:`checkEvents`
        """
        xmax = np.max((pt0[0],pt1[0]))
        xmin = np.min((pt0[0],pt1[0]))
        ymax = np.max((pt0[1],pt1[1]))
        ymin = np.min((pt0[1],pt1[1]))
        return xmin,ymin,xmax-xmin,ymax-ymin

    def writeFrame(self, img, fit=True):
        """
        **SUMMARY**

        writeFrame copies the given Image object to the display, you can also use
        Image.save()
        
        Write frame trys to fit the image to the display with the minimum ammount
        of distortion possible. When fit=True write frame will decide how to scale
        the image such that the aspect ratio is maintained and the smallest amount
        of distorition possible is completed. This means the axis that has the minimum
        scaling needed will be shrunk or enlarged to match the display.        
        
        
        **PARAMETERS**
        
        * *img* -  the SimpleCV image to save to the display. 
        * *fit* - When fit=False write frame will crop and center the image as best it can.
          If the image is too big it is cropped and centered. If it is too small
          it is centered. If it is too big along one axis that axis is cropped and
          the other axis is centered if necessary.

        
        **RETURNS**
        
        Nothing.

        **EXAMPLE**
        
        >>> img = Image("lenna")
        >>> disp = Display((512,512))
        >>> disp.writeFrame(img)
        
 
        """
        # Grrrrr we're going to need to re-write this functionality
        # So if the image is the right size do nothing
        # if the image has a 'nice' scale factor we should scale it e.g. 800x600=>640x480
        # if( fit )
        #   if one axis is too big -> scale it down to fit
        #   if both axes are too big and they don't match eg 800x800 img and 640x480 screen => scale to 400x400 and center
        #   if both axis are too small -> scale the biggest to fill
        #   if one axis is too small and one axis is alright we center along the too small axis
        # else(!fit)
        #   if one / both axis is too big - crop it
        #   if one / both too small - center along axis
        #
        # this is getting a little long. Probably needs to be refactored. 
        wndwAR = float(self.resolution[0])/float(self.resolution[1])
        imgAR = float(img.width)/float(img.height)
        self.sourceresolution = img.size()
        self.sourceoffset = (0,0)
        self.imgw = img.width
        self.imgh = img.height
        self.xscale = 1.0
        self.yscale = 1.0
        self.xoffset = 0
        self.yoffset = 0
        if( img.size() == self.resolution): # we have to resize
            s = img.getPGSurface()
            self.screen.blit(s, s.get_rect())
            pg.display.flip() 
        elif( imgAR == wndwAR ):
            self.xscale = (float(img.width)/float(self.resolution[0]))
            self.yscale = (float(img.height)/float(self.resolution[1]))
            img = img.scale(self.resolution[0], self.resolution[1])
            s = img.getPGSurface()
            self.screen.blit(s, s.get_rect())
            pg.display.flip() 
        elif(fit):
            #scale factors 
            wscale = (float(img.width)/float(self.resolution[0]))
            hscale = (float(img.height)/float(self.resolution[1]))
            targetw = img.width
            targeth = img.height
            if(wscale>1): #we're shrinking what is the percent reduction
                wscale=1-(1.0/wscale)
            else: # we need to grow the image by a percentage
                wscale = 1.0-wscale

            if(hscale>1):
                hscale=1-(1.0/hscale)
            else:
                hscale=1.0-hscale

            if( wscale == 0 ): #if we can get away with not scaling do that
                targetx = 0
                targety = (self.resolution[1]-img.height)/2
                targetw = img.width
                targeth = img.height
                s = img.getPGSurface()
            elif( hscale == 0 ): #if we can get away with not scaling do that
                targetx = (self.resolution[0]-img.width)/2
                targety = 0
                targetw = img.width
                targeth = img.height
                s = img.getPGSurface()
            elif(wscale < hscale): # the width has less distortion
                sfactor = float(self.resolution[0])/float(img.width)
                targetw = int(float(img.width)*sfactor)
                targeth = int(float(img.height)*sfactor)
                if( targetw > self.resolution[0] or targeth > self.resolution[1]):
                    #aw shucks that still didn't work do the other way instead
                    sfactor = float(self.resolution[1])/float(img.height)
                    targetw = int(float(img.width)*sfactor)
                    targeth = int(float(img.height)*sfactor)
                    targetx = (self.resolution[0]-targetw)/2
                    targety = 0
                else:
                    targetx = 0
                    targety = (self.resolution[1]-targeth)/2
                img = img.scale(targetw,targeth)
                s = img.getPGSurface()
            else: #the height has more distortion
                sfactor = float(self.resolution[1])/float(img.height)
                targetw = int(float(img.width)*sfactor)
                targeth = int(float(img.height)*sfactor)
                if( targetw > self.resolution[0] or targeth > self.resolution[1]):
                    #aw shucks that still didn't work do the other way instead
                    sfactor = float(self.resolution[0])/float(img.width)
                    targetw = int(float(img.width)*sfactor)
                    targeth = int(float(img.height)*sfactor)
                    targetx = 0
                    targety = (self.resolution[1]-targeth)/2
                else:
                    targetx = (self.resolution[0]-targetw)/2
                    targety = 0
                img = img.scale(targetw,targeth)
                s = img.getPGSurface()
            #clear out the screen so everything is clean
            black = pg.Surface((self.resolution[0], self.resolution[1]))
            black.fill((0,0,0))
            self.screen.blit(black,black.get_rect())
            self.screen.blit(s,(targetx,targety))
            self.sourceoffset = (targetx, targety)
            pg.display.flip()
            self.xoffset = targetx
            self.yoffset = targety
            self.xscale = (float(self.imgw)/float(targetw))
            self.yscale = (float(self.imgh)/float(targeth))     
        else: # we're going to crop instead
            self.doClamp = False
            targetx = 0
            targety = 0
            cornerx = 0
            cornery = 0
            if(img.width <= self.resolution[0] and img.height <= self.resolution[1] ): # center a too small image 
                #we're too small just center the thing
                targetx = (self.resolution[0]/2)-(img.width/2)
                targety = (self.resolution[1]/2)-(img.height/2)
                cornerx = targetx
                cornery = targety
                s = img.getPGSurface()
            elif(img.width > self.resolution[0] and img.height > self.resolution[1]): #crop too big on both axes
                targetw = self.resolution[0]
                targeth = self.resolution[1]
                targetx = 0
                targety = 0
                x = (img.width-self.resolution[0])/2
                y = (img.height-self.resolution[1])/2
                cornerx = -1*x
                cornery = -1*y
                img = img.crop(x,y,targetw,targeth)
                s = img.getPGSurface()
            elif( img.width < self.resolution[0] and img.height >= self.resolution[1]): #height too big
                #crop along the y dimension and center along the x dimension
                targetw = img.width
                targeth = self.resolution[1]
                targetx = (self.resolution[0]-img.width)/2
                targety = 0
                x = 0
                y = (img.height-self.resolution[1])/2
                cornerx = targetx
                cornery = -1 * y
                img = img.crop(x,y,targetw,targeth)
                s = img.getPGSurface()
            elif( img.width > self.resolution[0] and img.height <= self.resolution[1]): #width too big
                #crop along the y dimension and center along the x dimension
                targetw = self.resolution[0]
                targeth = img.height
                targetx = 0
                targety = (self.resolution[1]-img.height)/2
                x = (img.width-self.resolution[0])/2
                y = 0
                cornerx = -1 * x
                cornery = targety
                img = img.crop(x,y,targetw,targeth)
                s = img.getPGSurface()
            self.xoffset = cornerx
            self.yoffset = cornery
            black = pg.Surface((self.resolution[0], self.resolution[1]))
            black.fill((0,0,0))
            self.screen.blit(black,black.get_rect())                    
            self.screen.blit(s,(targetx,targety))
            pg.display.flip()
                

      
    def _setButtonState(self, state, button):
        if button == 1:
            self.mouseLeft = state
        if button == 2:
            self.mouseMiddle = state
        if button == 3:
            self.mouseRight = state
        if button == 4:
            self.mouseWheelUp = 1
        if button == 5:
            self.mouseWheelDown = 1
      
    def checkEvents(self):
        """
        **SUMMARY**

        CheckEvents checks the pygame event queue and sets the internal display
        values based on any new generated events.
        
        .. warning:: 
          This method must be called (or :py:meth:`isDone` or :py:meth:`isNotDone`) to
          perform mouse event checking. 

        **RETURNS**

        Nothing.
        """
        self.mouseWheelUp = self.mouseWheelDown = 0
        self.lastLeftButton = self.mouseLeft
        self.lastRightButton = self.mouseRight
        self.leftButtonDown = None
        self.leftButtonUp = None
        self.rightButtonDown = None
        self.rightButtonUp = None

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                self.done = True
            if event.type == pg.MOUSEMOTION:
                self.mouseRawX = event.pos[0]
                self.mouseRawY = event.pos[1]
                x = int((event.pos[0]-self.xoffset)*self.xscale)
                y = int((event.pos[1]-self.yoffset)*self.yscale)
                (self.mouseX,self.mouseY) = self._clamp(x,y)
                self.mouseLeft, self.mouseMiddle, self.mouseRight = event.buttons
            if event.type == pg.MOUSEBUTTONUP:

                self._setButtonState(0, event.button)
                
            if event.type == pg.MOUSEBUTTONDOWN:
                self._setButtonState(1, event.button)

        pressed = pg.key.get_pressed()

        if( self.lastLeftButton == 0 and self.mouseLeft == 1 ):
            self.leftButtonDown = (self.mouseX,self.mouseY)
        if( self.lastLeftButton == 1 and self.mouseLeft == 0 ):
            self.leftButtonUp = (self.mouseX,self.mouseY)

        if( self.lastRightButton == 0 and self.mouseRight == 1 ):
            self.rightButtonDown = (self.mouseX,self.mouseY)
        if( self.lastRightButton == 1 and self.mouseRight == 0 ):
            self.rightButtonUp = (self.mouseX,self.mouseY)

        #If ESC pressed, end the display
        if(pressed[27] == 1):
            self.done = True
            
    def isDone(self):
        """
        **SUMMARY**

        Checks the event queue and returns True if a quit event has been issued.
        
        **RETURNS**
        
        True on a quit event, False otherwise.

        **EXAMPLE**
        
        >>> disp = Display()
        >>> cam = Camera()
        >>> while not disp.isDone():
        >>>   img = cam.getImage()
        >>>   img.save(disp)
       
        """
        self.checkEvents()
        return self.done

    def isNotDone(self):
        """
        **SUMMARY**

        Checks the event queue and returns False as long as the quit event hasn't been issued.

        **RETURNS**
        
        False on a quit event, True otherwise.

        **EXAMPLE**
        
        >>> disp = Display()
        >>> cam = Camera()
        >>> while disp.isNotDone():
        >>>   img = cam.getImage()
        >>>   img.save(disp)
       
        """
        return not self.isDone()
    
    def _clamp(self,x,y):
        """
        clamp all values between zero and the image width
        """
        rx = x
        ry = y
        if(x > self.imgw):
            rx = self.imgw
        if(x < 0 ):
            rx = 0
        
        if(y > self.imgh):
            ry = self.imgh
        if(y < 0 ):
            ry = 0   
        return (rx,ry)
        
    def quit(self):
        """
        quit the pygame instance

        Example:
        >>> img = Image("simplecv")
        >>> d = img.show()
        >>> time.sleep(5)
        >>> d.quit()
        """
        pg.display.quit()
        pg.quit()
