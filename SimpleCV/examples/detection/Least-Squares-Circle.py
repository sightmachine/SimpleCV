'''
This program finds least squares fitting approximation for more information see:
http://en.wikipedia.org/wiki/Least_squares

The program basically takes in a shape and tries to find the size of it.

'''
print __doc__

from SimpleCV import *
from scipy import optimize

img = Image("derp.png", sample=True)
img = img.edges()
npimg = img.getGrayNumpy()
x,y = np.where(npimg > 128)
x_m = np.average(x)
y_m = np.average(y)
def calc_R(xc, yc):
      return np.sqrt((x-xc)**2 + (y-yc)**2)
  
def f_2(c):
    Ri = calc_R(*c)
    return Ri - Ri.mean()
  
center_estimate = x_m, y_m
center_2, ier = optimize.leastsq(f_2, center_estimate)

xc_2, yc_2 = center_2
Ri_2 = calc_R(*center_2)
R_2 = Ri_2.mean()
residu_2 = sum((Ri_2 - R_2)**2)

print xc_2,yc_2
print R_2
img.drawCircle((xc_2,yc_2),R_2,color=Color.RED,thickness=3)
img.show()
time.sleep(10)
