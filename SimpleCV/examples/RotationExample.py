#!/usr/bin/python 
from SimpleCV import *
from numpy import linspace 
from scipy.interpolate import UnivariateSpline
import sys, time, socket

#settings for the project)
srcImg  = "../sampleimages/orson_welles.jpg"
input = Image(srcImg)
input.save("RotSource.png")

rot  = input.rotate(45)
rot.save("r45.png")

rotS  = input.rotate(45,scale=0.5)
rotS.save("rs45.png")

rotST  = input.rotate(45,scale=0.5, point = (0,0) )
rotST.save("rst45.png")


rotF  = input.rotate(45, "full")
rotF.save("fr45.png")

rotFS  = input.rotate(45, "full", scale=0.5)
rotFS.save("frs45.png")

rotFST  = input.rotate(45, "full", scale=0.5, point = (0,0) )
rotFST.save("frst45.png")


#Now do affine transform
#we're going to use openCV to calculate our transform for now

img = Image(srcImg)

atrans = img.shear([(img.width/2,0),(img.width-1,img.height/2),(img.width/2,img.height-1)])
atrans.save("atrans.png")

#now do the perspective transform 
ptrans = img.warp([(img.width*0.05,img.height*0.03),(img.width*0.9,img.height*0.1),(img.width*0.8,img.height*0.7),(img.width*0.2,img.height*0.9)])
ptrans.save("ptrans.png")


