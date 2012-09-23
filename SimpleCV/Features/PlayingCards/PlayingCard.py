from SimpleCV.base import *
from SimpleCV.ImageClass import *
from SimpleCV.Color import * 
from SimpleCV.Features.Features import Feature, FeatureSet

class PlayingCard(Feature):
    def __init__(self, i, at_x, at_y, w, h,rank=None,suit=None):
        
        self.rank = rank
        self.suit = suit
        self.centerBlobs = None
        self.suitBlobs = None
        self.rankBlobs = None
        self.numberBlobs = None
        self.color = None
        self.cardImg = None
        self.c_width = None
        self.c_height = None
        self.c_angle = None 
        self.corners = None 
        self.img=i
        points = [(at_x,at_y),(at_x+w,at_y),(at_x+w,at_y+h),(at_x,at_y+h)]
        super(PlayingCard, self).__init__(i, at_x, at_y,points)

    def getCard(self):
        return (self.suit,self.rank)

    def draw(self, color = (255, 0, 0),width=1):
        """
        """
        (tl,tr,bl,br) = self.corners
        self.img.drawLine(tl,tr,color,thickness=width)
        self.img.drawLine(bl,br,color,thickness=width)
        self.img.drawLine(tl,bl,color,thickness=width)
        self.img.drawLine(tr,br,color,thickness=width)

