#!/usr/bin/python
# All this example does is find a face and replace it with another image.
# the image should auto scale to match the size of the face.


import time
from SimpleCV import *

cam = Camera() #initialize the camera
substition_image = "../../sampleimages/troll_face.png"

# Loop forever
while True:
    image = cam.getImage().flipHorizontal().scale(320, 240) # get image, flip it so it looks mirrored, scale to speed things up
    faces = image.findHaarFeatures("facetrack-training.xml") # load in trained face file
    #if there were faces found do something
    if faces:
        face = faces[-1]
        troll_face = Image(substition_image).scale(face.height(), face.width()) #load the image to super impose and scale it correctly
        image.dl().blit(troll_face, (face.points[0][0], face.points[0][1])) #super impose the new face on the existing face
    image.show() #display the image
    time.sleep(0.01) # Let the program sleep for 1 millisecond so the computer can do other things

