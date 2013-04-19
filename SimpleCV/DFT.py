#Load required libraries
import math
import numpy

class DFT():
	"""
	**SUMMARY**
	
	The DFT class is used to create a 2-Dimensional filter of 
	given size with a set cutoff frequency and order of filter.
	
	"""
	
	def lowpassfilter(self,row,col,cutoff,n):
		"""
		**SUMMARY**
		
		This will return a low pass butterworth filter with given
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