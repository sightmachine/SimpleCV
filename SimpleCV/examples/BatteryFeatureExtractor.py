#!/usr/bin/python 
import os
import glob
from SimpleCV import *
from numpy import *

def BuildWidthHistogram( img, bins ):
    raw_vals = []
    for i in range(0,img.width):
        scanline = img.getHorzScanlineGray(i)
        points = np.where(scanline==255)
        if( points[0].shape[0] > 2 ):
            w = points[0][-1]-points[0][0] 
            raw_vals.append(w)
            
    return raw_vals #np.histogram(raw_vals,bins)
        
def ExtractFeatures( fname, outbase ):
    img = Image(fname)
    img = img.medianFilter()
    blobs = img.binarizeAdaptive()
    blobs = blobs.invert()
    blobs = blobs.dilate(1)
    edges = img.edges()
    edges = edges.dilate()
    mult = edges*blobs
    mult = mult.dilate()
    chunks = mult.findBlobs()
    x = (chunks[0].cvblob.maxx - chunks[0].cvblob.minx)/2
    y = (chunks[0].cvblob.maxy - chunks[0].cvblob.miny)/2
    angle = 90-chunks[0].angle()
    mult = mult.rotate(-1*angle,point=(x,y))
    chunks = mult.findBlobs()
    w = (chunks[0].cvblob.maxx - chunks[0].cvblob.minx)
    h = (chunks[0].cvblob.maxy - chunks[0].cvblob.miny)
    cx = chunks[0].cvblob.minx+(w/2)
    cy = chunks[0].cvblob.miny+(h/2)
    mult = mult.crop(cx,cy,int(w+(w/5)),int(h+(h/10)),centered=True)
    mult = mult.erode()
    mult.save(outfile)
    return BuildWidthHistogram( mult, 10 )
    
path = '../sampleimages/battery/good/'
i = 0
for infile in glob.glob( os.path.join(path, '*.jpg') ):
    print "Opening File: " + infile
    outfile = 'Result' + str(i) + ".png"
    hist = ExtractFeatures(infile, outfile)
    outfile = 'Result' + str(i) + ".txt"
    savetxt(outfile,hist)#hist[0])
    i = i+1

