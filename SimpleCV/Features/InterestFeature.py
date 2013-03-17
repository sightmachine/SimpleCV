from SimpleCV.base import *
from SimpleCV.Features.Features import Feature, FeatureSet
from SimpleCV.Color import Color
from SimpleCV.ImageClass import Image



class KeypointClusterFeature(Feature):
	'''
	This class is used to find interesting points in an image

	Example:
	>>> i = Image('simplecv')
	>>> points = i.findInterestingPoints()
	>>> points.draw()
	>>> i.show()
	'''
	
	rank_order = None

	
	def __init__(self, i, at_x, at_y):
		super(KeypointClusterFeature, self).__init__(i, at_x, at_y, [(at_x, at_y),(at_x, at_y),(at_x, at_y),(at_x, at_y)])


		
	def draw(self, color = Color.GREEN, width = -1, fontsize = 20):
		if width == -1 or width == 1:
			fontsize = 20
		for r in self.rank_order:
			self.image.drawText(str(r), self.x, self.y, color, fontsize)

			
