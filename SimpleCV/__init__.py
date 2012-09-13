__version__ = '1.3.0'

from SimpleCV.base import *
from SimpleCV.Camera import *
from SimpleCV.Color import *
from SimpleCV.Display import *
from SimpleCV.Features import *
from SimpleCV.ImageClass import *
from SimpleCV.Stream import *
from SimpleCV.Font import *
from SimpleCV.ColorModel import *
from SimpleCV.DrawingLayer import *
from SimpleCV.Segmentation import *
from SimpleCV.MachineLearning import *


if (__name__ == '__main__'):
    from SimpleCV.Shell import *
    main(sys.argv)
