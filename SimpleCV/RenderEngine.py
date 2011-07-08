#!/usr/bin/env python

import sys
import os
from SimpleCV.base import *
from SimpleCV.ImageClass import * 
from SimpleCV.Color import *
from SimpleCV import *
from numpy import int32
try:
    import pygame as pg
    
except ImportError:
    raise ImportError('Error Importing Pygame/surfarray')

class RenderEngine:
    """
    """
    _mSurface = []
    _mImage = []
    _mDefaultColor = 0
    _mBold = False
    _mUnderline = False
    _mItalic = False

    def __init__(self, img):
        self._mSurface = pg.Surface((int(img.width),int(img.height)))
        self._mSurface.set_colorkey(pg.Color(7,22,81,0))
        self._mSurface.fill(pg.Color(7,22,81,0))
        self._mImage = img
        self._mDefaultColor = Color.BLACK
        self._mBold = False
        self._mUnderline = False
        self._mItalic = False
        pg.init()
        
    def _surface2Image(self,surface):
        imgarray = pg.surfarray.array3d(surface)
        #imgarray = np.transpose(imgarray)
        retVal = Image(imgarray)
        return retVal.toBGR().rotate90()

    
    def _image2Surface(self,img):
        return pg.surfarray.make_surface(img.toRGB().getNumpy())
    
    #coordiante conversion
    def _scvXYToPg2d(self,x,y):
        return (y,x)
        
    def _scv2dToPg2d(self,point):
        return([point[1],point[0]])
        
    def _csvRGB2pgColor(self,color):
        if(color==Color.DEFAULT):
            color=self._mDefaultColor
        return pg.Color(color[0],color[1],color[2],255)
        
    def drawLine(self,start,stop, color=Color.DEFAULT, width=1, antialias=True ):
        start = self._scv2dToPg2d(start)
        stop = self._scv2dToPg2d(stop)
 
        if(antialias):           
            pg.draw.aaline(self._mSurface,self._csvRGB2pgColor(color),start,stop)
        else:
            pg.draw.line(self._mSurface,self._csvRGB2pgColor(color),start,stop,width)        
        return None
    
    def drawPoints(self,points,color=Color.DEFAULT,width=1,antialias=True ):
        return None
    
    def drawRectangle(self,rectangle,color=Color.DEFAULT,width=1, filled=False ):
        return None
    
    def drawPolygon(self,points,color=Color.DEFAULT,width=1,filled=False,antialias=True):
        return None
    
    def drawCircle(self,center,radius,color=Color.DEFAULT,width=1,filled=False):
        return None
    
    def setFontBold(self,doBold):
        return None

    #def DrawElipse(bound_box,color=Color.DEFAULT,width=1,filled=False):
    #def InitFont(fontName, size=1,underline=False,bold=False,italic=False,color=Color.DEFAULT):

    def setFontItalic(self,doItalic):
        return None
    
    def setFontUnderline(self,doUnderline):
        return None
    
    def setFontColor(self,color): # We need a default color
        return None
    
    def setFontSize(self,sz):
        return None
    
    def writeText(self,text,location,color=Color.DEFAULT, antialias=True):
        return None
    
    #render text in a box so it is easy to read
    #def writeEZReadText(self,text,location,fgcolor=Color.WHITE,bgcolor=Color.BLACK,antialias=True)
    #    return None
    
    #set an alpha for the whole surface, give it a cool effect
    def setRenderAlpha(self,alpha):
        return None
    
    #give the entire surface a color     
    def setSurfaceBaseColor(self,color):
        return None
    
    def drawSprite(self,img,pos=(0,0),scale=1.0,rot=0.0,alpha=1.0):
        return None
    #sprite overload
    
    def drawWatermark(self):
        return None
        
    #capture time, color depth, path, etc
    def printStats(self):
        return None
    
    def getSourceImage(self):
        return None
    
    #plot 2D data on the image
    def plot(self,rect,data,color=Color.DEFAULT,show_axis=TRUE):
        return None
    
    #plot a histogram
    def drawHistogram(self,rect,data,color=Color.DEFAULT,show_axis=TRUE):
        return None
    
    #Replace the image in place - the layer is replaced if the image is not the same size    
    def replaceImage(self,img):
        return None
    
    def replaceOverlay(self, overlay):
        return None
    
    #get rid of all drawing
    def clear(self):
        return None
    
    #render the image. 
    def renderImage(self):
        imgSurf = self._image2Surface(self._mImage)
        imgSurf.blit(self._mSurface,(0,0))
        return self._surface2Image(imgSurf)