from SimpleCV import *

disp = Display((640,528))
cam = Camera(1)
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
