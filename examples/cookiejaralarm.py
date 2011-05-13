#!/usr/bin/python 

import sys, time, socket
sys.path.append("..")

from SimpleCV import *
import pyfirmata

original_js = JpegStreamer() #defaults to 8080
processed_js = JpegStreamer(8081)
cam = Camera(1)
arduino = pyfirmata.Arduino("/dev/ttyACM0")

closed_hu = 0
def alarm(onoroff):
  arduino.digital[13].write(onoroff)
  pass


while (1):
  i = cam.getImage()
  
  i.save(original_js.filename)
  r,g,b = i.channels(True)

  cv.Sub(r.getBitmap(), g.getBitmap(), i.getBitmap()) 
  #red cookie jar

  red_blobs = ""
  thresh = 50
  i.save(processed_js.filename)
  red_blobs = i.findBlobs(thresh)
   
  if not red_blobs:
    #print str(thresh) + "no blobs"
    continue
  
  count = 0
  hu = red_blobs[0].cvblob.u11
  if not closed_hu: 
    closed_hu = red_blobs[0].cvblob.u11      

  print str(count) + ":" + str(hu) + str(abs(closed_hu - hu) / hu)
  if (abs((closed_hu - hu)/ hu) > 0.5): 
    alarm(1)
  else:
    alarm(0)

    count = count + 1
    time.sleep(0)
    

