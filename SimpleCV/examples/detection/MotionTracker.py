#!/usr/bin/python
'''
This SimpleCV example uses a technique called frame differencing to determine
if motion has occured.  You take an initial image, then another, subtract
the difference, what is left over is what has changed between those two images
this are typically blobs on the images, so we do a blob search to count
the number of blobs and if they exist then motion has occured
'''
import sys, time, socket
from SimpleCV import *

cam = Camera() #setup the camera

#settings for the project
min_size = 0.1*cam.getProperty("width")*cam.getProperty("height") #make the threshold adapatable for various camera sizes
thresh = 10 # frame diff threshold
show_message_for = 2 # the amount of seconds to show the motion detected message
motion_timestamp = int(time.time())
message_text = "Motion detected"
draw_message = False

lastImg = cam.getImage()
lastImg.show()

while True:
    newImg = cam.getImage()
    trackImg = newImg - lastImg # diff the images
    blobs =  trackImg.findBlobs() #use adapative blob detection
    now = int(time.time())

    #If blobs are found then motion has occured
    if blobs:
        motion_timestamp = now
        draw_message = True

    #See if the time has exceeded to display the message
    if (now - motion_timestamp) > show_message_for:
        draw_message = False

    #Draw the message on the screen
    if(draw_message):
        newImg.drawText(message_text, 5,5)
        print message_text


    lastImg = newImg # update the image
    newImg.show()
