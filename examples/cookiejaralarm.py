#!/usr/bin/python

#-----------------------------------------------------------------------
#
# This is an example program demostrating a cookie jar alarm
# the program monitors using Hu moments and talks to the
# arduino to light pin 13.
#
# Requirements: Arduino with firmata loaded
#-----------------------------------------------------------------------

import sys, time, socket
sys.path.append("..")

from SimpleCV import *
import pyfirmata

#settings for the project
port_original = 8080  #port to view the camera view
port_processed = 8081 #port to look at the processed view
arduino_serial = "/dev/ttyUSB0"  #address of the arduino
arduino_pin = 8  #which pin goes high when the alarm sounds
blob_thresh = 50 #blob intensity thresh
hu_threshold = 0.5 #how much distortion will throw the alarm

#create JPEG streamers
original_js = JpegStreamer(port_original)
processed_js = JpegStreamer(port_processed)
cam = Camera()
arduino = pyfirmata.Arduino(arduino_serial)

closed_hu = 0
count = 0
while (1):
  i = cam.getImage()
  i.save(original_js.filename)

  r,g,b = i.channels(True)
  i = g - b #subtract green from blue

  blobs = i.findBlobs(blob_thresh)
  if not blobs:
    continue

  blobs[0].draw()  #we only really care about the largest blob
  i.save(processed_js.filename)

  hu = blobs[0].cvblob.u02
  if not closed_hu: 
    closed_hu = blobs[0].cvblob.u02      

#  print str(closed_hu) + ":" + str(hu) + ":" + str(abs(closed_hu - hu) / hu)
  if (abs((closed_hu - hu)/ hu) > hu_threshold): 
    arduino.digital[arduino_pin].write(1)
  else:
    arduino.digital[arduino_pin].write(0)

  count = count + 1
  time.sleep(0) #yield to the webserver
