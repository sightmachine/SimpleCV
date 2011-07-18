#!/usr/bin/python 

import webbrowser, sys, time, random
from SimpleCV import Camera, Image, JpegStreamer, Color
from scipy.spatial.distance import euclidean as distance
"""
This script can be used to quickly calibrate a camera 
"""

def showText(img, text):
  img.dl().setFontSize(25)
  width, height = img.dl().textDimensions(text)
  #img.dl().text(str(width) + 'x' + str(height), (100, 100))
  img.dl().text(text, ((img.width / 2) - (width / 2), 100 - height / 2), color = (0, 120, 0))
  
def drawline(img, pt1, pt2):
  img.dl().line(pt1, pt2, Color.GREEN, 5, antialias = False)

def saveCalibrationImage(i, imgset, dims):
  """
  Save our image in the calibration set
  """
  if (len(imgset)):
    lastcb = imgset[-1].findChessboard(dims, subpixel = False)
    thiscb = i.findChessboard(dims, subpixel = False)
    
    cbmid = len(lastcb.coordinates()) / 2
    if distance(lastcb.coordinates()[cbmid], thiscb.coordinates()[cbmid]) < 30:
      showText(i, "Move the chessboard around inside the green rectangle")
      return
  
  imgset.append(i.copy())
  global save_location
  if not save_location:
    return
    
  filename = save_location + "_image" + str(len(imgset)) + ".png"
  imgset[-1].save(filename)

def relativeSize(cb, i):
  return cb.area() / float(i.width * i.height)

def relPercent(cb, i):
  return str(int(relativeSize(cb,i) * 100)) + "%"

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
appears within the rectangle.
  """
  
def findLargeFlat(cb, i, calibration_set, dims):  
  drawline(i,  (10, 10), (i.width - 10, 10))
  drawline(i,  (i.width - 10, 10), (i.width - 10, i.height - 10))
  drawline(i,  (10, i.height - 10), (i.width - 10, i.height - 10))
  drawline(i,  (10, 10), (10, i.height - 10))
  
  
  if not cb:
    return
    
  if (relativeSize(cb, i) > 0.7):
    saveCalibrationImage(i, calibration_set, dims)
  else:
    showText(i,  "Chessboard is " + str(int(relativeSize(cb,i) * 100)) + " < 70% of view area, bring it closer")

  cb.draw()



def findSmallFlat(cb, i, calibration_set, dims):  
  lcs = len(calibration_set)
  if (lcs % 5 == 0): #outline the top left corner
    drawline(i,  (i.width / 2, 0), (i.width / 2, i.height / 2))
    drawline(i,  (0, i.height / 2), (i.width / 2, i.height / 2)) 
  if (lcs % 5 == 1): #outline top right corner
    drawline(i,  (i.width / 2, 0), (i.width / 2, i.height / 2)) 
    drawline(i,  (i.width, i.height/2), (i.width / 2, i.height / 2))
  if (lcs % 5 == 2): #outline bottom right corner
    drawline(i,  (i.width, i.height/2), (i.width / 2, i.height / 2))
    drawline(i,  (i.width / 2, i.height), (i.width / 2, i.height / 2))
  if (lcs % 5 == 3): #outline bottom left corner
    drawline(i,  (i.width / 2, i.height), (i.width / 2, i.height / 2))
    drawline(i,  (0, i.height / 2), (i.width / 2, i.height / 2))
  if (lcs % 5 == 4): #outline center
    drawline(i,  (i.width / 4, i.height / 4), (3 * i.width / 4, i.height / 4))
    drawline(i,  (3 * i.width / 4, i.height / 4), (3 * i.width / 4, 3 * i.height / 4))
    drawline(i,  (3 * i.width / 4, 3 * i.height / 4), (i.width / 4, 3 * i.height / 4))
    drawline(i,  (i.width / 4, 3 * i.height / 4), (i.width / 4, i.height / 4))

  if not cb:
    return
    
  if (relativeSize(cb, i) < 0.13):
    showText(i,  "Chessboard is " + relPercent(cb, i) + " < 13% bring it closer")
  elif (relativeSize(cb, i) > 0.25):
    showText(i,  "Chessboard is " + relPercent(cb, i) + " > 25% move it back")
  elif (horizontalTilt(cb) < 0.9 or verticalTilt < 0.9):
    showText(i,  "Chessboard is tilted, try to keep it flat")
  elif (lcs % 5 == 0): #top left corner
    if (cb.points[2][0] < i.width / 2 and cb.points[2][1] < i.height / 2):
      saveCalibrationImage(i, calibration_set, dims)
    else:
      showText(i, "Put the chessboard within the green rectangle")
  elif (lcs % 5 == 1): #top right corner
    if (cb.points[3][0] > i.width / 2 and cb.points[3][1] < i.height / 2):
      saveCalibrationImage(i, calibration_set, dims)
    else:
      showText(i, "Put the chessboard within the green rectangle")
  elif (lcs % 5 == 2): #bottom right corner
    if (cb.points[0][0] > i.width / 2 and cb.points[0][1] > i.height / 2):
      saveCalibrationImage(i, calibration_set, dims)
    else:
      showText(i, "Put the chessboard within the green rectangle")
  elif (lcs % 5 == 3): #bottom left corner
    if (cb.points[1][0] < i.width / 2 and cb.points[1][1] > i.height / 2):
      saveCalibrationImage(i, calibration_set, dims)
    else:
      showText(i, "Put the chessboard within the green rectangle")
  elif (lcs % 5 == 4): #center
    if (abs(cb.x - i.width / 2) < i.width/8.0 and abs(cb.y - i.height / 2) < i.height/8.0):
      saveCalibrationImage(i, calibration_set, dims)
  
  
def findHorizTilted(cb, i, calibration_set, dims):
  drawline(i,  (10, i.height / 8), (i.width - 10, 10))
  drawline(i,  (i.width - 10, 10), (i.width - 10, i.height - 10))
  drawline(i,  (10, i.height - i.height / 8), (i.width - 10, i.height - 10))
  drawline(i,  (10, i.height / 8), (10, i.height - i.height / 8))
  if not cb:
    return
    
  if relativeSize(cb, i) < 0.4:
    showText(i,  "Chessboard is " + relPercent(cb, i) + " / 40%, bring the Chessboard closer")
  elif horizontalTilt(cb) > 0.9:
    showText(i,  "Tip the right or left side of the Chessboard towards the camera")
  else:
    saveCalibrationImage(i, calibration_set, dims)

  
def findVertTilted(cb, i, calibration_set, dims):
  drawline(i,  (i.width / 8, 10), (i.width - i.width / 8, 10))
  drawline(i,  (i.width - i.width / 8, 10), (i.width - 10, i.height - 10))
  drawline(i,  (10, i.height - 10), (i.width - 10, i.height - 10))
  drawline(i,  (i.width / 8, 10), (10, i.height - 10))
  if not cb:
    return
    
  if relativeSize(cb, i) < 0.4:
    showText(i,  "Chessboard is " + relPercent(cb, i) + " / 40%, bring the Chessboard closer")
  elif verticalTilt(cb) > 0.9:
    showText(i,  "Tip the top or bottom of the Chessboard towards the camera")
  else:
    saveCalibrationImage(i, calibration_set, dims)
  
def findCornerTilted(cb, i, calibration_set, dims):
  drawline(i,  (i.width / 8, 10), (i.width - i.width / 8, 10))
  drawline(i,  (i.width - i.width / 8, 10), (i.width - 10, i.height - i.height / 8))
  drawline(i,  (10, i.height - 10), (i.width - 10, i.height - i.height / 8))
  drawline(i,  (i.width / 8, 10), (10, i.height - 10))
  
  if not cb:
    return 
  
  if relativeSize(cb, i) < 0.4:
    showText(i,  "Chessboard is " + relPercent(cb, i) + " / 40%, bring the Chessboard closer")
  elif verticalTilt(cb) > 0.9 or horizontalTilt(cb) > 0.9:
    showText(i,  "Tip the corner of the Chessboard more towards the camera")
  else:
    saveCalibrationImage(i, calibration_set, dims)
  
def main(camindex = 0, chessboard_width = 8, chessboard_height = 5, planemode = False, gridsize = 0.029, calibrationFile = "default"):
  global save_location
  
  camindex = 0
  if planemode:
    mode = 7
  else
    mode = 0
  
  dims = (chessboard_width, chessboard_height)  #change this if you are using something besides our 
  gridsize = 0.029  #default calibration to mm
  calibrationFile = "default"
  
  cam = Camera(camindex)
  d = cam.getImage().flipHorizontal().show()

  
  save_location = "" #change this if you want to save your calibration images
  
  calibration_set = [] #calibration images
  fc_set = []
  
  introMessage()
  
  
  while not d.isDone():
    time.sleep(0.01)
    i = cam.getImage().flipHorizontal()
    cb = i.findChessboard(dims, subpixel = False)
    
    
    if cb:
      cb = cb[0]
    elif mode != 6:
      showText(i, "Put a chessboard in the green outline")
      
    if mode == 0:  #10 pictures, chessboard filling 80% of the view space
      findLargeFlat(cb, i, calibration_set, dims)
      if (len(calibration_set) == 10):
        mode = 1
    elif mode == 1:  #5 pictures, chessboard filling 60% of screen, at 45 deg horiz
      findHorizTilted(cb, i, calibration_set, dims)
      if (len(calibration_set) == 15):
        mode = 2
    elif mode == 2:  #5 pictures, chessboard filling 60% of screen, at 45 deg vert
      findVertTilted(cb, i, calibration_set, dims)
      if (len(calibration_set) == 20):
        mode = 3
    elif mode == 3:  #5 pictures, chessboard filling 40% of screen, corners at 45
      findCornerTilted(cb, i, calibration_set, dims)
      if (len(calibration_set) == 25):
        mode = 4
    elif mode == 4:  #10 pictures, chessboard filling 12% - 25% of view space
      findSmallFlat(cb, i, calibration_set, dims)
      if (len(calibration_set) == 35):
        mode = 5
    elif mode == 5:
      cam.calibrate(calibration_set, gridsize, dims)
      cam.saveCalibration(calibrationFile)
      mode = 6
    elif mode == 6:
      showText(i,  "Saved calibration to " + calibrationFile)  
    if cb:
      cb.draw()
    
    i.save(d)
    
if __name__ == '__main__':
  import argparse
  
  #parser = argparse.ArgumentParser("Create calibration files for your camera")
  #args
  #camera = 0
  #chessboard_width = 8
  #chessboard_height = 5
  #plane_mode = False
  #grid_size = 0.029
  #calibrationFile
  
  #parser.add_argument('
  main(sys.argv)
