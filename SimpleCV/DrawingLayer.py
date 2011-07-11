#!/usr/bin/env python

import sys
import os
from SimpleCV.base import *
from SimpleCV.ImageClass import * 
from SimpleCV.Color import *
from SimpleCV import *
from numpy import int32
from numpy import uint8
try:
    import pygame as pg
    
#DOCS
#TESTS
#IMAGE AGNOSTIC
#RESIZE
#ADD IMAGE INTERFACE

except ImportError:
    raise ImportError('Error Importing Pygame/surfarray')

class DrawingLayer:
    """
    """
    _mSurface = []
    _mDefaultColor = 0
    _mFontColor = 0
    _mClearColor = 0
    _mFont = 0
    _mFontName = ""
    _mFontSize = 0
    _mDefaultAlpha = 255

    def __init__(self,(width,height)):
        pg.init()
        if( not pg.font.get_init() ):
            pg.font.init()
        self._mSurface = pg.Surface((width,height),flags=pg.SRCALPHA)
        self._mDefaultAlpha = 255
        #self._mSurface.set_alpha(128)
        self._mClearColor = pg.Color(0,0,0,0)
        
        self._mSurface.fill(self._mClearColor)
        self._mDefaultColor = Color.BLACK

        self._mFontSize = 18
        self._mFontName = None
        self._mFont = pg.font.Font(self._mFontName,self._mFontSize)    
     
    def setDefaultAlpha(self,alpha):
        if(alpha >= 0 and alpha <= 255 ):
            self._mDefaultAlpha = alpha 
        return None
    
    def getDefaultAlpha(self):
        return self._mDefaultAlpha

    def setLayerAlpha(self,alpha):
        self._mSurface.set_alpha(alpha)
        return None
    
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
        
    def _csvRGB2pgColor(self,color,alpha=-1):
        if(alpha==-1):
            alpha = self._mDefaultAlpha
        if(color==Color.DEFAULT):
            color=self._mDefaultColor
        retVal = pg.Color(color[2],color[1],color[0],alpha)
        print(retVal)
        return retVal
        
    def line(self,start,stop, color=Color.DEFAULT, width=1, antialias=True,alpha=-1 ):
        start = self._scv2dToPg2d(start)
        stop = self._scv2dToPg2d(stop)
        if(antialias):           
            pg.draw.aaline(self._mSurface,self._csvRGB2pgColor(color,alpha),start,stop)
        else:
            pg.draw.line(self._mSurface,self._csvRGB2pgColor(color,alpha),start,stop,width)        
        return None
    
    def lines(self,points,color=Color.DEFAULT,width=1,antialias=True,alpha=-1 ):
        pts = map(self._scv2dToPg2d,points)
        if(antialias):
            pg.draw.aalines(self._mSurface,self._csvRGB2pgColor(color,alpha),0,pts)
        else:
            pg.draw.lines(self._mSurface,self._csvRGB2pgColor(color,alpha),0,pts)                
        return None
    
    #need two points(TR,BL), center+W+H, and TR+W+H
    def rectangle(self,topleft,delta,color=Color.DEFAULT,w=1, filled=False, alpha=-1 ):
        if(filled):
            w = 0
        tl = self._scv2dToPg2d(topLeft)
        dt = self._scv2dToPg2d(delta)
        r = pg.Rect(tl[0],tl[1],delta[0],delta[1])
        pg.draw.rect(self._mSurface,self._csvRGB2pgColor(color,alpha),r,width=w)
        return None
    
    def centerRectangle(self,center,dimensions,color=Color.DEFAULT,w=1, filled=False, alpha=-1 ):
        if(filled):
            w = 0
        c = self._scv2dToPg2d(center)
        d = self._scv2dToPg2d(dimensions)
        xtl = c[0]-(d[0]/2)
        ytl = c[1]-(d[1]/2)
        r = pg.Rect(xtl,ytl,delta[0],delta[1])
        pg.draw.rect(self._mSurface,self._csvRGB2pgColor(color,alpha),r,width=w)
        return None    
    
    
    def polygon(self,points,color=Color.DEFAULT,filled=False,antialias=True,alpha=-1):
        if(filled):
            w = 0
        pts = map(self._scv2dToPg2d,points)
        if(not filled):
            if(antialias):
                pg.draw.aalines(self._mSurface,self._csvRGB2pgColor(color,alpha),True,pts)
            else:
                pg.draw.lines(self._mSurface,self._csvRGB2pgColor(color,alpha),True,pts)
        else:
            pg.draw.polygon(self._mSurface,self._csvRGB2pgColor(color,alpha),pts)
        return None
    
    def circle(self,center,radius,color=Color.DEFAULT,width=1,filled=False,antialias=True,alpha=-1):
        if(filled):
            width = 0
        temp = self._scv2dToPg2d(center)
        if(antialias and not filled ):
            pg.gfxdraw.circle(self._mSurface, temp[0],temp[1],radius,self._csvRGB2pgColor(color,alpha))
        else:
            pg.draw.circle(self._mSurface,self._csvRGB2pgColor(color,alpha),center,radius,width)
        return None
    
    def ellipse(self,center,deltas,color=Color.DEFAULT,width=1, filled=False, antialias=True,alpha=-1):
        if(filled):
            width = 0
        ctemp = self._scv2dToPg2(center)
        dtemp = self._scv2dToPg2(deltas)
        if(antialias and not filled):
            pg.gfxdraw.aaellispe(self._mSurface,ctemp[0],ctemp[1],dtemp[0],dtemp[1],self._csvRGB2pgColor(color,alpha) )
        else:
            r = pg.Rect(ctemp[0],ctemp[1],dtemp[0],dtemp[1])
            pg.draw.ellipse(self._mSurface,self._csvRGB2pgColor(color,alpha),r,width)
        return None
    
    def bezier(self,points,steps,color=Color.DEFAULT,alpha=-1):
        pts = self._scv2dToPg2(points)
        pg.gfxdraw.bezier(self._mSurface,pts,steps,self._csvRGB2pgColor(color,alpha))
        return None
        
    def setFontBold(self,doBold):
        self._mFont.set_bold(doBold)
        return None

    def setFontItalic(self,doItalic):
        self._mFont.set_italic(doItalic)
        return None
    
    def setFontUnderline(self,doUnderline):
        self._mFont.set_underline(doUnderline)
        return None
    
    def selectFont(self,fontName):
        fullName = pg.font.match_font(fontName)
        self._mFontName = fullName
        self._mFont = pg.font.Font(self._mFontName,self._mFontSize)
        return None
        
    def listFonts(self):
        return pg.font.get_fonts();
        return None
    
    def setFontSize(self,sz):
        self._mFontSize = sz
        self._mFont = pg.font.Font(self._mFontName,self._mFontSize)
        return None
    
    def text(self,text,location,color=Color.DEFAULT, antialias=True,alpha=-1):
        tsurface = self._mFont.render(text,antialias,self._csvRGB2pgColor(color,alpha))
        if(alpha==-1):
            alpha = self._mDefaultAlpha
        #this is going to be slow, dumb no native support.
        #see http://www.mail-archive.com/pygame-users@seul.org/msg04323.html
        # Get access to the alpha band of the image.
        pixels_alpha = pg.surfarray.pixels_alpha(tsurface)
        # Do a floating point multiply, by alpha 100, on each alpha value.
        # Then truncate the values (convert to integer) and copy back into the surface.
        pixels_alpha[...] = (pixels_alpha * (alpha / 255.0)).astype(np.uint8)
        # Unlock the surface.
        del pixels_alpha
        self._mSurface.blit(tsurface,location)        
        return None        

    
    def ezViewText(self,text,location,fgcolor=Color.WHITE,bgcolor=Color.BLACK,alpha=-1):
        tsurface = self._mFont.render(text,antialias,self._csvRGB2pgColor(fgcolor,alpha),background=self._csvRGB2pgColor(bgcolor,alpha))
        if(alpha==-1):
            alpha = self._mDefaultAlpha
        #this is going to be slow, dumb no native support.
        #see http://www.mail-archive.com/pygame-users@seul.org/msg04323.html
        # Get access to the alpha band of the image.
        pixels_alpha = pg.surfarray.pixels_alpha(tsurface)
        # Do a floating point multiply, by alpha 100, on each alpha value.
        # Then truncate the values (convert to integer) and copy back into the surface.
        pixels_alpha[...] = (pixels_alpha * (alpha / 255.0)).astype(np.uint8)
        # Unlock the surface.
        del pixels_alpha
        self._mSurface.blit(tsurface,location)        
        return None
    
    def sprite(self,img,pos=(0,0),scale=1.0,rot=0.0,alpha=1.0):
        return None
    #sprite overload
    
    def watermark(self):
        return None
        
    #capture time, color depth, path, etc
    def printStats(self):
        return None
    
    #plot 2D data on the image
    def plot(self,rect,data,color=Color.DEFAULT,show_axis=TRUE):
        return None
    
    #plot a histogram
    def histogram(self,rect,data,color=Color.DEFAULT,show_axis=TRUE):
        return None
        
    def replaceOverlay(self, overlay):
        self._mSurface = overlay
        return None
    
    #get rid of all drawing
    def clear(self):
        self._mSurface = pg.Surface((int(self._mImage.width),int(self._mImage.height)))
        return None
    
    #render the image. 
    def renderImage(self, img):
        imgSurf = self._image2Surface(img)
        imgSurf.blit(self._mSurface,(0,0))
        return self._surface2Image(imgSurf)