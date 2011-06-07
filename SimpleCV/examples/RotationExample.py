#!/usr/bin/python 
from SimpleCV import *
from numpy import linspace 
from scipy.interpolate import UnivariateSpline
import sys, time, socket

#settings for the project)
srcImg  = "../sampleimages/orson_welles.jpg"
input = Image(srcImg)
input.save("RotSource.png")

rot  = input.rotate_fixed(45)
rot.save("r45.png")

rotS  = input.rotate_fixed(45,scale=0.5)
rotS.save("rs45.png")

rotST  = input.rotate_fixed(45,scale=0.5, point = (0,0) )
rotST.save("rst45.png")


rotF  = input.rotate_full(45)
rotF.save("fr45.png")

rotFS  = input.rotate_full(45,scale=0.5)
rotFS.save("frs45.png")

rotFST  = input.rotate_full(45,scale=0.5, point = (0,0) )
rotFST.save("frst45.png")


#Now do affine transform
#we're going to use openCV to calculate our transform for now

img = Image(srcImg)

src =  ((0,0),(img.width-1,0),(img.width-1,img.height-1))
dst =  ((img.width/2,0),(img.width-1,img.height/2),(img.width/2,img.height-1))
aWarp = cv.CreateMat(2,3,cv.CV_32FC1)
cv.GetAffineTransform(src,dst,aWarp)
atrans = img.transform_affine(aWarp)
atrans.save("atrans.png")

#now do it again using a np.array (this is the same transform)
aWarp2 = np.array(aWarp)
atrans2 = img.transform_affine(aWarp2)
atrans2.save("atrans2.png")


#now do the perspective transform 
src = ((0,0),(img.width-1,0),(img.width-1,img.height-1),(0,img.height-1))
dst = ((img.width*0.05,img.height*0.03),(img.width*0.9,img.height*0.1),(img.width*0.8,img.height*0.7),(img.width*0.2,img.height*0.9))
pWarp = cv.CreateMat(3,3,cv.CV_32FC1)
cv.GetPerspectiveTransform(src,dst,pWarp)
ptrans = img.transform_perspective(pWarp)
ptrans.save("ptrans.png")

#do the same with an np array, 3x3
pWarp2 = np.array(pWarp)
#now do it again using a np.array (this is the same transform)
ptrans2 = img.transform_perspective(pWarp2)
ptrans2.save("ptrans2.png")


