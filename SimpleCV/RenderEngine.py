#!/usr/bin/env python

import sys
import os
from SimpleCV import * 
try:
    import pygame
    from pygame import surfarray
    from pygame.locals import *
except ImportError:
    raise ImportError('Error Importing Pygame/surfarray')

class RenderEngine:
    """
    """
    _mSurface = []
    _mImage = []
    
    def __init__(self, img):
        self._mSurface = Surface(img.width,img.height)
        self._mImage = img
    
    def DrawLine(start,stop, color=Colors.Black, width=1, antialias=True ):
        return None
    
    def DrawPoints(points,color=Colors.Black,width=1,antialias=True ):
        return None
    
    def DrawRectangle(rectangle,color=Colors.Black,width=1, filled=False ):
        return None
    
    def DrawPolygon(points,color=Colors.Black,width=1,filled=False,antialias=True):
        return None
    
    def DrawCircle(center,radius,color=Colors.Black,width=1,filled=False):
        return None
    
    def DrawElipse(bound_box,color=Colors.Black,width=1,filled=False):
    
    def InitFont(fontName, size=1,underline=False,bold=False,italic=False,color=Colors.BLACK):

    def SetFontBold(doBold):

    def SetFontItalic(doItalic):

    def SetFontUnderline(doUnderline):

    def SetFontColor(color): # We need a default color

    def SetFontSize(sz):
    
    def WriteText(text,location,color=Colors.BLACK, antialias=True):
    
    #render text in a box so it is easy to read
    def WriteEZReadText(text,location,fgcolor=Colors.WHITE,bgcolor=Colors.BLACK, antialias=True)
    
    #set an alpha for the whole surface, give it a cool effect
    def SetRenderAlpha(alpha):
   
    #give the entire surface a color     
    def SetSurfaceBaseColor(color):
    
    def DrawSprite(img,pos=(0,0),scale=1.0,rot=0.0,alpha=1.0):
    
    #sprite overload
    def DrawWatermark():
        
    #capture time, color depth, path, etc
    def PrintStats():
    
    def GetSourceImage():
    
    #plot 2D data on the image
    def Plot(rect,data,color=Colors.BLACK,show_axis=TRUE):
    
    #plot a histogram
    def DrawHistogram(rect,data,color=Colors.BLACK,show_axis=TRUE):
    
    def RenderImage(): 