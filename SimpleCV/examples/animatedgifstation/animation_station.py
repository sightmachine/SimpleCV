#!/usr/bin/python

from time import sleep
from pyfirmata import Arduino, util
from images2gif import writeGif 
from SimpleCV import *

pyrinter_url = "http://localhost:8080/printtext/"
flickr_user = "foo"
flickr_tags = "ingenuitas"
animation_file = "./animation.gif"

c = Camera()
board = Arduino("/dev/ttyUSB0")

it = util.Iterator(board)
it.start()

button_1 = board.get_pin('d:12:i')
button_2 = board.get_pin('d:13:i')

imageset = []

button_1_state = False
button_2_state = False


while True:
  if (button_1.read() and not button_1_state):
    button_1_state = True
    imageset.append(c.getImage().getPIL())
    writeGif(animation_file, imageset, 0.2, 9999)
    sleep(0.5)
    print "button 1 pressed"
  elif (button_1_state and not button_1.read()):
    print "button 1 let up"
    button_1_state = False
    
    
  if (button_2.read() and not button_2_state):
    button_2_state = True
    imageset.append(c.getImage().getPIL())
    writeGif(animation_file, imageset, 0.2, 9999)
    #url = upload_to_flickr
    #p = pyrinter
    print "button 2 pressed"
    imageset = []
  elif (button_2_state and not button_2.read()):
    print "button 2 let up"
    button_2_state = False

  sleep(0.01)
