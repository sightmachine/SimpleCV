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
    _mFontColor = 0
    _mClearColor = 0
    _mFont = 0
    _mFontName = ""
    _mFontSize = 0

    def __init__(self, img):
        self._mClearColor = pg.Color(7,22,81,0)
        self._mSurface = pg.Surface((int(img.width),int(img.height)))
        self._mSurface.set_colorkey(self._mClearColor)
        self._mSurface.fill(self._mClearColor)
        self._mImage = img 
        self._mDefaultColor = Color.BLACK
        pg.init()
        if( not pg.font.get_init() ):
            pg.font.init()
        self._mFontSize = 18
        self._mFontName = None
        self._mFont = pg.font.Font(self._mFontName,self._mFontSize)    
     
    def setClearColor(self,color):
        self._mClearColor = pg.Color(color[2],color[1],color[0],0)
        return None
    
    def getClearColor(self):
        return( (self._mClearColor.r,self._mClearColor.g,self._mClearColor.b))

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
        retVal = pg.Color(color[2],color[1],color[0],255)
        return retVal
        
    def drawLine(self,start,stop, color=Color.DEFAULT, width=1, antialias=True ):
        start = self._scv2dToPg2d(start)
        stop = self._scv2dToPg2d(stop)
        if(antialias):           
            pg.draw.aaline(self._mSurface,self._csvRGB2pgColor(color),start,stop)
        else:
            pg.draw.line(self._mSurface,self._csvRGB2pgColor(color),start,stop,width)        
        return None
    
    def drawLines(self,points,color=Color.DEFAULT,width=1,antialias=True ):
        pts = map(self._scv2dToPg2d,points)
        if(antialias):
            pg.draw.aalines(self._mSurface,self._csvRGB2pgColor(color),0,pts)
        else:
            pg.draw.lines(self._mSurface,self._csvRGB2pgColor(color),0,pts)                
        return None
    
    #need two points(TR,BL), center+W+H, and TR+W+H
    def drawRectangle(self,rectangle,color=Color.DEFAULT,w=1, filled=False ):
        if(filled):
            w = 0
        pg.draw.rect(self._mSurface,self._csvRGB2pgColor(color),rectangle,width=w)
        return None
    
    def drawPolygon(self,points,color=Color.DEFAULT,w=1,filled=False,antialias=True):
        if(filled):
            w = 0
        pts = map(self._scv2dToPg2d,points)
        if(not filled):
            if(antialias):
                pg.draw.aalines(self._mSurface,self._csvRGB2pgColor(color),1,pts)
            else:
                pg.draw.lines(self._mSurface,self._csvRGB2pgColor(color),True,pts,width=w)
        else:
            pg.draw.polygon(self._mSurface,self._csvRGB2pgColor(color),pts)
        return None
    
    def drawCircle(self,center,radius,color=Color.DEFAULT,width=1,filled=False):
        if(filled):
            width = 0
        pg.draw.circle(self._mSurface,self._csvRGB2pgColor(color),center,radius,width)
        return None
    
    def drawEllipse(elf,rectangle,color=Color.DEFAULT,width=1, filled=False):
        if(filled):
            width = 0
        pg.draw.ellipse(self._mSurface,self._csvRGB2pgColor(color),rectangle,width)
        return None
        
    def setFontBold(self,doBold):
        self._mFont.set_bold(doBold)
        return None

    #def DrawElipse(bound_box,color=Color.DEFAULT,width=1,filled=False):
    #def InitFont(fontName, size=1,underline=False,bold=False,italic=False,color=Color.DEFAULT):

    def setFontItalic(self,doItalic):
        self._mFont.set_italic(doItalic)
        return None
    
    def setFontUnderline(self,doUnderline):
        self._mFont.set_underline(doUnderline)
        return None
    
    def selectFont(self,fontName):
        self._mFontName = fontName
        self._mFont = pg.font.Font(self._mFontName,self._mFontSize)
        return None
        
    def listFonts(self):
        return pg.font.get_fonts();
        return None
    
    def setFontSize(self,sz):
        self._mFontSize = sz
        self._mFont = pg.font.Font(self._mFontName,self._mFontSize)
        return None
    
    def writeText(self,text,location,color=Color.DEFAULT, antialias=True):
        tsurface = self._mFont.render(text,antialias,self._csvRGB2pgColor(color))
        self._mSurface.blit(tsurface,location)        
        return None        

    
    def writeEZViewText(self,text,location,fgcolor=Color.WHITE,bgcolor=Color.BLACK):
        tsurface = self._mFont.render(text,antialias,self._csvRGB2pgColor(fgcolor),background=self._csvRGB2pgColor(bgcolor))
        self._mSurface.blit(tsurface,location)        
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
        return self._mImage
    
    #plot 2D data on the image
    def plot(self,rect,data,color=Color.DEFAULT,show_axis=TRUE):
        return None
    
    #plot a histogram
    def drawHistogram(self,rect,data,color=Color.DEFAULT,show_axis=TRUE):
        return None
    
    #Replace the image in place - the layer is replaced if the image is not the same size    
    def replaceImage(self,img):
        if(img.width != self._mImage.width or img.height != self._mImage.height):
            warnings.warn("RenderEngine::replaceImage: It is okay to replace the image, but it must match the old image")
        else:
            self._mImage = img
        return None
    
    def replaceOverlay(self, overlay):
        self._mSurface = overlay
        return None
    
    #get rid of all drawing
    def clear(self):
        self._mSurface = pg.Surface((int(self._mImage.width),int(self._mImage.height)))
        return None
    
    #render the image. 
    def renderImage(self):
        imgSurf = self._image2Surface(self._mImage)
        imgSurf.blit(self._mSurface,(0,0))
        return self._surface2Image(imgSurf)