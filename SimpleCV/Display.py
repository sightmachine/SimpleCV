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
          
        
    def writeFrame(self, img):
        """
        writeFrame copies the given Image object to the display, you can also use
        Image.save()
        """
        if img.size() != self.resolution:
            img = img.scale(self.resolution[0], self.resolution[1])
        s = img.getPGSurface()
        self.screen.blit(s, s.get_rect())
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

    def isDone(self):
        """
        Checks the event queue and returns True if a quit event has been issued
        """
        self.checkEvents()
        return self.done
      
