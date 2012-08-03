'''
This program trys to extract the color pallette from an image
it could be used in machine learning as a color classifier
'''
print __doc__

from SimpleCV import *
disp = Display((640,528))
cam = Camera()
count = 0
pal = None
while disp.isNotDone():
    img = cam.getImage()
    if count%10 == 0:
        temp = img.scale(.3)
        p = temp.getPalette()
        pal = temp.drawPaletteColors(size=(640,48))
    result = img.rePalette(p)
    result = result.sideBySide(pal,side='bottom')
    result.save(disp)
    count = count + 1
