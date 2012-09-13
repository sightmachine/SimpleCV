#!/usr/bin/python
'''
This program is a standard barcode reader.
To use it you need to have the following library installed:
http://zbar.sourceforge.net

To install on Ubuntu Linux 12.04 or higher:
sudo apt-get install python-zbar


Then line up the item in the red box and left click the mouse to tell
the program to try and read the barcode
'''

print __doc__


import time
import csv
from SimpleCV import Color, ColorCurve, Camera, Image, pg, np, cv
from SimpleCV.Display import Display

cam = Camera()
display = Display((800,600))
data = "None"
mydict = dict()
myfile = "barcode-list.csv"

while display.isNotDone():
    display.checkEvents()#check for mouse clicks
    img = cam.getImage()
    img.drawRectangle(img.width/4,img.height/4,img.width/2,img.height/2,color=Color.RED,width=3)
    if display.mouseLeft: # click the mouse to read
        img.drawText("reading barcode... wait",10,10)
        img.save(display)
        barcode = img.findBarcode()
        if barcode: # if we have a barcode
            data = str(barcode.data)
            print data
            if mydict.has_key(data):
                mydict[data] = mydict[data] + 1 
            else:
                mydict[data] = 1 
    img.drawText("Click to scan.",10,10,color=Color.RED)
    myItem = "Last item scanned: " + data
    img.drawText(myItem,10,30)
    img.save(display) #display
    
#write to a CSV file. 
target= open( myfile, "wb" )
wtr= csv.writer( target )
wtr.writerow( ["item","count"])
for d in mydict.items():
    wtr.writerow(d)
target.close()
