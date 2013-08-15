"""
These classes are used to represent the objects drawn on a drawing layer.

**Note**
These calsses should be kept picklable to be sent over a Pipe

Not to be confused with classes in Detection.* . In addition to coordinates
thse also store color, alpha and other displaying parameters

"""


class Line(object):
    def __init__(self,start,stop,color ,width,antialias,alpha):
        self.start = start
        self.stop = stop
        self.color = color
        self.width = width
        self.antialias = antialias
        self.alpha = alpha

class Rectangle(object):
    def __init__(self,pt1,pt2,color ,width,filled,antialias,alpha):
        self.pt1 = pt1
        self.pt2 = pt2
        self.color = color
        self.width = width
        self.filled = filled
        self.antialias = antialias
        self.alpha = alpha

class Polygon(object):
    def __init__(self,points,color, width, filled, antialias, alpha ):
        self.points = points
        self.color = color
        self.width = width
        self.filled = filled
        self.antialias = antialias
        self.alpha = alpha

class Circle(object):
    def __init__(self, center, radius, color, width, filled, antialias, alpha ):
        self.center = center
        self.radius = radius
        self.color = color
        self.width = width
        self.filled = filled
        self.antialias = antialias
        self.alpha = alpha

class Ellipse(object):
    def __init__(self, center, dimensions, color, width,filled ,antialias ,alpha ):
        
        self.center = center
        self.dimensions = dimensions
        self.color = color
        self.width = width
        self.filled = filled
        self.antialias = antialias
        self.alpha = alpha

class Bezier(object):
    def __init__(self, points, color, width, antialias, alpha ):
        self.points = points
        self.color = color
        self.width = width
        self.antialias = antialias
        self.alpha = alpha
        
class Text(object):
    def __init__(self, text, location, color ,size, font , bold ,italic ,underline, alpha,bg = None):
        self.text = text
        self.location = location
        self.font = font
        self.size = size
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.color = color
        self.alpha = alpha
        self.bg = bg # comes into play for ezViewText
        self.antialias = True # TODO maybe push this to the API


