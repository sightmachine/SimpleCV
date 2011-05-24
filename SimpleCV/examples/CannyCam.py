#!/usr/bin/python 
from SimpleCV import *


#settings for the project
num_caps = 10    #number of files to capture
path  = ""     #Path for output files
fname = "CanCan" #File base name
ext = ".jpg"     #File extension

#Create the camera
cam = Camera()


for j in range(num_caps):
  img = cam.getImage() #get image
  fileName = path + fname + str(j) + ext #make file name
  print fileName #print filename
  img2 = img.edges() #make edge image TODO: make this return an image object
  img2.save(fileName) # save the output

exit
