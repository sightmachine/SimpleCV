#!/usr/bin/python

import webbrowser, sys, time, random
from SimpleCV import Camera, Image, JpegStreamer, Color
from SimpleCV.Display import Display
from scipy.spatial.distance import euclidean as distance
"""
This script can be used to quickly calibrate a camera


You will need to print out the accompanying calibration grid, or provide your
own.  The default arguments are for the provided grid.

By default, the camera calibrates to maximize the amount of coverage of different
planes and distances.  If you want higher accuracy for a single plane in a locked
distance specify "planemode".

"""

def showText(img, text):
    img.dl().setFontSize(25)
    width, height = img.dl().textDimensions(text)
    #img.dl().text(str(width) + 'x' + str(height), (100, 100))
    img.dl().text(text, ((img.width / 2) - (width / 2), 100 - height / 2), color = (0, 120, 0))

def drawline(img, pt1, pt2):
    img.dl().line(pt1, pt2, Color.GREEN, 5, antialias = False)

def drawrect(img, pt1, pt2):
    drawline(img, pt1, (pt1[0],pt2[1]))
    drawline(img, (pt1[0], pt2[1]), pt2)
    drawline(img, pt2, (pt2[0], pt1[1]))
    drawline(img, pt1, (pt2[0], pt1[1]))

def inrect(rect, pts):
    for p in pts:
        if p[0] < rect[0][0] or p[1] < rect[0][1] or p[0] > rect[1][0] or p[1] > rect[1][1]:
            return False

    return True

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

def testrect(img, cb, calibration_set, dims, rect):
    drawrect(img, rect[0], rect[1])
    if inrect(rect, cb.points):
        saveCalibrationImage(img, calibration_set, dims)
        return True
    return False

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

  To begin, please put your chessboard close to the camera so the long side is
  horizontal and it fill most of the screen.  Keep it parallel to the camera so it
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
        showText(i,  "Chessboard is " + relPercent(cb, i) + " / 40%, bring it closer")
    elif horizontalTilt(cb) > 0.9:
        showText(i,  "Tip the right or left side of the chessboard towards the camera")
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
        showText(i,  "Chessboard is " + relPercent(cb, i) + " / 40%, bring it closer")
    elif verticalTilt(cb) > 0.9:
        showText(i,  "Tip the top or bottom of the chessboard towards the camera")
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
        showText(i,  "Chessboard is " + relPercent(cb, i) + " / 40%, bring it closer")
    elif verticalTilt(cb) > 0.9 or horizontalTilt(cb) > 0.9:
        showText(i,  "Tip the corner of the chessboard more towards the camera")
    else:
        saveCalibrationImage(i, calibration_set, dims)


def findPlane(cb, i, calibration_set, dims):
    if not cb:
        drawrect(i, (10,10), (i.width - 10, i.height - 10))
        return

    cbwidth = cb.width()
    cbheight = cb.height()
    lcs = len(calibration_set)

    tolerance = 1.2 #20% tolerance

    min_x = 5
    left_x = i.width - cbwidth * tolerance
    mid_min_x = i.width / 2 - cbwidth * tolerance / 2
    mid_max_x = i.width / 2 + cbwidth * tolerance / 2
    right_x = cbwidth * tolerance
    max_x = i.width - 5

    min_y = 5
    top_y = i.height - cbheight * tolerance
    mid_min_y = i.height / 2 - cbheight * tolerance / 2
    mid_max_y = i.height / 2 + cbheight * tolerance / 2
    bottom_y = cbheight * tolerance
    max_y = i.height - 5

    result = False

    grid = (
      #outline the top left corner
      ((min_x, min_y), (right_x, bottom_y)),
      #top middle
      ((mid_min_x, min_y), (mid_max_x, bottom_y)),
      #top right
      ((left_x, min_y), (max_x, bottom_y)),
      #right side middle
      ((left_x, mid_min_y), (max_x, mid_max_y)),
      # center
      ((mid_min_x, mid_min_y), (mid_max_x, mid_max_y)),
      #left middle
      ((min_x, mid_min_y), (right_x, mid_max_y)),
      #left bottom corner
      ((min_x, top_y), (right_x, max_y)),
      #bottom middle,
      ((mid_min_x, top_y), (mid_max_x, max_y)),
      #right bottom
      ((left_x, top_y), (max_x, max_y)) )

    testrect(i, cb, calibration_set, dims, grid[lcs % len(grid)])




def main(camindex = 0, capture_width = 800, capture_height = 600, chessboard_width = 8, chessboard_height = 5, planemode = False, gridsize = 0.029, calibrationFile = "default"):
    global save_location

    if planemode:
        mode = 7
    else:
        mode = 0

    dims = (chessboard_width, chessboard_height)

    cam = Camera(camindex, prop_set = { "width": capture_width, "height": capture_height })
    d = Display((capture_width, capture_height))

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
        elif mode == 7:
            findPlane(cb, i, calibration_set, dims)
            if (len(calibration_set) == 25):
                mode = 5

        if cb:
            cb.draw()

        i.save(d)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description = "Create calibration files for your camera")

    parser.add_argument("--camera", type=int, help="id of the camera", default = 0)
    parser.add_argument("--capturewidth",  type=int, help="width of image to capture", default = 800)
    parser.add_argument("--captureheight",  type=int, help="height of image to capture", default = 600)
    parser.add_argument("--width",  type=int, help="number of chessboard squares wide", default = 8)
    parser.add_argument("--height",  type=int, help="number of chessboard squares high", default = 5)
    parser.add_argument("--planemode", action="store_true", help="calibrate on a single 2D plane", default = False)
    parser.add_argument("--gridsize",  type=float, help="chessboard grid size in real units", default = 0.029)
    parser.add_argument("--calibrationfile", type=str, help="filename to output calibration", default = "default")

    args = parser.parse_args()
    main(args.camera, args.capturewidth, args.captureheight, args.width, args.height, args.planemode, args.gridsize, args.calibrationfile)
