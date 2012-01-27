#!/usr/bin/python 
import time
import csv
from SimpleCV import Color, ColorCurve, Camera, Image, pg, np, cv
from SimpleCV.Display import Display

cam = Camera(1)
time.sleep(.1) # uhg
display = Display((800,600))
data = "None"
mydict = dict()
myfile = "mystuff.csv"
while( display.isNotDone() ):
    display.checkEvents()#check for mouse clicks
    img = cam.getImage()
    img = img.scale(.5) #use a smaller image
    img.drawRectangle(img.width/4,img.height/4,img.width/2,img.height/2,color=Color.RED,width=3)
    if( display.mouseLeft > 0 ): # click the mouse to read
        img.drawText("reading barcode... wait",10,10)
        img.save(display)
        bc = img.findBarcode()
        if( bc is not None ): # if we have a bc
            data = str(bc.data)
            print(data)
            if( mydict.has_key(data) ):
                mydict[data] = mydict[data] + 1 
            else:
                mydict[data] = 1 
    img.drawText("Click to scan.",10,10,color=Color.RED)
    myItem = "Last item scanned: " + data
    img.drawText(myItem,10,30)
    img.save(display) #display
    time.sleep(0.01)
#write to a CSV file. 
target= open( myfile, "wb" )
wtr= csv.writer( target )
wtr.writerow( ["item","count"])
for d in mydict.items():
    wtr.writerow(d)
target.close()
