from SimpleCV import *

# just putting this here so I don't forget

img = Image("derp.png")
img = img.edges()
npimg = img.getGrayNumpy()
x,y = np.where(npimg > 128)
pts = np.array([zip(x,y)],dtype='float32')
r = cv2.minEnclosingCircle(pts)
img.drawCircle(r[0],r[1],color=Color.RED,thickness=3)
