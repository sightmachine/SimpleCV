#!/usr/bin/python
'''
This example replicates a turret in that it searches the screen for a
person and then once found will announce with a sound and then track
them.  Although it is not required an Arduino with a Servo motor is
recommended to act as the turret.  The sound samples are not included
but any .wav file should work as long as it's in the same directory.
To use the arduino you will also need pyfirmata installed on the arduino
itself as well as the python library installed. This can be found at:
https://bitbucket.org/tino/pyfirmata

'''
print __doc__
import time
from SimpleCV import *
import pygame

#----Start Config-----#
ARDUINO = False #Set this to true to enable arduino support
if ARDUINO:
  from pyfirmata import Arduino, util
  board = Arduino('/dev/ttyUSB0') #This value may have to change to match your system
  it = util.Iterator(board) #load arduino drivers
  it.start() #start the arduino
  pin9 = board.get_pin('d:9:p') #the pin to control the motor
  pin2 = board.get_pin('d:2:o') #pin to control the light
  pin3 = board.get_pin('d:3:o') #pin to control the light
  pin4 = board.get_pin('d:4:o') #pin to control the light

# Sound Config
SOUND = True
if SOUND:
  pygame.mixer.init()
  ping = pygame.mixer.Sound('ping.wav')
  found_sound = pygame.mixer.Sound('found.wav')
  searching_sound = pygame.mixer.Sound('searching.wav')

# Time Config
found_time = time.time()
search_timelimit = 2
search_time = time.time()
speak_time = 3
speak_last = time.time()
light_time = time.time()
light_time_max = 0.1

#Other Config
cam = Camera() #initialize the camera
display = Display((800,600)) #create a display of 800 x 600 to show the image
swidth = 320
sheight = 240
hc = HaarCascade('face.xml')
previous_face_xy = None
face_ratio = 0.02 #the face found has to be this percent of the screen size
max_move_x = 0.85 #the maximum percent to move the servo relative to screen size
min_move_x = 0.25 #the minimum percent to move the servo relative to screen size
search_x = (max_move_x + min_move_x) / 2.0 #set the start position to the middle
search_move_inc = 0.01 #how fast to move the turret
face_not_found_frames = 0 #counter to keep if face is lost
face_not_found_limit = 20 #the amount of frames to lose a face than switch to search mode
light_flip = 1 #start the light cycle in this mode
number_of_lights = 3 #the number of LED's attached
STATE = "SEARCH" #set search at the beginning state.
print "Starting Search mode"
if SOUND: searching_sound.play()
#--- End Config ---#

#---Main Loop ----#
while True:
  # Start Acquistion
  current_time = time.time()
  image = cam.getImage().flipHorizontal().scale(swidth, sheight)
  faces = image.findHaarFeatures(hc, scale_factor=1.2, min_neighbors=2, use_canny=1) # load in trained face file
  if faces: #if any faces are found in the scene
    if not previous_face_xy:
      previous_face_xy = (faces[-1].x, faces[-1].y)
    if previous_face_xy:
      distances = [int(f.distanceFrom(previous_face_xy)) for f in faces]
      nearest = faces[distances.index(min(distances))]
      ratio = (nearest.width() * nearest.height()) / float(image.area())
      if ratio > face_ratio: #Found the face
        found_time = time.time()
        image.drawCircle((nearest.x, nearest.y), 10,Color.BLUE, 5)
        previous_face_xy = (nearest.x, nearest.y)
        y = previous_face_xy[1]
        x = previous_face_xy[0]
        sfactorx = x / float(swidth)
        face_not_found_frames = 0
      else:
        face_not_found_frames = face_not_found_frames + 1
  else:
    face_not_found_frames = face_not_found_frames + 1
  # End Acquistiion

  # Start State Actions
  if STATE == "SEARCH": #This is search mode and moves left to right
    if search_x < min_move_x:
      search_move_inc = -search_move_inc
    elif search_x > max_move_x:
      search_move_inc = -search_move_inc

    search_x = search_x + search_move_inc
          
    if ARDUINO:
      pin9.write(search_x)
      if light_flip == 1:
        pin2.write(True)
        pin3.write(False)
        pin4.write(False)
      elif light_flip == 2:
        pin2.write(False)
        pin3.write(True)
        pin4.write(False)
      elif light_flip == 3:
        pin2.write(False)
        pin3.write(False)
        pin4.write(True)
 
      if (current_time - light_time) > light_time_max:        
        light_flip = light_flip + 1
        light_time = time.time()
        if light_flip > number_of_lights:
          light_flip = 1
          
    #Change state if need be
    if (current_time - search_time) > search_timelimit and face_not_found_frames == 0:
        print "switching to TRACKING mode"
        STATE = "TRACKING"
        if SOUND: found_sound.play()
  
  if STATE == "TRACKING": #This is tracking mode and moves
      movex = max_move_x * sfactorx #apply the scale factor for movement to appear more realistic
      if movex < min_move_x:
        movex = min_move_x
      if movex > max_move_x:
        movex = max_move_x
      if ARDUINO: #move servo and turn on all lights
        pin9.write(movex)
        pin2.write(True)
        pin3.write(True)
        pin4.write(True)
          
  # Start State change
  if face_not_found_frames > face_not_found_limit and STATE == "TRACKING":
      print "switching to SEARCH mode"
      STATE = "SEARCH"
      search_time = time.time()

      if (current_time - speak_last) > speak_time and SOUND: #only speak if a certain amount of time has elapsed
        searching_sound.play()
        speak_last = time.time()

  image.save(display) #display the image
