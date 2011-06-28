#!/usr/bin/python 

import webbrowser, sys, time
from SimpleCV import Camera, Image, JpegStreamer, Color
from scipy.spatial.distance import euclidean as distance
"""
This script can be used to quickly calibrate a camera 
"""


def saveCalibrationImage(i, imgset, dims):
  """
  Save our image in the calibration set
  
  """
  if (len(imgset)):
    lastcb = imgset[-1].findChessboard(dims, subpixel = False)
    thiscb = i.findChessboard(dims, subpixel = False)
    if distance(lastcb.coordinates()[0], thiscb.coordinates()[0]) < 10:
      return 
  
  imgset.append(i)
  global save_location
  if not save_location:
    return
    
  filename = save_location + "_image" + str(len(imgset)) + ".png"
  imgset[-1].save(filename)
  print "Saved to " + filename

def relativeSize(cb, i):
  return cb.area() / float(i.width * i.height)

def horizontalTilt(cb):  #ratio between the 0,3 and 1,2 point pairs
  distance_ratio = distance(cb.points[0], cb.points[3]) / distance(cb.points[1], cb.points[2])
  if distance_ratio > 1:
    return 1.0 / distance_ratio
  return distance_ratio

def verticalTilt(cb):  #radio between the 0, 1 and 2,3 point pairs
  distance_ratio = distance(cb.points[0], cb.points[1]) / distance(cb.points[2], cb.points[3])
  if distance_ratio > 1:
    return 1.0 / distance_ratio
  return distance_ratio
  
def introMessage():
  print """
This tool will help you calibrate your camera to help remove the effects of
lens distortion and give you more accurate measurement.  You will need:
  
- a printed 5x8 chessboard from our provided PDF, taped to a hard flat surface
- a room with good lighting and plenty of space for moving around
- a few minutes to begin calibration
  
To begin, please put your Chessboard close to the camera so the long side is
horizontal and it fill most of the screen.  Keep it parellel to the camera so it
appears as a rectangle.
  
We are going to take 10 pictures:
  """
  
def findLargeFlat(cb, i, calibration_set, dims):
  j = i.copy()
  
  i.drawLine( (10, 10), (i.width - 10, 10), Color.GREEN )
  i.drawLine( (i.width - 10, 10), (i.width - 10, i.height - 10), Color.GREEN )
  i.drawLine( (10, i.height - 10), (i.width - 10, i.height - 10), Color.GREEN )
  i.drawLine( (10, 10), (10, i.height - 10), Color.GREEN )
  
  
  if not cb:
    return
    
  if (relativeSize(cb, i) > 0.7):
    saveCalibrationImage(j, calibration_set, dims)
  else:
    print "Chessboard is " + str(int(relativeSize(cb,i) * 100)) + "% of view area, bring it closer"

  cb.draw()



def printSmallFlatMessage():
  print """
Now move back, so that the chessboard is parallel to the camera and far away, so
that it occupies about 1/6th of the screen. Take at least one image near each of
the corners and one near the center of the image.

First, lets take a picture in the top left corner of the image.
"""


def findSmallFlat(cb, i, calibration_set, dims):
  j = i.copy()
  
  lcs = len(calibration_set)
  if (lcs % 5 == 0): #outline the top left corner
    i.drawLine( (i.width / 2, 0), (i.width / 2, i.height / 2), Color.GREEN)
    i.drawLine( (0, i.height / 2), (i.width / 2, i.height / 2), Color.GREEN) 
  if (lcs % 5 == 1): #outline top right corner
    i.drawLine( (i.width / 2, 0), (i.width / 2, i.height / 2), Color.GREEN) 
    i.drawLine( (i.width, i.height/2), (i.width / 2, i.height / 2), Color.GREEN)
  if (lcs % 5 == 2): #outline bottom right corner
    i.drawLine( (i.width, i.height/2), (i.width / 2, i.height / 2), Color.GREEN)
    i.drawLine( (i.width / 2, i.height), (i.width / 2, i.height / 2), Color.GREEN)
  if (lcs % 5 == 3): #outline bottom left corner
    i.drawLine( (i.width / 2, i.height), (i.width / 2, i.height / 2), Color.GREEN)
    i.drawLine( (0, i.height / 2), (i.width / 2, i.height / 2), Color.GREEN)
  if (lcs % 5 == 4): #outline center
    i.drawLine( (i.width / 4, i.height / 4), (3 * i.width / 4, i.height / 4), Color.GREEN)
    i.drawLine( (3 * i.width / 4, i.height / 4), (3 * i.width / 4, 3 * i.height / 4), Color.GREEN)
    i.drawLine( (3 * i.width / 4, 3 * i.height / 4), (i.width / 4, 3 * i.height / 4), Color.GREEN)
    i.drawLine( (i.width / 4, 3 * i.height / 4), (i.width / 4, i.height / 4), Color.GREEN)

  if not cb:
    return
    
  
  if (relativeSize(cb, i) < 0.125):
    print "Chessboard is too small, bring it closer"
  elif (relativeSize(cb, i) > 0.25):
    print "Chessboard is too big, move it back"
  elif (horizontalTilt(cb) < 0.9 or verticalTilt < 0.9):
    print "Chessboard is tilted, try to keep it flat"
  elif (lcs % 5 == 0): #top left corner
    if (cb.points[2][0] < i.width / 2 and cb.points[2][1] < i.height / 2):
      saveCalibrationImage(j, calibration_set, dims)
  elif (lcs % 5 == 1): #top right corner
    if (cb.points[3][0] > i.width / 2 and cb.points[3][1] < i.height / 2):
      saveCalibrationImage(j, calibration_set, dims)
  elif (lcs % 5 == 2): #bottom right corner
    if (cb.points[0][0] > i.width / 2 and cb.points[0][1] > i.height / 2):
      saveCalibrationImage(j, calibration_set, dims)
  elif (lcs % 5 == 3): #bottom left corner
    if (cb.points[1][0] < i.width / 2 and cb.points[1][1] > i.height / 2):
      saveCalibrationImage(j, calibration_set, dims)
  elif (lcs % 5 == 4): #center
    if (abs(cb.x - i.width / 2) < i.width/8.0 and abs(cb.y - i.height / 2) < i.height/8.0):
      saveCalibrationImage(j, calibration_set, dims)
  
def printHorizTiltedMessage():
  print """
Now bring the board close to the screen and tilt it to the right or left
so that it is as close as it can be to a 45 degree angle from the camera.  Move it around the view
area, we are going to take 5 pictures.
  """
  
def findHorizTilted(cb, i, calibration_set, dims):
  j = i.copy()
  
  i.drawLine( (10, i.height / 8), (i.width - 10, 10), Color.GREEN )
  i.drawLine( (i.width - 10, 10), (i.width - 10, i.height - 10), Color.GREEN )
  i.drawLine( (10, i.height - i.height / 8), (i.width - 10, i.height - 10), Color.GREEN )
  i.drawLine( (10, i.height / 8), (10, i.height - i.height / 8), Color.GREEN )
  if not cb:
    return
    
  if relativeSize(cb, i) < 0.4:
    print "Bring the Chessboard closer"
  elif horizontalTilt(cb) > 0.9:
    print "Tip the right or left side of the Chessboard towards the camera"
  else:
    saveCalibrationImage(j, calibration_set, dims)

    
def printVertTiltedMessage():
  print """
Keeping the board close to the screen, tilt the top or bottom as much as you
can towards a 45 degree angle from the camera.  Move it around the view area.
  """
  
def findVertTilted(cb, i, calibration_set, dims):
  j = i.copy()
  
  i.drawLine( (i.width / 8, 10), (i.width - i.width / 8, 10), Color.GREEN )
  i.drawLine( (i.width - i.width / 8, 10), (i.width - 10, i.height - 10), Color.GREEN )
  i.drawLine( (10, i.height - 10), (i.width - 10, i.height - 10), Color.GREEN )
  i.drawLine( (i.width / 8, 10), (10, i.height - 10), Color.GREEN )
  if not cb:
    return
    
  if relativeSize(cb, i) < 0.4:
    print "Bring the Chessboard closer"
  elif verticalTilt(cb) > 0.9:
    print "Tip the top or bottom of the Chessboard towards the camera"
  else:
    saveCalibrationImage(j, calibration_set, dims)

def printCornerTiltedMessage():
  print """
Keeping the board close to the screen, tilt a corner as much as you
can towards a 45 degree angle from the camera.  Move it around the view area.
  """
  
def findCornerTilted(cb, i, calibration_set, dims):
  j = i.copy()
  
  i.drawLine( (i.width / 8, 10), (i.width - i.width / 8, 10), Color.GREEN )
  i.drawLine( (i.width - i.width / 8, 10), (i.width - 10, i.height - i.height / 8), Color.GREEN )
  i.drawLine( (10, i.height - 10), (i.width - 10, i.height - i.height / 8), Color.GREEN )
  i.drawLine( (i.width / 8, 10), (10, i.height - 10), Color.GREEN )
  
  if not cb:
    return 
  
  if relativeSize(cb, i) < 0.4:
    print "Bring the Chessboard closer"
  elif verticalTilt(cb) > 0.9 or horizontalTilt(cb) > 0.9:
    print "Tip the corner of the Chessboard more towards the camera"
  else:
    saveCalibrationImage(j, calibration_set, dims)
  
def printDoneMessage():
  print """
We are now going to calibrate the camera.  This may take a few moments.
"""
  
def main(argv):
  global save_location
  
  camindex = 1
  mode = 0
  dims = (5, 8)  #change this if you are using something besides our 
  gridsize = 29  #default calibration to mm
  calibrationFile = "Default"
  
  cam = Camera(camindex)
  js = JpegStreamer()

  
  save_location = "" #change this if you want to save your calibration images
  
  calibration_set = [] #calibration images
  
  cam.getImage().flipHorizontal().save(js)
  webbrowser.open(js.url())
  
  
  introMessage()
  
  
  while True:
    time.sleep(0.01)
    i = cam.getImage()
    cb = i.findChessboard(dims, subpixel = False)
    
    if cb:
      cb = cb[0]
    
    if mode == 0:  #10 pictures, chessboard filling 80% of the view space
      findLargeFlat(cb, i, calibration_set, dims)
      if (len(calibration_set) == 10):
        mode = 1
        printSmallFlatMessage()
    elif mode == 1:  #10 pictures, chessboard filling 12% - 25% of view space
      findSmallFlat(cb, i, calibration_set, dims)
      if (len(calibration_set) == 20):
        mode = 2
        printHorizTiltedMessage()
    elif mode == 2:  #5 pictures, chessboard filling 60% of screen, at 45 deg horiz
      findHorizTilted(cb, i, calibration_set, dims)
      if (len(calibration_set) == 25):
        mode = 3
        printVertTiltedMessage()
    elif mode == 3:  #5 pictures, chessboard filling 60% of screen, at 45 deg vert
      findVertTilted(cb, i, calibration_set, dims)
      if (len(calibration_set) == 30):
        mode = 4
        printCornerTiltedMessage()
    elif mode == 4:  #5 pictures, chessboard filling 40% of screen, corners at 45
      findCornerTilted(cb, i, calibration_set, dims)
      if (len(calibration_set) == 35):
        mode = 5
    elif mode == 5:
      printDoneMessage()
      
      cam.calibrate(calibration_set, gridsize, dims)
      cam.saveCalibration(calibrationFile)
      
      print "Saved calibration to " + calibrationFile
      print "you will need to load it with:"
      print "    Camera.loadCalibration(\""+calibrationFile+"\")"
      print "or "
      print "    Camera(" + str(camindex) + ", calibrationfile = \"" + calibrationFile + "\")"
      
    
    if cb:
      cb.draw()
    i.flipHorizontal().save(js)
    
if __name__ == '__main__':
  main(sys.argv)
