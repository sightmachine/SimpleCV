from SimpleCV.base import *
from SimpleCV.ImageClass import *
from SimpleCV.Color import *
from SimpleCV.Features.Features import Feature, FeatureSet

class PlayingCard(Feature):
    def __init__(self, i, at_x, at_y, rank=None,suit=None):

        self.rank = rank
        self.suit = suit

        points = [(at_x-1,at_y-1),(at_x-1,at_y+1),(at_x+1,at_y+1),(at_x+1,at_y-1)]
        super(PlayingCard, self).__init__(i, at_x, at_y,points)

    def getCard(self):
        return (self.suit,self.rank)

    def draw(self, color = (255, 0, 0),width=1):
        """
        **SUMMARY**

        Draw a small circle around the corner.  Color tuple is single parameter, default is Red.

        **PARAMETERS**

        * *color* - An RGB color triplet.
        * *width* - if width is less than zero we draw the feature filled in, otherwise we draw the
          contour using the specified width.


        **RETURNS**

        Nothing - this is an inplace operation that modifies the source images drawing layer.

        """
        self.image.drawCircle((self.x, self.y), 4, color,width)
