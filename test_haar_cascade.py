#!/usr/bin/python

from SimpleCV import * 

testimage = "sampleimages/orson_welles.jpg"
testoutput = "sampleimages/orson_welles_face.jpg"

def test_haarcascade():
  img = Image(testimage)
  faces = img.findHaarFeatures("haarcascade_frontalface_alt.xml")

  if (faces):
    faces.draw()
    img.save(testoutput)
    return 1
  else: 
    return 0
