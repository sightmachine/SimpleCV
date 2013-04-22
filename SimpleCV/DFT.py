#Load required libraries
from SimpleCV import Image
from SimpleCV.base import *
from SimpleCV.Color import *

from numpy import int32
from numpy import uint8

from EXIF import *

import scipy.ndimage as ndimage
import scipy.stats.stats as sss  #for auto white balance
import scipy.cluster.vq as scv
import scipy.linalg as nla  # for linear algebra / least squares
import math # math... who does that
import copy

class DFT():
	
	width = 0
	height = 0
	depth = 0
	_DFT = []
    	
	def _doDFT(self,inimg,grayscale = False):
		"""
		**SUMMARY**

		This private method peforms the discrete Fourier transform on an input image.
		The transform can be applied to a single channel gray image or to each channel of the
		image. Each channel generates a 64F 2 channel IPL image corresponding to the real
		and imaginary components of the DFT. A list of these IPL images are then cached
		in the private member variable _DFT.


		**PARAMETERS**
		
		* *inimg* - Image to do DFT on.
		* *grayscale* - If grayscale is True we first covert the image to grayscale, otherwise
		  we perform the operation on each channel.

		**RETURNS**

		nothing - but creates a locally cached list of IPL imgaes corresponding to the real
		and imaginary components of each channel.

		**EXAMPLE**

		>>> img = Image('logo.png')
		>>> df = DFT()
		>>> df._doDFT(img)
		>>> df._DFT[0] # get the b channel Re/Im components

		**NOTES**

		http://en.wikipedia.org/wiki/Discrete_Fourier_transform
		http://math.stackexchange.com/questions/1002/fourier-transform-for-dummies

		**TO DO**

		This method really needs to convert the image to an optimal DFT size.
		http://opencv.itseez.com/modules/core/doc/operations_on_arrays.html#getoptimaldftsize

		"""
		
		if( grayscale and (len(self._DFT) == 0 or len(self._DFT) == 3)):
			self._DFT = []
			img = inimg._getGrayscaleBitmap()
			width, height = cv.GetSize(img)
			src = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 2)
			dst = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 2)
			data = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 1)
			blank = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 1)
			cv.ConvertScale(img,data,1.0)
			cv.Zero(blank)
			cv.Merge(data,blank,None,None,src)
			cv.Merge(data,blank,None,None,dst)
			cv.DFT(src, dst, cv.CV_DXT_FORWARD)
			self._DFT.append(dst)
		elif( not grayscale and (len(self._DFT) < 2 )):
			self._DFT = []
			r = inimg.getEmpty(1)
			g = inimg.getEmpty(1)
			b = inimg.getEmpty(1)
			cv.Split(inimg.getBitmap(),b,g,r,None)
			chans = [b,g,r]
			width = inimg.width
			height = inimg.height
			data = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 1)
			blank = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 1)
			src = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 2)
			for c in chans:
				dst = cv.CreateImage((width, height), cv.IPL_DEPTH_64F, 2)
				cv.ConvertScale(c,data,1.0)
				cv.Zero(blank)
				cv.Merge(data,blank,None,None,src)
				cv.Merge(data,blank,None,None,dst)
				cv.DFT(src, dst, cv.CV_DXT_FORWARD)
				self._DFT.append(dst)

	def rawDFTImage(self,inimg,grayscale = False):
		"""
		**SUMMARY**

		This method returns the **RAW** DFT transform of an image as a list of IPL Images.
		Each result image is a two channel 64f image where the first channel is the real
		component and the second channel is teh imaginary component. If the operation
		is performed on an RGB image and grayscale is False the result is a list of
		these images of the form [b,g,r].

		**PARAMETERS**

		* *inimg* - Image to do DFT on.
		* *grayscale* - If grayscale is True we first covert the image to grayscale, otherwise
		  we perform the operation on each channel.

		**RETURNS**

		A list of the DFT images (see above). Note that this is a shallow copy operation.

		**EXAMPLE**

		>>> img = Image('logo.png')
		>>> df = DFT()
		>>> myDFT = df.rawDFTImage(img)
		>>> for c in myDFT:
		>>>    #do some operation on the DFT

		**NOTES**

		http://en.wikipedia.org/wiki/Discrete_Fourier_transform
		http://math.stackexchange.com/questions/1002/fourier-transform-for-dummies

		**SEE ALSO**

		:py:meth:`rawDFTImage`
		:py:meth:`getDFTLogMagnitude`
		:py:meth:`applyDFTFilter`
		:py:meth:`highPassFilter`
		:py:meth:`lowPassFilter`
		:py:meth:`bandPassFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyButterworthFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyGaussianFilter`
		:py:meth:`applyUnsharpMask`

		"""
		inimg._doDFT(grayscale)
		return self._DFT
	
	def _getDFTClone(self,inimg,grayscale = False):
		"""
		**SUMMARY**

		This method works just like _doDFT but returns a deep copy
		of the resulting array which can be used in destructive operations.

		**PARAMETERS**

		* *inimg* - Image to do DFT on.
		* *grayscale* - If grayscale is True we first covert the image to grayscale, otherwise
		  we perform the operation on each channel.

		**RETURNS**

		A deep copy of the cached DFT real/imaginary image list.

		**EXAMPLE**

		>>> img = Image('logo.png')
		>>> df = DFT()
		>>> myDFT = df._getDFTClone(img)
		>>> SomeCVFunc(myDFT[0])

		**NOTES**

		http://en.wikipedia.org/wiki/Discrete_Fourier_transform
		http://math.stackexchange.com/questions/1002/fourier-transform-for-dummies

		**SEE ALSO**

		DFT._doDFT()

		"""
		self._doDFT(inimg,grayscale)
		retVal = []
		if(grayscale):
			gs = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_64F,2)
			cv.Copy(self._DFT[0],gs)
			retVal.append(gs)
		else:
			for img in self._DFT:
				temp = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_64F,2)
				cv.Copy(img,temp)
				retVal.append(temp)
		return retVal
		
	def getDFTLogMagnitude(self,inimg,grayscale = False):
		"""
		**SUMMARY**

		This method returns the log value of the magnitude image of the DFT transform. This
		method is helpful for examining and comparing the results of DFT transforms. The log
		component helps to "squish" the large floating point values into an image that can
		be rendered easily.

		In the image the low frequency components are in the corners of the image and the high
		frequency components are in the center of the image.

		**PARAMETERS**

		* *inimg* - Image to do DFT on.
		* *grayscale* - if grayscale is True we perform the magnitude operation of the grayscale
		  image otherwise we perform the operation on each channel.

		**RETURNS**

		Returns a SimpleCV image corresponding to the log magnitude of the input image.

		**EXAMPLE**

		>>> img = Image("RedDog2.jpg")
		>>> df = DFT()
		>>> df.getDFTLogMagnitude(img).show()
		>>> lpf = df.lowPassFilter(img,img.width/10.img.height/10)
		>>> df.getDFTLogMagnitude(img).show()

		**NOTES**

		* http://en.wikipedia.org/wiki/Discrete_Fourier_transform
		* http://math.stackexchange.com/questions/1002/fourier-transform-for-dummies

		**SEE ALSO**

		:py:meth:`rawDFTImage`
		:py:meth:`getDFTLogMagnitude`
		:py:meth:`applyDFTFilter`
		:py:meth:`highPassFilter`
		:py:meth:`lowPassFilter`
		:py:meth:`bandPassFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyButterworthFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyGaussianFilter`
		:py:meth:`applyUnsharpMask`


		"""
		dft = self._getDFTClone(inimg,grayscale)
		chans = []
		if( grayscale ):
			chans = [inimg.getEmpty(1)]
		else:
			chans = [inimg.getEmpty(1),inimg.getEmpty(1),inimg.getEmpty(1)]
		data = cv.CreateImage((inimg.width, inimg.height), cv.IPL_DEPTH_64F, 1)
		blank = cv.CreateImage((inimg.width, inimg.height), cv.IPL_DEPTH_64F, 1)

		for i in range(0,len(chans)):
			cv.Split(dft[i],data,blank,None,None)
			cv.Pow( data, data, 2.0)
			cv.Pow( blank, blank, 2.0)
			cv.Add( data, blank, data, None)
			cv.Pow( data, data, 0.5 )
			cv.AddS( data, cv.ScalarAll(1.0), data, None ) # 1 + Mag
			cv.Log( data, data ) # log(1 + Mag
			min, max, pt1, pt2 = cv.MinMaxLoc(data)
			cv.Scale(data, data, 1.0/(max-min), 1.0*(-min)/(max-min))
			cv.Mul(data,data,data,255.0)
			cv.Convert(data,chans[i])

		retVal = None
		if( grayscale ):
			retVal = Image(chans[0])
		else:
			retVal = inimg.getEmpty()
			cv.Merge(chans[0],chans[1],chans[2],None,retVal)
			retVal = Image(retVal)
		return retVal
	
	def _boundsFromPercentage(self, floatVal, bound):
		return np.clip(int(floatVal*(bound/2.00)),0,(bound/2))
	
	def _inverseDFT(self,input):
		w = input[0].width
		h = input[0].height
		if( len(input) == 1 ):
			cv.DFT(input[0], input[0], cv.CV_DXT_INV_SCALE)
			result = cv.CreateImage((w,h), cv.IPL_DEPTH_8U, 1)
			data = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
			blank = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
			cv.Split(input[0],data,blank,None,None)
			min, max, pt1, pt2 = cv.MinMaxLoc(data)
			denom = max-min
			if(denom == 0):
				denom = 1
			cv.Scale(data, data, 1.0/(denom), 1.0*(-min)/(denom))
			cv.Mul(data,data,data,255.0)
			cv.Convert(data,result)
			retVal = Image(result)
		else: # DO RGB separately
			results = []
			data = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
			blank = cv.CreateImage((w,h), cv.IPL_DEPTH_64F, 1)
			for i in range(0,len(input)):
				cv.DFT(input[i], input[i], cv.CV_DXT_INV_SCALE)
				result = cv.CreateImage((w,h), cv.IPL_DEPTH_8U, 1)
				cv.Split( input[i],data,blank,None,None)
				min, max, pt1, pt2 = cv.MinMaxLoc(data)
				denom = max-min
				if(denom == 0):
					denom = 1
				cv.Scale(data, data, 1.0/(denom), 1.0*(-min)/(denom))
				cv.Mul(data,data,data,255.0) # this may not be right
				cv.Convert(data,result)
				results.append(result)

			retVal = cv.CreateImage((w,h),cv.IPL_DEPTH_8U,3)
			cv.Merge(results[0],results[1],results[2],None,retVal)
			retVal = Image(retVal)
		del input
		return retVal
	
	def applyDFTFilter(self, inimg, flt, grayscale=False):
		"""
		**SUMMARY**

		This function allows you to apply an arbitrary filter to the DFT of an image.
		This filter takes in a gray scale image, whiter values are kept and black values
		are rejected. In the DFT image, the lower frequency values are in the corners
		of the image, while the higher frequency components are in the center. For example,
		a low pass filter has white squares in the corners and is black everywhere else.

		**PARAMETERS**

		* *inimg* - Image to do DFT on.
		* *grayscale* - if this value is True we perfrom the operation on the DFT of the gray
		  version of the image and the result is gray image. If grayscale is true
		  we perform the operation on each channel and the recombine them to create
		  the result.

		* *flt* - A grayscale filter image. The size of the filter must match the size of
		  the image.

		**RETURNS**

		A SimpleCV image after applying the filter.

		**EXAMPLE**

		>>>  filter = Image("MyFilter.png")
		>>>  myImage = Image("MyImage.png")
		>>>  df = DFT()
		>>>  result = df.applyDFTFilter(myImage,filter)
		>>>  result.show()

		**SEE ALSO**

		:py:meth:`rawDFTImage`
		:py:meth:`getDFTLogMagnitude`
		:py:meth:`applyDFTFilter`
		:py:meth:`highPassFilter`
		:py:meth:`lowPassFilter`
		:py:meth:`bandPassFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyButterworthFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyGaussianFilter`
		:py:meth:`applyUnsharpMask`

		**TODO**

		Make this function support a separate filter image for each channel.
		"""
		if( flt.width != inimg.width and
			flt.height != inimg.height ):
			logger.warning("Image.applyDFTFilter - Your filter must match the size of the image")
		dft = []
		if( grayscale ):
			dft = self._getDFTClone(inimg,grayscale)
			flt = flt._getGrayscaleBitmap()
			flt64f = cv.CreateImage((flt.width,flt.height),cv.IPL_DEPTH_64F,1)
			cv.ConvertScale(flt,flt64f,1.0)
			finalFilt = cv.CreateImage((flt.width,flt.height),cv.IPL_DEPTH_64F,2)
			cv.Merge(flt64f,flt64f,None,None,finalFilt)
			for d in dft:
				cv.MulSpectrums(d,finalFilt,d,0)
		else: #break down the filter and then do each channel
			dft = self._getDFTClone(inimg,grayscale)
			flt = flt.getBitmap()
			b = cv.CreateImage((flt.width,flt.height),cv.IPL_DEPTH_8U,1)
			g = cv.CreateImage((flt.width,flt.height),cv.IPL_DEPTH_8U,1)
			r = cv.CreateImage((flt.width,flt.height),cv.IPL_DEPTH_8U,1)
			cv.Split(flt,b,g,r,None)
			chans = [b,g,r]
			for c in range(0,len(chans)):
				flt64f = cv.CreateImage((chans[c].width,chans[c].height),cv.IPL_DEPTH_64F,1)
				cv.ConvertScale(chans[c],flt64f,1.0)
				finalFilt = cv.CreateImage((chans[c].width,chans[c].height),cv.IPL_DEPTH_64F,2)
				cv.Merge(flt64f,flt64f,None,None,finalFilt)
				cv.MulSpectrums(dft[c],finalFilt,dft[c],0)
	
		return self._inverseDFT(dft)
		
		
	def highPassFilter(self, inimg, xCutoff,yCutoff=None,grayscale=False):
		"""
		**SUMMARY**

		This method applies a high pass DFT filter. This filter enhances
		the high frequencies and removes the low frequency signals. This has
		the effect of enhancing edges. The frequencies are defined as going between
		0.00 and 1.00 and where 0 is the lowest frequency in the image and 1.0 is
		the highest possible frequencies. Each of the frequencies are defined
		with respect to the horizontal and vertical signal. This filter
		isn't perfect and has a harsh cutoff that causes ringing artifacts.

		**PARAMETERS**

		* *inimg* - Image to do DFT on.
		* *xCutoff* - The horizontal frequency at which we perform the cutoff. A separate
		  frequency can be used for the b,g, and r signals by providing a
		  list of values. The frequency is defined between zero to one,
		  where zero is constant component and 1 is the highest possible
		  frequency in the image.

		* *yCutoff* - The cutoff frequencies in the y direction. If none are provided
		  we use the same values as provided for x.

		* *grayscale* - if this value is True we perfrom the operation on the DFT of the gray
		  version of the image and the result is gray image. If grayscale is true
		  we perform the operation on each channel and the recombine them to create
		  the result.

		**RETURNS**

		A SimpleCV Image after applying the filter.

		**EXAMPLE**

		>>> img = Image("SimpleCV/sampleimages/RedDog2.jpg")
		>>> df = DFT()
		>>> df.getDFTLogMagnitude(img).show()
		>>> hpf = df.highPassFilter(img,[0.2,0.1,0.2])
		>>> hpf.show()
		>>> df.getDFTLogMagnitude(hpf).show()

		**NOTES**

		This filter is far from perfect and will generate a lot of ringing artifacts.
		* See: http://en.wikipedia.org/wiki/Ringing_(signal)
		* See: http://en.wikipedia.org/wiki/High-pass_filter#Image

		**SEE ALSO**

		:py:meth:`rawDFTImage`
		:py:meth:`getDFTLogMagnitude`
		:py:meth:`applyDFTFilter`
		:py:meth:`highPassFilter`
		:py:meth:`lowPassFilter`
		:py:meth:`bandPassFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyButterworthFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyGaussianFilter`
		:py:meth:`applyUnsharpMask`

		"""
		if( isinstance(xCutoff,float) ):
			xCutoff = [xCutoff,xCutoff,xCutoff]
		if( isinstance(yCutoff,float) ):
			yCutoff = [yCutoff,yCutoff,yCutoff]
		if(yCutoff is None):
			yCutoff = [xCutoff[0],xCutoff[1],xCutoff[2]]

		for i in range(0,len(xCutoff)):
			xCutoff[i] = self._boundsFromPercentage(xCutoff[i],inimg.width)
			yCutoff[i] = self._boundsFromPercentage(yCutoff[i],inimg.height)

		filter = None
		h  = inimg.height
		w  = inimg.width

		if( grayscale ):
			filter = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			cv.Zero(filter)
			cv.AddS(filter,255,filter) # make everything white
			#now make all of the corners black
			cv.Rectangle(filter,(0,0),(xCutoff[0],yCutoff[0]),(0,0,0),thickness=-1) #TL
			cv.Rectangle(filter,(0,h-yCutoff[0]),(xCutoff[0],h),(0,0,0),thickness=-1) #BL
			cv.Rectangle(filter,(w-xCutoff[0],0),(w,yCutoff[0]),(0,0,0),thickness=-1) #TR
			cv.Rectangle(filter,(w-xCutoff[0],h-yCutoff[0]),(w,h),(0,0,0),thickness=-1) #BR

		else:
			#I need to look into CVMERGE/SPLIT... really need to know
			# how much memory we're allocating here
			filterB = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			filterG = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			filterR = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			cv.Zero(filterB)
			cv.Zero(filterG)
			cv.Zero(filterR)
			cv.AddS(filterB,255,filterB) # make everything white
			cv.AddS(filterG,255,filterG) # make everything whit
			cv.AddS(filterR,255,filterR) # make everything white
			#now make all of the corners black
			temp = [filterB,filterG,filterR]
			i = 0
			for f in temp:
				cv.Rectangle(f,(0,0),(xCutoff[i],yCutoff[i]),0,thickness=-1)
				cv.Rectangle(f,(0,h-yCutoff[i]),(xCutoff[i],h),0,thickness=-1)
				cv.Rectangle(f,(w-xCutoff[i],0),(w,yCutoff[i]),0,thickness=-1)
				cv.Rectangle(f,(w-xCutoff[i],h-yCutoff[i]),(w,h),0,thickness=-1)
				i = i+1

			filter = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,3)
			cv.Merge(filterB,filterG,filterR,None,filter)

		scvFilt = Image(filter)
		retVal = self.applyDFTFilter(inimg,scvFilt,grayscale)
		return retVal
	
	def lowPassFilter(self,inimg, xCutoff,yCutoff=None,grayscale=False):
		"""
		**SUMMARY**

		This method applies a low pass DFT filter. This filter enhances
		the low frequencies and removes the high frequency signals. This has
		the effect of reducing noise. The frequencies are defined as going between
		0.00 and 1.00 and where 0 is the lowest frequency in the image and 1.0 is
		the highest possible frequencies. Each of the frequencies are defined
		with respect to the horizontal and vertical signal. This filter
		isn't perfect and has a harsh cutoff that causes ringing artifacts.

		**PARAMETERS**

		* *inimg* - Image to do DFT on.
		* *xCutoff* - The horizontal frequency at which we perform the cutoff. A separate
		  frequency can be used for the b,g, and r signals by providing a
		  list of values. The frequency is defined between zero to one,
		  where zero is constant component and 1 is the highest possible
		  frequency in the image.

		* *yCutoff* - The cutoff frequencies in the y direction. If none are provided
		  we use the same values as provided for x.

		* *grayscale* - if this value is True we perfrom the operation on the DFT of the gray
		  version of the image and the result is gray image. If grayscale is true
		  we perform the operation on each channel and the recombine them to create
		  the result.

		**RETURNS**

		A SimpleCV Image after applying the filter.

		**EXAMPLE**

		>>> img = Image("SimpleCV/sampleimages/RedDog2.jpg")
		>>> df = DFT()
		>>> df.getDFTLogMagnitude(img).show()
		>>> lpf = df.lowPassFilter(img,[0.2,0.2,0.05])
		>>> lpf.show()
		>>> df.getDFTLogMagnitude(lpf).show()

		**NOTES**

		This filter is far from perfect and will generate a lot of ringing artifacts.
		See: http://en.wikipedia.org/wiki/Ringing_(signal)
		See: http://en.wikipedia.org/wiki/Low-pass_filter

		**SEE ALSO**

		:py:meth:`rawDFTImage`
		:py:meth:`getDFTLogMagnitude`
		:py:meth:`applyDFTFilter`
		:py:meth:`highPassFilter`
		:py:meth:`lowPassFilter`
		:py:meth:`bandPassFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyButterworthFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyGaussianFilter`
		:py:meth:`applyUnsharpMask`

		"""
		if( isinstance(xCutoff,float) ):
			xCutoff = [xCutoff,xCutoff,xCutoff]
		if( isinstance(yCutoff,float) ):
			yCutoff = [yCutoff,yCutoff,yCutoff]
		if(yCutoff is None):
			yCutoff = [xCutoff[0],xCutoff[1],xCutoff[2]]

		for i in range(0,len(xCutoff)):
			xCutoff[i] = self._boundsFromPercentage(xCutoff[i],inimg.width)
			yCutoff[i] = self._boundsFromPercentage(yCutoff[i],inimg.height)

		filter = None
		h  = inimg.height
		w  = inimg.width

		if( grayscale ):
			filter = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			cv.Zero(filter)
			#now make all of the corners black

			cv.Rectangle(filter,(0,0),(xCutoff[0],yCutoff[0]),255,thickness=-1) #TL
			cv.Rectangle(filter,(0,h-yCutoff[0]),(xCutoff[0],h),255,thickness=-1) #BL
			cv.Rectangle(filter,(w-xCutoff[0],0),(w,yCutoff[0]),255,thickness=-1) #TR
			cv.Rectangle(filter,(w-xCutoff[0],h-yCutoff[0]),(w,h),255,thickness=-1) #BR

		else:
			#I need to look into CVMERGE/SPLIT... really need to know
			# how much memory we're allocating here
			filterB = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			filterG = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			filterR = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			cv.Zero(filterB)
			cv.Zero(filterG)
			cv.Zero(filterR)
			#now make all of the corners black
			temp = [filterB,filterG,filterR]
			i = 0
			for f in temp:
				cv.Rectangle(f,(0,0),(xCutoff[i],yCutoff[i]),255,thickness=-1)
				cv.Rectangle(f,(0,h-yCutoff[i]),(xCutoff[i],h),255,thickness=-1)
				cv.Rectangle(f,(w-xCutoff[i],0),(w,yCutoff[i]),255,thickness=-1)
				cv.Rectangle(f,(w-xCutoff[i],h-yCutoff[i]),(w,h),255,thickness=-1)
				i = i+1

			filter = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,3)
			cv.Merge(filterB,filterG,filterR,None,filter)

		scvFilt = Image(filter)
		retVal = self.applyDFTFilter(inimg,scvFilt,grayscale)
		return retVal
	
	def bandPassFilter(self,inimg, xCutoffLow, xCutoffHigh, yCutoffLow=None, yCutoffHigh=None,grayscale=False):
		
		"""
		**SUMMARY**

		This method applies a simple band pass DFT filter. This filter enhances
		the a range of frequencies and removes all of the other frequencies. This allows
		a user to precisely select a set of signals to display . The frequencies are
		defined as going between
		0.00 and 1.00 and where 0 is the lowest frequency in the image and 1.0 is
		the highest possible frequencies. Each of the frequencies are defined
		with respect to the horizontal and vertical signal. This filter
		isn't perfect and has a harsh cutoff that causes ringing artifacts.

		**PARAMETERS**

		* *inimg* - Image to do DFT on.
		* *xCutoffLow*  - The horizontal frequency at which we perform the cutoff of the low
		  frequency signals. A separate
		  frequency can be used for the b,g, and r signals by providing a
		  list of values. The frequency is defined between zero to one,
		  where zero is constant component and 1 is the highest possible
		  frequency in the image.

		* *xCutoffHigh* - The horizontal frequency at which we perform the cutoff of the high
		  frequency signals. Our filter passes signals between xCutoffLow and
		  xCutoffHigh. A separate frequency can be used for the b, g, and r
		  channels by providing a
		  list of values. The frequency is defined between zero to one,
		  where zero is constant component and 1 is the highest possible
		  frequency in the image.

		* *yCutoffLow* - The low frequency cutoff in the y direction. If none
		  are provided we use the same values as provided for x.

		* *yCutoffHigh* - The high frequency cutoff in the y direction. If none
		  are provided we use the same values as provided for x.

		* *grayscale* - if this value is True we perfrom the operation on the DFT of the gray
		  version of the image and the result is gray image. If grayscale is true
		  we perform the operation on each channel and the recombine them to create
		  the result.

		**RETURNS**

		A SimpleCV Image after applying the filter.

		**EXAMPLE**

		>>> img = Image("SimpleCV/sampleimages/RedDog2.jpg")
		>>> df = DFT()
		>>> df.getDFTLogMagnitude(img).show()
		>>> bpf = df.bandPassFilter(img,[0.2,0.2,0.05],[0.3,0.3,0.2])
		>>> bpf.show()
		>>> df.getDFTLogMagnitude(bpf).show()

		**NOTES**

		This filter is far from perfect and will generate a lot of ringing artifacts.

		See: http://en.wikipedia.org/wiki/Ringing_(signal)

		**SEE ALSO**

		:py:meth:`rawDFTImage`
		:py:meth:`getDFTLogMagnitude`
		:py:meth:`applyDFTFilter`
		:py:meth:`highPassFilter`
		:py:meth:`lowPassFilter`
		:py:meth:`bandPassFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyButterworthFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyGaussianFilter`
		:py:meth:`applyUnsharpMask`

		"""
		if( isinstance(xCutoffLow,float) ):
			xCutoffLow = [xCutoffLow,xCutoffLow,xCutoffLow]
		if( isinstance(yCutoffLow,float) ):
			yCutoffLow = [yCutoffLow,yCutoffLow,yCutoffLow]
		if( isinstance(xCutoffHigh,float) ):
			xCutoffHigh = [xCutoffHigh,xCutoffHigh,xCutoffHigh]
		if( isinstance(yCutoffHigh,float) ):
			yCutoffHigh = [yCutoffHigh,yCutoffHigh,yCutoffHigh]

		if(yCutoffLow is None):
			yCutoffLow = [xCutoffLow[0],xCutoffLow[1],xCutoffLow[2]]
		if(yCutoffHigh is None):
			yCutoffHigh = [xCutoffHigh[0],xCutoffHigh[1],xCutoffHigh[2]]

		for i in range(0,len(xCutoffLow)):
			xCutoffLow[i] = self._boundsFromPercentage(xCutoffLow[i],inimg.width)
			xCutoffHigh[i] = self._boundsFromPercentage(xCutoffHigh[i],inimg.width)
			yCutoffHigh[i] = self._boundsFromPercentage(yCutoffHigh[i],inimg.height)
			yCutoffLow[i] = self._boundsFromPercentage(yCutoffLow[i],inimg.height)

		filter = None
		h  = inimg.height
		w  = inimg.width
		
		if( grayscale ):
			filter = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			cv.Zero(filter)
			#now make all of the corners black
			cv.Rectangle(filter,(0,0),(xCutoffHigh[0],yCutoffHigh[0]),255,thickness=-1) #TL
			cv.Rectangle(filter,(0,h-yCutoffHigh[0]),(xCutoffHigh[0],h),255,thickness=-1) #BL
			cv.Rectangle(filter,(w-xCutoffHigh[0],0),(w,yCutoffHigh[0]),255,thickness=-1) #TR
			cv.Rectangle(filter,(w-xCutoffHigh[0],h-yCutoffHigh[0]),(w,h),255,thickness=-1) #BR
			cv.Rectangle(filter,(0,0),(xCutoffLow[0],yCutoffLow[0]),0,thickness=-1) #TL
			cv.Rectangle(filter,(0,h-yCutoffLow[0]),(xCutoffLow[0],h),0,thickness=-1) #BL
			cv.Rectangle(filter,(w-xCutoffLow[0],0),(w,yCutoffLow[0]),0,thickness=-1) #TR
			cv.Rectangle(filter,(w-xCutoffLow[0],h-yCutoffLow[0]),(w,h),0,thickness=-1) #BR


		else:
			#I need to look into CVMERGE/SPLIT... really need to know
			# how much memory we're allocating here
			filterB = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			filterG = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			filterR = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,1)
			cv.Zero(filterB)
			cv.Zero(filterG)
			cv.Zero(filterR)
			#now make all of the corners black
			temp = [filterB,filterG,filterR]
			i = 0
			for f in temp:
				cv.Rectangle(f,(0,0),(xCutoffHigh[i],yCutoffHigh[i]),255,thickness=-1) #TL
				cv.Rectangle(f,(0,h-yCutoffHigh[i]),(xCutoffHigh[i],h),255,thickness=-1) #BL
				cv.Rectangle(f,(w-xCutoffHigh[i],0),(w,yCutoffHigh[i]),255,thickness=-1) #TR
				cv.Rectangle(f,(w-xCutoffHigh[i],h-yCutoffHigh[i]),(w,h),255,thickness=-1) #BR
				cv.Rectangle(f,(0,0),(xCutoffLow[i],yCutoffLow[i]),0,thickness=-1) #TL
				cv.Rectangle(f,(0,h-yCutoffLow[i]),(xCutoffLow[i],h),0,thickness=-1) #BL
				cv.Rectangle(f,(w-xCutoffLow[i],0),(w,yCutoffLow[i]),0,thickness=-1) #TR
				cv.Rectangle(f,(w-xCutoffLow[i],h-yCutoffLow[i]),(w,h),0,thickness=-1) #BR
				i = i+1

			filter = cv.CreateImage((inimg.width,inimg.height),cv.IPL_DEPTH_8U,3)
			cv.Merge(filterB,filterG,filterR,None,filter)

		scvFilt = Image(filter)
		retVal = self.applyDFTFilter(inimg,scvFilt,grayscale)
		return retVal
		
	def applyButterworthFilter(self,inimg,dia=400,order=2,highpass=False,grayscale=False):
		"""
		**SUMMARY**

		Creates a butterworth filter of 64x64 pixels, resizes it to fit
		image, applies DFT on image using the filter.
		Returns image with DFT applied on it

		**PARAMETERS**
		* *inimg* - Image to do DFT on.
		* *dia* - int Diameter of Butterworth low pass filter
		* *order* - int Order of butterworth lowpass filter
		* *highpass*: BOOL True: highpass filterm False: lowpass filter
		* *grayscale*: BOOL

		**EXAMPLE**

		>>> im = Image("lenna")
		>>> df = DFT()
		>>> img = df.applyButterworth(im,dia=400,order=2,highpass=True,grayscale=False)

		Output image: http://i.imgur.com/5LS3e.png

		>>> img = df.applyButterworth(im,dia=400,order=2,highpass=False,grayscale=False)

		Output img: http://i.imgur.com/QlCAY.png

		>>> im = Image("grayscale_lenn.png") #take image from here: http://i.imgur.com/O0gZn.png
		>>> img = df.applyButterworth(im,dia=400,order=2,highpass=True,grayscale=True)

		Output img: http://i.imgur.com/BYYnp.png

		>>> img = df.applyButterworth(im,dia=400,order=2,highpass=False,grayscale=True)

		Output img: http://i.imgur.com/BYYnp.png

		**SEE ALSO**

		:py:meth:`rawDFTImage`
		:py:meth:`getDFTLogMagnitude`
		:py:meth:`applyDFTFilter`
		:py:meth:`highPassFilter`
		:py:meth:`lowPassFilter`
		:py:meth:`bandPassFilter`
		:py:meth:`_inverseDFT`
		:py:meth:`applyButterworthFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyGaussianFilter`
		:py:meth:`applyUnsharpMask`

		"""
		w,h = inimg.size()
		flt = cv.CreateImage((64,64),cv.IPL_DEPTH_8U,1)
		dia = int(dia/((w/64.0+h/64.0)/2.0))
		if highpass:
			for i in range(64):
				for j in range(64):
					d = sqrt((j-32)**2+(i-32)**2)
					flt[i,j] = 255-(255/(1+(d/dia)**(order*2)))
		else:
			for i in range(64):
				for j in range(64):
					d = sqrt((j-32)**2+(i-32)**2)
					flt[i,j] = 255/(1+(d/dia)**(order*2))

		flt = Image(flt)
		flt_re = flt.resize(w,h)
		img = self.applyDFTFilter(inimg,flt_re,grayscale)
		return img

	def applyGaussianFilter(self,inimg, dia=400, highpass=False, grayscale=False):
		"""
		**SUMMARY**

		Creates a gaussian filter of 64x64 pixels, resizes it to fit
		image, applies DFT on image using the filter.
		Returns image with DFT applied on it

		**PARAMETERS**

		* *inimg* - Image to do DFT on.
		* *dia* -  int - diameter of Gaussian filter
		* *highpass*: BOOL True: highpass filter False: lowpass filter
		* *grayscale*: BOOL

		**EXAMPLE**

		>>> im = Image("lenna")
		>>> df = DFT()
		>>> img = df.applyGaussianfilter(im,dia=400,highpass=True,grayscale=False)

		Output image: http://i.imgur.com/DttJv.png

		>>> img = df.applyGaussianfilter(im,dia=400,highpass=False,grayscale=False)

		Output img: http://i.imgur.com/PWn4o.png

		>>> im = Image("grayscale_lenn.png") #take image from here: http://i.imgur.com/O0gZn.png
		>>> img = df.applyGaussianfilter(im,dia=400,highpass=True,grayscale=True)

		Output img: http://i.imgur.com/9hX5J.png

		>>> img = df.applyGaussianfilter(im,dia=400,highpass=False,grayscale=True)

		Output img: http://i.imgur.com/MXI5T.png

		**SEE ALSO**

		:py:meth:`rawDFTImage`
		:py:meth:`getDFTLogMagnitude`
		:py:meth:`applyDFTFilter`
		:py:meth:`highPassFilter`
		:py:meth:`lowPassFilter`
		:py:meth:`bandPassFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyButterworthFilter`
		:py:meth:`InverseDFT`
		:py:meth:`applyGaussianFilter`
		:py:meth:`applyUnsharpMask`

		"""
		w,h = inimg.size()
		flt = cv.CreateImage((64,64),cv.IPL_DEPTH_8U,1)
		dia = int(dia/((w/64.0+h/64.0)/2.0))
		if highpass:
			for i in range(64):
				for j in range(64):
					d = sqrt((j-32)**2+(i-32)**2)
					val = 255-(255.0*math.exp(-(d**2)/((dia**2)*2)))
					flt[i,j]=val
		else:
			for i in range(64):
				for j in range(64):
					d = sqrt((j-32)**2+(i-32)**2)
					val = 255.0*math.exp(-(d**2)/((dia**2)*2))
					flt[i,j]=val        
				
		flt = Image(flt)
		flt_re = flt.resize(w,h)
		img = self.applyDFTFilter(inimg,flt_re,grayscale)
		return img
		
	def applyUnsharpMask(self,inimg,boost=1,dia=400,grayscale=False):
		"""
        **SUMMARY**

        This method applies unsharp mask or highboost filtering
        on image depending upon the boost value provided.
        DFT is applied on image using gaussian lowpass filter.
        A mask is created subtracting the DFT image from the original
        iamge. And then mask is added in the image to sharpen it.
        unsharp masking => image + mask
        highboost filtering => image + (boost)*mask

        **PARAMETERS**

		* *inimg* - Image to do DFT on.
        * *boost* - int  boost = 1 => unsharp masking, boost > 1 => highboost filtering
        * *dia* - int Diameter of Gaussian low pass filter
        * *grayscale* - BOOL

        **EXAMPLE**

        Gaussian Filters:

        >>> im = Image("lenna")
		>>> df = DFT()
        >>> img = df.applyUnsharpMask(im,2,grayscale=False) #highboost filtering

        output image: http://i.imgur.com/A1pZf.png

        >>> img = df.applyUnsharpMask(im,1,grayscale=False) #unsharp masking

        output image: http://i.imgur.com/smCdL.png

        >>> im = Image("grayscale_lenn.png") #take image from here: http://i.imgur.com/O0gZn.png
        >>> img = df.applyUnsharpMask(im,2,grayscale=True) #highboost filtering

        output image: http://i.imgur.com/VtGzl.png

        >>> img = df.applyUnsharpMask(im,1,grayscale=True) #unsharp masking

        output image: http://i.imgur.com/bywny.png

        **SEE ALSO**

        :py:meth:`rawDFTImage`
        :py:meth:`getDFTLogMagnitude`
        :py:meth:`applyDFTFilter`
        :py:meth:`highPassFilter`
        :py:meth:`lowPassFilter`
        :py:meth:`bandPassFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyButterworthFilter`
        :py:meth:`InverseDFT`
        :py:meth:`applyGaussianFilter`
        :py:meth:`applyUnsharpMask`

        """
		if boost < 0:
			print "boost >= 1"
			return None

		lpIm = self.applyGaussianFilter(inimg,dia=dia,grayscale=grayscale,highpass=False)
		im = Image(inimg.getBitmap())
		mask = im - lpIm
		img = im
		for i in range(boost):
			img = img + mask
		return img
		
	def createLowpassfilter(self,row,col,cutoff,n):
		"""
		**SUMMARY**
		
		This will return a low pass filter with given
		dimension(row * column). The parameters are:
		row : 	  Number of row of the filter
		col : 	  Number of columns of the filter
		cutoff :  Cutoff frequency. Must be in between 0 and 0.5
		n :		  Order of the filter. Must be an integer >= 1
		
		**RETURNS**
		A 2 dimensional array of the filter created with row  * col
		
		**EXAMPLE**
		result = lowpassfilter(10,10,0.3,2)
		"""
		#Check if cutoff value is within 0 and 0.5 
		if cutoff < 0 or cutoff > 0.5:
			print('Cutoff frequency must be between 0 and 0.5')
			sys.exit(-1)
		
		#Check if n is an integer >= 1
		if n%1 != 0 or n < 1:
			print('n must be an integer >= 1')
			sys.exit(-1)
		
		#Make empty arrays to store values
		x = numpy.zeros(row*col).reshape(row,col)
		y = numpy.zeros(row*col).reshape(row,col)
		radius = numpy.zeros(row*col).reshape(row,col)
		filter = numpy.zeros(row*col).reshape(row,col)
		
		for i in range(0,row):
			for j in range(0,col):
				#Create row*col arrays, with centralized values
				# and calculate value from center(radius).
				# Create filter using this radius, cutoff and n values.
				x[i,j] = ((j+1) - (math.floor(col/2) + 1))/col
				y[i,j] = ((i+1) - (math.floor(row/2) + 1))/row
				radius[i,j] = math.sqrt(math.pow(x[i,j],2) + math.pow(y[i,j],2))
				filter[i,j] = round(1 / (1 + math.pow((radius[i,j] / cutoff),2*n)) , 4)
	
		return filter