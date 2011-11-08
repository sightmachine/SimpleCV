import time
from SimpleCV import *
from SimpleCV.Display import Display, pg
w = 400
h = 300
t=1
display = Display(resolution = (w,h)) #create a new display to draw images on
img = Image('../sampleimages/aerospace.jpg')
img = img.scale(800,600)
img2 = img.scale(w,h)
smallWbigH = img.scale(100,400)
smallHbigW = img2.scale(500,100)
smallW = img2.scale(100,h)
smallH = img2.scale(w,100)
small = img2.scale(99,23)
big = img2.scale(555,432)

foo = "Image:"+str((img.width,img.height))
print(foo)
print('Image should scale clean')
display.writeFrame(img)
time.sleep(t)

foo = "Image:"+str((img2.width,img2.height))
print(foo)
print('Image should scale clean')
display.writeFrame(img2)
time.sleep(t)

foo = "Image:"+str((smallWbigH.width,smallWbigH.height))
print(foo)
display.writeFrame(smallWbigH)
time.sleep(t)

foo = "Image:"+str((smallHbigW.width,smallHbigW.height))
print(foo)
display.writeFrame(smallHbigW)
time.sleep(t)

foo = "Image:"+str((smallW.width,smallW.height))
print(foo)
display.writeFrame(smallW)
time.sleep(t)

foo = "Image:"+str((smallH.width,smallH.height))
print(foo)
display.writeFrame(smallH)
time.sleep(t)

foo = "Image:"+str((small.width,small.height))
print(foo)
display.writeFrame(small)
time.sleep(t)

foo = "Image:"+str((big.width,big.height))
print(foo)
display.writeFrame(big)
time.sleep(t)

foo = "Crop Image:"+str((img.width,img.height))
print(foo)
display.writeFrame(img, fit=False)
time.sleep(t)

foo = "Crop Image:"+str((img2.width,img2.height))
print(foo)
display.writeFrame(img2, fit=False)
time.sleep(t)

foo = "Crop Image:"+str((smallWbigH.width,smallWbigH.height))
print(foo)
display.writeFrame(smallWbigH, fit=False)
time.sleep(t)

foo = "Crop Image:"+str((smallHbigW.width,smallHbigW.height))
print(foo)
display.writeFrame(smallHbigW, fit=False)
time.sleep(t)

foo = "Crop Image:"+str((smallW.width,smallW.height))
print(foo)
display.writeFrame(smallW, fit=False)
time.sleep(t)

foo = "Crop Image:"+str((smallH.width,smallH.height))
print(foo)
display.writeFrame(smallH, fit=False)
time.sleep(t)

foo = "Crop Image:"+str((small.width,small.height))
print(foo)
display.writeFrame(small, fit=False)
time.sleep(t)

foo = "Crop Image:"+str((big.width,big.height))
print(foo)
display.writeFrame(big, fit=False)
time.sleep(t)
