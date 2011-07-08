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
    _mDefaultColor = Colors.BLACK
    _mBold = False
    _mUnderline = False
    _mItalic = False
    _m
    def __init__(self, img):
        self._mSurface = Surface(img.width,img.height)
        self._mImage = img
    
    def DrawLine(self,start,stop, color=Colors.DEFAULT, width=1, antialias=True ):
        return None
    
    def DrawPoints(self,points,color=Colors.DEFAULT,width=1,antialias=True ):
        return None
    
    def DrawRectangle(self,rectangle,color=Colors.DEFAULT,width=1, filled=False ):
        return None
    
    def DrawPolygon(self,points,color=Colors.DEFAULT,width=1,filled=False,antialias=True):
        return None
    
    def DrawCircle(self,center,radius,color=Colors.DEFAULT,width=1,filled=False):
        return None
    
    def SetFontBold(self,doBold):
        return None

    #def DrawElipse(bound_box,color=Colors.DEFAULT,width=1,filled=False):
    #def InitFont(fontName, size=1,underline=False,bold=False,italic=False,color=Colors.DEFAULT):

    def SetFontItalic(self,doItalic):
        return None
    def SetFontUnderline(self,doUnderline):
        return None
    
    def SetFontColor(self,color): # We need a default color
        return None
    
    def SetFontSize(self,sz):
        return None
    
    def WriteText(self,text,location,color=Colors.DEFAULT, antialias=True):
        return None
    
    #render text in a box so it is easy to read
    def WriteEZReadText(self,text,location,fgcolor=Colors.WHITE,bgcolor=Colors.DEFAULT, antialias=True)
        return None
    
    #set an alpha for the whole surface, give it a cool effect
    def SetRenderAlpha(self,alpha):
        return None
    #give the entire surface a color     
    def SetSurfaceBaseColor(self,color):
        return None
    
    def DrawSprite(self,img,pos=(0,0),scale=1.0,rot=0.0,alpha=1.0):
        return None
    #sprite overload
    def DrawWatermark(self):
        return None
        
    #capture time, color depth, path, etc
    def PrintStats(self):
        return None
    
    def GetSourceImage(self):
        return None
    
    #plot 2D data on the image
    def Plot(self,rect,data,color=Colors.DEFAULT,show_axis=TRUE):
        return None
    
    #plot a histogram
    def DrawHistogram(self,rect,data,color=Colors.DEFAULT,show_axis=TRUE):
        return None
    
    #Replace the image in place - the layer is replaced if the image is not the same size    
    def ReplaceImage(self,img):
        return None
    
    def ReplaceOverlay(self, overlay):
        return None
    
    #get rid of all drawing
    def Clear(self):
        return None
    
    #render the image. 
    def RenderImage(self,alpha):
        return None