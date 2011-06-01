#!/usr/bin/python 
from SimpleCV import *
from numpy import linspace 
from scipy.interpolate import UnivariateSpline
import sys, time, socket

#settings for the project
srcImg  = "../sampleimages/barcode.png"     #Path for output files
input = Image(srcImg)
input.save("MorphSource.png")
erode = input.erode(3)
erode.save("Erode.png")
dilate = input.dilate(3)
dilate.save("Dilate.png")
open = input.morphOpen()
open.save("Open.png")
close = input.morphClose()
close.save("Close.png")
grad = input.morphGradient()
grad.save("Gradient.png")
