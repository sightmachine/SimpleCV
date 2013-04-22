	#!/usr/bin/python
'''
This example shows how to perform various DFT on images
and save the results.
'''

from DFT import *
from SimpleCV import Image

df = DFT()
img = Image("lenna.png", sample=True)

highpassfilter = df.highPassFilter(img,[0.2,0.1,0.2])
bandpassfilter = df.bandPassFilter(img,[0.2,0.2,0.05],[0.3,0.3,0.2])
logmagnitude = df.getDFTLogMagnitude(img)
butterworthfilter = df.applyButterworthFilter(img,dia=400,order=2,highpass=True,grayscale=False)
gaussianfilter = df.applyGaussianFilter(img,dia=400,highpass=True,grayscale=False)
unsharpmask = df.applyUnsharpMask(img,2,grayscale=False)

unsharpmask.save('UnsharpMast.png')
gaussianfilter.save('GaussianFilter.png')
butterworthfilter.save('ButterworthFilter.png')
logmagnitude.save('LogMagnitude.png')
highpassfilter.save('HighPassFilter.png')
bandpassfilter.save('BandPassFilter.png')
