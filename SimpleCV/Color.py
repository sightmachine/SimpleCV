# SimpleCV Color Library
#
# This library is used to modify different color properties of images

#load required libraries
from .base import *

class ColorCurve:
  """
  ColorCurve is a color spline class for performing color correction.  
  It can takeas parameters a SciPy Univariate spline, or an array with at 
  least 4 point pairs.  Either of these must map in a 255x255 space.  The curve 
  can then be used in the applyRGBCurve, applyHSVCurve, and 
  applyInstensityCurve functions::

    clr = ColorCurve([[0,0], [100, 120], [180, 230], [255, 255]])
    image.applyIntensityCurve(clr)

  the only property, mCurve is a linear array with 256 elements from 0 to 255
  """
  mCurve =""

  def __init__(self, curve_vals ):
    inBins = linspace(0,255,256)
    if( type(curve_vals) == UnivariateSpline ):
      self.mCurve = curvVals(inBins)
    else: 
      curve_vals = np.array(curve_vals)
      aSpline = UnivariateSpline( curve_vals[:,0],curve_vals[:,1],s=1)   
      self.mCurve = aSpline(inBins)
 
