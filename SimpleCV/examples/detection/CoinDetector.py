'''
This example finds a quarter in the picture and then uses that measurement
to determine the rest of the coins in the picture.  Since a quarter is always
a certain size we can use it as a reference because it is known.

In this example we use millimeters to pixels to do the conversion.

The sizes of coins are as follows:
penny - 19.05 mm
nickel - 21.21 mm
dime - 17.9 mm
quarter - 24.26 mm

'''

print __doc__

from SimpleCV import *
# A quarter is 24.26mm or 0.955in
quarterSize = 24.26 #millimeters

# This will hold the ratio of the image size to a quarter's actual size
sizeRatio = 0
objectSize = 0

img = Image('coins.jpg', sample=True)
segmented = img.hueDistance(Color.BLACK)
coins = img.invert().findBlobs(minsize=200)

#Here we compute the scale factor
if coins:
		c = coins[-1]
		diameter = c.radius() * 2
		sizeRatio = quarterSize / diameter

#Now we print the measurements back on the picture
for coin in coins:
		#get the physical size of the coin
		size = (coin.radius() * 2) * sizeRatio
		#label the coin accordingly
		if size > 18 and size < 20:
			text = "Type: penny"
		elif size > 20 and size < 23:
			text = "Type: nickel"
		elif size > 16 and size < 18:
			text = "Type: dime"
		elif size > 23 and size < 26:
			text = "Type: quarter"
		else:
			text = "unknown"

		text = text + ", Size:" + str(size) + "mm"
		img.drawText(text, coin.x, coin.y)

img.show()
time.sleep(10)
