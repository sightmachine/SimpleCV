#!/usr/bin/python
'''
This example shows how to create different DFT Filters and 
images apply them to multiple images.
'''
from ImageClass import DFTFilter
from SimpleCV import *

#Both images must be of same dimensions for same filter to work!!

img = Image("LyleJune1973.png", sample = True)
image = Image("lenna.png", sample = True)
df = DFTFilter()
lpf = df.createLowPassFilter(img.width,img.height,[0.2,0.1,0.2])
hpf = df.createHighPassFilter(img.width,img.height,[0.2,0.2,0.05])
bpf = df.createBandPassFilter(img.width,img.height,[0.2,0.2,0.05],[0.3,0.3,0.2])
bwf = df.createButterworthFilter(img.width,img.height, dia=400,order=2,highpass=True,grayscale=False)
gf = df.createGaussianFilter(img.width,img.height,dia=400,highpass=True,grayscale=False)
um1 = df.applyUnsharpMask(img,2,grayscale=False) 
um2 = df.applyUnsharpMask(image,2,grayscale=False) 

lpf1 = img.applyDFTFilter(lpf)
lpf2 = image.applyDFTFilter(lpf)
hpf1 = img.applyDFTFilter(hpf)
hpf2 = image.applyDFTFilter(hpf)
bpf1 = img.applyDFTFilter(bpf)
bpf2 = image.applyDFTFilter(bpf)
bwf1 = img.applyDFTFilter(bwf)
bwf2 = image.applyDFTFilter(bwf)
gf1 = img.applyDFTFilter(gf)
gf2 = image.applyDFTFilter(gf)

lpf1.save('lpf1.png')
lpf2.save('lpf2.png')
hpf1.save('hpf1.png')
hpf1.save('hpf2.png')
bpf1.save('bpf1.png')
bpf2.save('bpf2.png')
bwf1.save('bwf1.png')
bwf2.save('bwf2.png')
gf1.save('gf1.png')
gf2.save('gf2.png')
um1.save('um1.png')
um2.save('um2.png')

