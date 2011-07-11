import time, threading
from SimpleCV.base import *
import SimpleCV.ImageClass
try:
  import pygame as pg
  pg.init()
  
except ImportError:
  raise ImportError('Error Importing Pygame/surfarray')

class DisplayEventHandler(threading.Thread):
  """
  Helper class for the display -- make sure we can quit out 
  """
  events = ""
  
  def run():
    events = ()
    while True:
      time.sleep(0.01)
      for event in pg.event.get():
        if event.type == pg.QUIT: sys.exit()


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
   
  """
  screen = ''
  eventhandler = ''
  
  def __init__(self, resolution = (640, 480), flags = 0, title = "SimpleCV", Threaded = True):
    self.screen = pg.display.set_mode(resolution, flags)
    if flags != pg.FULLSCREEN and flags != pg.NOFRAME:
      pg.display.set_caption(title)
      
    if Threaded:
      self.eventhandler = DisplayEventHandler()
      self.eventhandler.daemon = True
      self.eventhandler.start()
      time.sleep(0)
    
  def writeFrame(self, img):
    surface = pg.surfarray.make_surface(img.getNumpy())
    self.screen.blit(surface, surface.get_rect())
    pg.display.flip()
    
  def addEvent(self, eventCondition, eventHandlerFunction):
    self.eventhandler.events.append(eventCondition, eventHandlerFunction)
    