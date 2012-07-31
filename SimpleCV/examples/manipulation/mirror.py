from SimpleCV import *

c = Camera()

while True:
    split = img.split(2, 1)
    left = split[0][0]
    mirrorred = img.blit(left.flipHorizontal(),(left.width + 1, 0))
    mirrorred.show()

    img = c.getImage()
