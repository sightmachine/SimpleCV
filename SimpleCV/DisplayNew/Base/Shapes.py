"""
These classes are used to represent the objects drawn on a drawing layer.

**Note**
Not to be confused with classes in Detection.* . In addition to coordinates
thse also store color, alpha anf other displaying parameters
"""


class Line:
    def __init__(self,start,stop,color,width,antialias,alpha):
        self.start = start
        self.stop = stop
        self.color = color
        self.width = width
        self.antialias = antialias
        self.alpha = aplha

class Rectangle:
    def __init__(self,pt1,pt2,width,filled,antialias,alpha):
        self.pt1 = pt1
        self.pt2 = pt2
        self.color = color
        self.width = width
        self.antialias = antialias
        self.alpha = aplha

class Polygon:
    def __init__(self,points,width,filled,antialias,alpha):
        self.points = points
        self.color = color
        self.width = width
        self.antialias = antialias
        self.alpha = aplha

class Circle:
    def __init__(self, center, radius, color = Color.DEFAULT,antialias = True, width = 1, filled = False, alpha = -1, ):
        self.conter = center
        self.radius = radius
        self.color = color
        self.width = width
        self.antialias = antialias
        self.alpha = aplha

class Ellipse:
    def __init__(self, center, dimensions, color = Color.DEFAULT,antialias = True, width = 1, filled = False, alpha = -1):
        
        self.center = center
        self.dimensions = dimensions
        self.color = color
        self.width = width
        self.antialias = antialias
        self.alpha = aplha

class Bezier
    def __init__(self, points, steps, color = Color.DEFAULT,antialias = True, alpha = -1):
        self.points = points
        self.steps = steps
        self.color = color
        self.antialias = antialias
        self.alpha = aplha


