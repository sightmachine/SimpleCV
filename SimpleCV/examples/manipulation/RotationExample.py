#!/usr/bin/python 
from SimpleCV import *
from numpy import linspace 
from scipy.interpolate import UnivariateSpline
import sys, time, socket

#settings for the project)
srcImg  = "../../sampleimages/orson_welles.jpg"
font_size = 20
sleep_for = 3 #seconds to sleep for
draw_color = Color.RED


while True:
    image = Image(srcImg)
    image.drawText("Original Size", 10,10, color=draw_color, fontsize=font_size)
    image.show()
    time.sleep(sleep_for)
    
    rot = image.rotate(45)
    rot.drawText("Rotated 45 degrees", 10,10, color=draw_color, fontsize=font_size)
    rot.show()
    time.sleep(sleep_for)
    
    rot = image.rotate(45, scale=0.5)
    rot.drawText("Rotated 45 degrees and scaled", 10,10, color=draw_color, fontsize=font_size)
    rot.show()
    time.sleep(sleep_for)
    
    rot = image.rotate(45,scale=0.5, point = (0,0) )
    rot.drawText("Rotated 45 degrees and scaled around a point", 10,10, color=draw_color, fontsize=font_size)
    rot.show()
    time.sleep(sleep_for)

    rot = image.rotate(45,"full")
    rot.drawText("Rotated 45 degrees and full", 10,10, color=draw_color, fontsize=font_size)
    rot.show()
    time.sleep(sleep_for)
    
    atrans = image.shear([(image.width/2,0),(image.width-1,image.height/2),(image.width/2,image.height-1)])
    atrans.drawText("Affine Transformation", 10,10, color=draw_color, fontsize=font_size)
    atrans.show()
    time.sleep(sleep_for)

    ptrans = image.warp([(image.width*0.05,image.height*0.03),(image.width*0.9,image.height*0.1),(image.width*0.8,image.height*0.7),(image.width*0.2,image.height*0.9)])
    ptrans.drawText("Perspective Transformation", 10,10, color=draw_color, fontsize=font_size)
    ptrans.show()
    time.sleep(sleep_for)
    

