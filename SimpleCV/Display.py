import time, threading
from SimpleCV.base import *
import SimpleCV.ImageClass
import Queue
import pygame as pg

pg.init()


class Display:
    """
    WindowStream opens a window (Pygame Display Surface) to which you can write
    images.  The default resolution is 640, 480 -- but you can also specify 0,0
    which will maximize the display.  Flags are pygame constants, including:
  
    pygame.FULLSCREEN    create a fullscreen display
    pygame.DOUBLEBUF     recommended for HWSURFACE or OPENGL
    pygame.HWSURFACE     hardware accelerated, only in FULLSCREEN
    pygame.OPENGL        create an opengl renderable display
    pygame.RESIZABLE     display window should be sizeable
    pygame.NOFRAME       display window will have no border or controls
   
    Display should be used in a while loop with the isDone() method, which
    checks events and sets the following internal state controls:
  
    mouseX - the x position of the mouse cursor
    mouseY - the y position of the mouse curson
    mouseLeft - the state of the left button
    mouseRight - the state of the right button
    mouseMiddle - the state of the middle button
    mouseWheelUp - if the wheel has been clicked towards the top of the mouse
    mouseWheelDown - if the wheel has been clicked towards the bottom of the mouse



    Example:
    display = Display(resolution = (800, 600)) #create a new display to draw images on
    cam = Camera() #initialize the camera
    done = False # setup boolean to stop the program
    
    # Loop until not needed
    while not display.isDone():
        cam.getImage().flipHorizontal().save(display) # get image, flip it so it looks mirrored, save to display
        time.sleep(0.01) # Let the program sleep for 1 millisecond so the computer can do other things
        if display.mouseLeft:
            display.done = True
 
    """
    resolution = ''
    screen = ''
    eventhandler = ''
    mq = ''
    done = False
    mouseX = 0
    mouseY = 0
    mouseLeft = 0
    mouseMiddle = 0
    mouseRight = 0
    mouseWheelUp = 0
    mouseWheelDown = 0
    
    def __init__(self, resolution = (640, 480), flags = 0, title = "SimpleCV"):
        self.resolution = resolution
        self.screen = pg.display.set_mode(resolution, flags)
        if flags != pg.FULLSCREEN and flags != pg.NOFRAME:
            pg.display.set_caption(title)
          
        
    def writeFrame(self, img, fit=True):
        """
        writeFrame copies the given Image object to the display, you can also use
        Image.save()
        
        Write frame trys to fit the image to the display with the minimum ammount
        of distortion possible. When fit=True write frame will decide how to scale
        the image such that the aspect ratio is maintained and the smallest amount
        of distorition possible is completed. This means the axis that has the minimum
        scaling needed will be shrunk or enlarged to match the display.
        
        
        When fit=False write frame will crop and center the image as best it can.
        If the image is too big it is cropped and centered. If it is too small
        it is centered. If it is too big along one axis that axis is cropped and
        the other axis is centered if necessary.
 
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
        wndwAR = float(self.resolution[0])/float(self.resolution[1])
        imgAR = float(img.width)/float(img.height)
        if( img.size() == self.resolution): # we have to resize
            s = img.getPGSurface()
            self.screen.blit(s, s.get_rect())
            pg.display.flip() 
        elif( imgAR == wndwAR ):
            img = img.scale(self.resolution[0], self.resolution[1])
            s = img.getPGSurface()
            self.screen.blit(s, s.get_rect())
            pg.display.flip() 
        elif(fit):
            #scale factors 
            wscale = (float(img.width)/float(self.resolution[0]))
            hscale = (float(img.height)/float(self.resolution[1]))
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
                s = img.getPGSurface()
            elif( hscale == 0 ): #if we can get away with not scaling do that
                targetx = (self.resolution[0]-img.width)/2
                targety = 0
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
            pg.display.flip() 
        else: # we're going to crop instead
            targetx = 0
            targety = 0
            if(img.width <= self.resolution[0] and img.height <= self.resolution[1] ): # center a too small image 
                #we're too small just center the thing
                targetx = (self.resolution[0]/2)-(img.width/2)
                targety = (self.resolution[1]/2)-(img.height/2)
                s = img.getPGSurface()
            elif(img.width > self.resolution[0] and img.height > self.resolution[1]): #crop too big on both axes
                targetw = self.resolution[0]
                targeth = self.resolution[1]
                targetx = 0
                targety = 0
                x = (img.width-self.resolution[0])/2
                y = (img.height-self.resolution[1])/2
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
                img = img.crop(x,y,targetw,targeth)
                s = img.getPGSurface()
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
        checkEvents checks the pygame event queue and sets the internal display
        values based on any new generated events
        """
        self.mouseWheelUp = self.mouseWheelDown = 0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                self.done = True
            if event.type == pg.MOUSEMOTION:
                self.mouseX = event.pos[0]
                self.mouseY = event.pos[1]
                self.mouseLeft, self.mouseMiddle, self.mouseRight = event.buttons
            if event.type == pg.MOUSEBUTTONUP:
                self._setButtonState(0, event.button)
            if event.type == pg.MOUSEBUTTONDOWN:
                self._setButtonState(1, event.button)

            pressed = pg.key.get_pressed()
            #If ESC pressed, end the display
            if(pressed[27] == 1):
                self.done = True
            
    def isDone(self):
        """
        Checks the event queue and returns True if a quit event has been issued
        """
        self.checkEvents()
        return self.done
      
