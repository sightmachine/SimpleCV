from SimpleCV import Image, Camera, Display, Color
import pygame as pg
import numpy as np
from pylab import *
from mpl_toolkits.mplot3d import axes3d
from matplotlib.backends.backend_agg import FigureCanvasAgg
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
cam = Camera()
disp = Display((800,600))
fig = figure()
fig.set_size_inches( (10,7) )

canvas = FigureCanvasAgg(fig)
azim = 0
while disp.isNotDone():
    ax = fig.gca(projection='3d')
    ax.set_xlabel('BLUE', color=(0,0,1) )
    ax.set_ylabel('GREEN',color=(0,1,0))
    ax.set_zlabel('RED',color=(1,0,0))
    # Get the color histogram
    img = cam.getImage().scale(0.3)
    rgb = img.getNumpyCv2()
    hist = cv2.calcHist([rgb],[0,1,2],None,[bins,bins,bins],[0,256,0,256,0,256])
    hist = hist/np.max(hist)
    # render everything
    [ ax.plot([x],[y],[z],'.',markersize=max(hist[x,y,z]*100,6),color=color) for x,y,z,color in idxs if(hist[x][y][z]>0) ]
    #[ ax.plot([x],[y],[z],'.',color=color) for x,y,z,color in idxs if(hist[x][y][z]>0) ]
    ax.set_xlim3d(0, bins-1)
    ax.set_ylim3d(0, bins-1)
    ax.set_zlim3d(0, bins-1)
    azim = (azim+0.5)%360
    ax.view_init(elev=35, azim=azim)
    ########### convert matplotlib to  SimpleCV image
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()    
    surf = pg.image.fromstring(raw_data, size, "RGB")
    figure = Image(surf)
    ############ All done
    figure = figure.floodFill((0,0), tolerance=5,color=Color.WHITE)
    result = figure.blit(img, pos=(20,20))
    result.save(disp)
    fig.clf()
