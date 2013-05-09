from SimpleCV import Image, Camera, Display
import pygame as pg
import cStringIO
from pylab import *
import numpy as np
from mpl_toolkits.mplot3d import axes3d
from matplotlib.backends.backend_agg import FigureCanvasAgg
import time as time
import cv2

bins = 8
#precompute
idxs = []
colors = []
offset = bins/2
skip = 255/bins
for x in range(0,bins):
    for y in range(0,bins):
        for z in range(0,bins):
            b = ((x*skip)+offset)/255.0
            g = ((y*skip)+offset)/255.0
            r = ((z*skip)+offset)/255.0
            idxs.append((x,y,z,(r,g,b)))



# plot points in 3D
cam = Camera(0)
disp = Display((800,600))
fig = figure()
canvas = FigureCanvasAgg(fig)
azim = 0
while disp.isNotDone():
    ax = fig.gca(projection='3d')
    ax.set_xlabel('BLUE', color=(0,0,1) )
    ax.set_ylabel('GREEN',color=(0,1,0))
    ax.set_zlabel('RED',color=(1,0,0))
    img = cam.getImage().scale(0.2)
    rgb = img.getNumpyCv2()
    hist = cv2.calcHist([rgb],[0,1,2],None,[bins,bins,bins],[0,256,0,256,0,256])
    hist = hist/np.max(hist)
    print hist.shape
    #[ ax.plot([x],[y],[z],'.',markersize=hist[x,y,z]*100,color=color) for x,y,z,color in idxs if(hist[x][y][z]>0) ]
    [ ax.plot([x],[y],[z],'.',color=color) for x,y,z,color in idxs if(hist[x][y][z]>0) ]
    ax.set_xlim3d(-1, bins)
    ax.set_ylim3d(-1, bins)
    ax.set_zlim3d(-1, bins)
    azim = (azim+0.25)%360
    ax.view_init(elev=35, azim=azim)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    
    surf = pg.image.fromstring(raw_data, size, "RGB")
    figure = Image(surf)
#    buf = cStringIO.StringIO()
#    canvas.print_png(buf)
    #data = buf.getvalue()
#    figure = Image(canvas.print_to_buffer())
#    fig.savefig('temp.png')
#    figure = Image('temp.png')
    result = figure.blit(img)
    result.save(disp)
    fig.clf()
