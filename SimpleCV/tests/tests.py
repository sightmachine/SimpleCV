#!/usr/bin/python
# To run this test you need python nose tools installed
# Run test just use:
#   nosetest tests.py
#
# *Note: If you add additional test, please prefix the function name
# to the type of operation being performed.  For instance modifying an
# image, test_image_erode().  If you are looking for lines, then
# test_detection_lines().  This makes it easier to verify visually
# that all the correct test per operation exist

import os, sys
from SimpleCV import * 
from nose.tools import with_setup

#colors
black = Color.BLACK
white = Color.WHITE
red = Color.RED
green = Color.GREEN
blue = Color.BLUE


#images
barcode = "../sampleimages/barcode.png"
testimage = "../sampleimages/9dots4lines.png"
testimage2 = "../sampleimages/aerospace.jpg"
whiteimage = "../sampleimages/white.png"
blackimage = "../sampleimages/black.png"
testimageclr = "../sampleimages/statue_liberty.jpg"
testbarcode = "../sampleimages/barcode.png"
testoutput = "../sampleimages/9d4l.jpg"
tmpimg = "../sampleimages/tmpimg.jpg"
greyscaleimage = "../sampleimages/greyscale.jpg"
logo = "../sampleimages/logo.png"
logo_inverted = "../sampleimages/logo_inverted.png"

#These function names are required by nose test, please leave them as is
def setup_context():
  img = Image(testimage)
  
def destroy_context():
  img = ""

@with_setup(setup_context, destroy_context)
def test_image_loadsave():
  img = Image(testimage)
  img.save(testoutput)  
  if (os.path.isfile(testoutput)):
    os.remove(testoutput)
    pass
  else: 
    assert False
  
def test_image_numpy_constructor():
  img = Image(testimage)
  grayimg = img.grayscale()

  chan3_array = np.array(img.getMatrix())
  chan1_array = np.array(img.getGrayscaleMatrix())

  img2 = Image(chan3_array)
  grayimg2 = Image(chan1_array)

  if (img2[0,0] == img[0,0] and grayimg2[0,0] == grayimg[0,0]):
    pass
  else:
    assert False 


def test_image_bitmap():
  img = Image(testimage)
  bmp = img.getBitmap();
  if bmp.width > 0:
    pass
  else:
    assert False


# Image Class Test

def test_image_stretch():
  img = Image(greyscaleimage)
  stretched = img.stretch(100,200)
  img.save(tmpimg)

  
def test_image_scale():
  img = Image(testimage)
  thumb = img.scale(30,30)
  thumb.save(testoutput)

def test_image_copy():
  img = Image(testimage2)
  copy = img.copy()

  if (img[1,1] != copy[1,1] or img.size() != copy.size()):
    assert False 
  pass
  

def test_image_getitem():
  img = Image(testimage)
  colors = img[1,1]
  if (colors[0] == 255 and colors[1] == 255 and colors[2] == 255):
    pass
  else: 
    assert False

def test_image_getslice():
  img = Image(testimage)
  section = img[1:10,1:10]
  section.save(testoutput)
  pass


def test_image_setitem():
  img = Image(testimage)
  img[1,1] = (0, 0, 0)
  newimg = Image(img.getBitmap())
  colors = newimg[1,1]
  if (colors[0] == 0 and colors[1] == 0 and colors[2] == 0):
    pass
  else:
    assert False

def test_image_setslice():
  img = Image(testimage)
  img[1:10,1:10] = (0,0,0) #make a black box
  newimg = Image(img.getBitmap())
  section = newimg[1:10,1:10]
  for i in range(5):
    colors = section[i,0]
    if (colors[0] != 0 or colors[1] != 0 or colors[2] != 0):
      assert False  
  pass

def test_detection_findCorners():
  img = Image(testimage2)
  corners = img.findCorners(25)
  if (len(corners) == 0):
    assert False 
  corners.draw()
  img.save(testoutput)
  
def test_color_meancolor():
  img = Image(testimage2)
  roi = img[1:50,1:50]
  
  r, g, b = roi.meanColor()

  if (r >= 0 and r <= 255 and g >= 0 and g <= 255 and b >= 0 and b <= 255):
    pass 

def test_image_smooth():
  img = Image(testimage2)
  img.smooth()
  img.smooth('bilateral', (3,3), 4, 1)
  img.smooth('blur', (3, 3))
  img.smooth('median', (3, 3))
  img.smooth('gaussian', (5,5), 0) 
  pass

def test_image_binarize():
  img =  Image(testimage2)
  binary = img.binarize()
  binary2 = img.binarize((60, 100, 200))
  hist = binary.histogram(20)
  hist2 = binary2.histogram(20)
  if (hist[0] + hist[-1] == np.sum(hist) and hist2[0] + hist2[-1] == np.sum(hist2)):
    pass
  else:
    assert False

def test_image_binarize_adaptive():
  img =  Image(testimage2)
  binary = img.binarize(-1)
  hist = binary.histogram(20)  
  if (hist[0] + hist[-1] == np.sum(hist)):
    pass
  else:
    assert False

def test_image_invert():
  img = Image(testimage2)
  clr = img[1,1]
  img = img.invert()

  if (clr[0] == (255 - img[1,1][0])):
    pass
  else:
    assert False


def test_image_size():
  img = Image(testimage2)
  (width, height) = img.size()
  if type(width) == int and type(height) == int and width > 0 and height > 0:
    pass
  else:
    assert False

def test_image_drawing():
  img = Image(testimageclr)
  img.drawCircle((5, 5), 3)
  img.drawLine((5, 5), (5, 8))
  
def test_image_splitchannels():  
  img = Image(testimageclr)
  (r, g, b) = img.splitChannels(True)
  (red, green, blue) = img.splitChannels()
  pass

def test_image_histogram():
  img = Image(testimage2)
  h = img.histogram(25)

  for i in h:
    if type(i) != int:
      assert False

  pass

def test_detection_lines():
  img = Image(testimage2)
  lines = img.findLines()

  lines.draw()
  img.save(testoutput)

def test_detection_feature_measures():
    img = Image(testimage2)
  
    fs = FeatureSet()
    fs.append(Corner(img, 5, 5))
    fs.append(Line(img, ((2, 2), (3,3))))
    print(fs)
    #if BLOBS_ENABLED:
    bm = BlobMaker()
    result = bm.extract(img)
    fs.extend(result)
    print(fs)
    #fs.append(img.findBlobs()[0])

    #if ZXING_ENABLED:
    # fake_barcode = Barcode(img, zxing.BarCode("""
    #file:default.png (format: FAKE_DATA, type: TEXT):
    #Raw result:
    #foo-bar|the bar of foo
    #Parsed result:
    #foo-bar 
    #the bar of foo
    #Also, there were 4 result points:
    #  Point 0: (24.0,18.0)
    #  Point 1: (21.0,196.0)
    #  Point 2: (201.0,198.0)
    #  Point 3: (205.23952,21.0)
    #"""))
    #fs.append(fake_barcode) 

    for f in fs:
        a = f.area()
        l = f.length()
        c = f.meanColor()
        d = f.colorDistance()
        th = f.angle()
        pts = f.coordinates()
        dist = f.distanceFrom() #distance from center of image 

    
    fs2 = fs.sortAngle()
    fs3 = fs.sortLength()
    fs4 = fs.sortColorDistance()
    fs5 = fs.sortArea()
    fs1 = fs.sortDistance() 

def test_detection_blobs():
    if not BLOBS_ENABLED:
      return None 
    img = Image(testbarcode)
  
    bm = BlobMaker()
    blobs = bm.extract(img)

    blobs[0].draw()
    img.save(testoutput)  

    pass

def test_detection_blobs_adaptive():
    if not BLOBS_ENABLED:
        return None
    img = Image(testimage)
    bm = BlobMaker()
    result = bm.extract(img, threshval=-1)
    result[0].draw()
    img.save(testoutput)  
    pass


def test_detection_barcode():
  if not ZXING_ENABLED:
    return None

  nocode = Image(testimage).findBarcode()
  if nocode: #we should find no barcode in our test image 
    assert False
  code = Image(testbarcode).findBarcode() 
  
  if code.points:
    pass
    
def test_detection_x():
  tmpX = Image(testimage).findLines().x()[0]

  if (tmpX > 0 and Image(testimage).size()[0]):
    pass
  else:
    assert False

def test_detection_y():
  tmpY = Image(testimage).findLines().y()[0]

  if (tmpY > 0 and Image(testimage).size()[0]):
    pass
  else:
    assert False

def test_detection_area():
    img = Image(testimage2)
    bm = BlobMaker()
    result = bm.extract(img)
    area_val = result[0].area()
  
    if(area_val > 0):
        pass
    else:
        assert False

def test_detection_angle():
  angle_val = Image(testimage).findLines().angle()[0]

def test_image():
  img = Image(testimage)
  if(isinstance(img, Image)):
    pass
  else:
    assert False

def test_color_colordistance():
  img = Image(blackimage)
  (r,g,b) = img.splitChannels()
  avg = img.meanColor()
  
  c1 = Corner(img, 1, 1)
  c2 = Corner(img, 1, 2)
  if (c1.colorDistance(c2.meanColor()) != 0):
    assert False
  
  if (c1.colorDistance((0,0,0)) != 0):
    assert False

  if (c1.colorDistance((0,0,255)) != 255):
    assert False

  if (c1.colorDistance((255,255,255)) != sqrt(255**2 * 3)):
    assert False
    
  pass
  
def test_detection_length():
  img = Image(testimage)
  val = img.findLines().length()

  if (val == None):
    assert False
  if (not isinstance(val, np.ndarray)):
    assert False
  if (len(val) < 0):
    assert False

  pass


  
  
def test_detection_sortangle():
  img = Image(testimage)
  val = img.findLines().sortAngle()

  if(val[0].x < val[1].x):
    pass
  else:
    assert False
    
def test_detection_sortarea():
    img = Image(testimage)
    bm = BlobMaker()
    result = bm.extract(img)
    val = result.sortArea()
  #FIXME: Find blobs may appear to be broken. Returning type none

def test_detection_sortLength():
  img = Image(testimage)
  val = img.findLines().sortLength()
  #FIXME: Length is being returned as euclidean type, believe we need a universal type, either Int or scvINT or something.
 
#def test_distanceFrom():
#def test_sortColorDistance():
#def test_sortDistance():

def test_image_add():
  imgA = Image(blackimage)
  imgB = Image(whiteimage)

  imgC = imgA + imgB

def test_color_curve_HSL():
  y = np.array([[0,0],[64,128],[192,128],[255,255]])  #These are the weights 
  curve = ColorCurve(y)
  img = Image(testimage)
  img2 = img.applyHLSCurve(curve,curve,curve)
  img3 = img-img2
  c = img3.meanColor()
  print(c)
  if( c[0] > 2.0 or c[1] > 2.0 or c[2] > 2.0 ): #there may be a bit of roundoff error 
    assert False

def test_color_curve_RGB():
  y = np.array([[0,0],[64,128],[192,128],[255,255]])  #These are the weights 
  curve = ColorCurve(y)
  img = Image(testimage)
  img2 = img.applyRGBCurve(curve,curve,curve)
  img3 = img-img2
  c = img3.meanColor()
  if( c[0] > 1.0 or c[1] > 1.0 or c[2] > 1.0 ): #there may be a bit of roundoff error 
    assert False

def test_color_curve_GRAY():
  y = np.array([[0,0],[64,128],[192,128],[255,255]])  #These are the weights 
  curve = ColorCurve(y)
  img = Image(testimage)
  gray = img.grayscale()
  img2 = img.applyIntensityCurve(curve)
  print(gray.meanColor())
  print(img2.meanColor())
  g=gray.meanColor()
  i2=img2.meanColor()
  if( g[0]-i2[0] > 1 ): #there may be a bit of roundoff error 
    assert False

def test_image_dilate():
  img=Image(barcode)
  img2 = img.dilate(20)
  c=img2.meanColor()
  print(c)
  if( c[0] < 254 or c[1] < 254 or c[2] < 254 ):
    assert False;

def test_image_erode():
  img=Image(barcode)
  img2 = img.erode(100)
  c=img2.meanColor()
  print(c)
  if( c[0] > 0 or c[1] > 0 or c[2] > 0 ):
    assert False;
  
def test_image_morph_open():
  img = Image(barcode);
  erode= img.erode()
  dilate = erode.dilate()
  result = img.morphOpen()
  test = result-dilate
  c=test.meanColor()
  print(c)
  if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    assert False;

def test_image_morph_close():
  img = Image(barcode)
  dilate = img.dilate()
  erode = dilate.erode()
  result = img.morphClose()
  test = result-erode
  c=test.meanColor()
  print(c)
  if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    assert False;

def test_image_morph_grad():
  img = Image(barcode)
  dilate = img.dilate()
  erode = img.erode()
  dif = dilate-erode
  result = img.morphGradient()
  test = result-dif
  c=test.meanColor()
  if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    assert False

def test_image_rotate_fixed():
  img = Image(testimage2)
  img2=img.rotate(180, scale = 1)
  img3=img.flipVertical()
  img4=img3.flipHorizontal()
  test = img4-img2
  c=test.meanColor()
  print(c)
  if( c[0] > 5 or c[1] > 5 or c[2] > 5 ):
    assert False


def test_image_rotate_full():
  img = Image(testimage2)
  img2=img.rotate(180,"full",scale = 1)
  c1=img.meanColor()
  c2=img2.meanColor()
  if( abs(c1[0]-c2[0]) > 5 or abs(c1[1]-c2[1]) > 5 or abs(c1[2]-c2[2]) > 5 ):
    assert False

def test_image_shear_warp():
  img = Image(testimage2)
  dst =  ((img.width/2,0),(img.width-1,img.height/2),(img.width/2,img.height-1))
  s = img.shear(dst)
  color = s[0,0] 
  if (color != (0,0,0)):
    assert False

  dst = ((img.width*0.05,img.height*0.03),(img.width*0.9,img.height*0.1),(img.width*0.8,img.height*0.7),(img.width*0.2,img.height*0.9))
  w = img.warp(dst)
  color = s[0,0] 
  if (color != (0,0,0)):
    assert False

  pass

def test_image_affine():
  img = Image(testimage2)
  src =  ((0,0),(img.width-1,0),(img.width-1,img.height-1))
  dst =  ((img.width/2,0),(img.width-1,img.height/2),(img.width/2,img.height-1))
  aWarp = cv.CreateMat(2,3,cv.CV_32FC1)
  cv.GetAffineTransform(src,dst,aWarp)
  atrans = img.transformAffine(aWarp)

  aWarp2 = np.array(aWarp)
  atrans2 = img.transformAffine(aWarp2)
  test = atrans-atrans2
  c=test.meanColor()
  if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    assert False

def test_image_perspective():
  img = Image(testimage2)
  src = ((0,0),(img.width-1,0),(img.width-1,img.height-1),(0,img.height-1))
  dst = ((img.width*0.05,img.height*0.03),(img.width*0.9,img.height*0.1),(img.width*0.8,img.height*0.7),(img.width*0.2,img.height*0.9))
  pWarp = cv.CreateMat(3,3,cv.CV_32FC1)
  cv.GetPerspectiveTransform(src,dst,pWarp)
  ptrans = img.transformPerspective(pWarp)

  pWarp2 = np.array(pWarp)
  ptrans2 = img.transformPerspective(pWarp2)

  
  test = ptrans-ptrans2
  c=test.meanColor()

  if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    assert False
    
def test_image_horz_scanline():
  img = Image(logo)
  sl = img.getHorzScanline(10)
  if( sl.shape[0]!=img.width or sl.shape[1]!=3 ):
    assert False

def test_image_vert_scanline():
  img = Image(logo)
  sl = img.getVertScanline(10)
  if( sl.shape[0]!=img.height or sl.shape[1]!=3 ):
    assert False
    
def test_image_horz_scanline_gray():
  img = Image(logo)
  sl = img.getHorzScanlineGray(10)
  if( sl.shape[0]!=img.width or sl.shape[1]!=1 ):
    assert False

def test_image_vert_scanline_gray():
  img = Image(logo)
  sl = img.getVertScanlineGray(10)
  if( sl.shape[0]!=img.height or sl.shape[1]!=1 ):
    assert False

def test_image_get_pixel():
    img = Image(logo)
    px = img.getPixel(0,0)
    if(px[0] != 0 or px[1] != 0 or px[2] != 0 ):
      assert False
      
def test_image_get_gray_pixel():
    img = Image(logo)
    px = img.getGrayPixel(0,0)
    if(px != 0):
      assert False

      
def test_camera_calibration():
  fakeCamera = FrameSource()
  path = "../sampleimages/CalibImage"
  ext = ".png"
  imgs = []
  for i in range(0,10):
    fname = path+str(i)+ext
    img = Image(fname)
    imgs.append(img)

  fakeCamera.calibrate(imgs)
  #we're just going to check that the function doesn't puke
  mat = fakeCamera.getCameraMatrix()
  if( type(mat) != cv.cvmat ):
    assert False
  #we're also going to test load in save in the same pass 
  matname = "TestCalibration"
  if( False == fakeCamera.saveCalibration(matname)):
    assert False
  if( False == fakeCamera.loadCalibration(matname)):
    assert False

def test_camera_undistort():
  fakeCamera = FrameSource()
  fakeCamera.loadCalibration("Default")
  img = Image("../sampleimages/CalibImage0.png") 
  img2 = fakeCamera.undistort(img)
  if( not img2 ): #right now just wait for this to return 
    assert False
    
def test_image_crop():
  img = Image(logo)
  x = 5
  y = 6
  w = 10
  h = 20
  crop = img.crop(x,y,w,h)
  crop2 = img[x:(x+w),y:(y+h)]
  diff = crop-crop2;
  c=diff.meanColor()
  if( c[0] > 0 or c[1] > 0 or c[2] > 0 ):
    assert False

def test_image_region_select():
  img = Image(logo)
  x1 = 0
  y1 = 0
  x2 = img.width
  y2 = img.height
  crop = img.regionSelect(x1,y1,x2,y2)
  diff = crop-img;
  c=diff.meanColor()
  if( c[0] > 0 or c[1] > 0 or c[2] > 0 ):
    assert False

def test_image_subtract():
  imgA = Image(logo)
  imgB = Image(logo_inverted)

  imgC = imgA - imgB

def test_image_negative():
  imgA = Image(logo)

  imgB = -imgA
 
def test_image_divide():
  imgA = Image(logo)
  imgB = Image(logo_inverted)

  imgC = imgA / imgB
  
def test_image_and():
  imgA = Image(logo)
  imgB = Image(logo_inverted)

  imgC = imgA and imgB
  
  
def test_image_or():
  imgA = Image(logo)
  imgB = Image(logo_inverted)

  imgC = imgA or imgB

def test_image_edgemap():
  imgA = Image(logo)
  imgB = imgA._getEdgeMap()


def test_color_colormap_build():
  cm = ColorModel()
  cm.add(Image(testimage))
  cm.add((127,127,127))
  if(cm.contains((127,127,127))):
    cm.remove((127,127,127))
  else:
    assert False
  img = cm.threshold(Image(testimage))
  c=img.meanColor()
  if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    assert False
  cm.save("temp.txt")
  cm2 = ColorModel()
  cm2.load("temp.txt")
  img = cm2.threshold(Image(testimage))
  c=img.meanColor()
  if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    assert False


def test_feature_height():
  imgA = Image(logo)
  lines = imgA.findLines(1)
  heights = lines.height()

  if(len(heights) <= 0 ):
    assert False
  else:
    pass

def test_feature_width():
  imgA = Image(logo)
  lines = imgA.findLines(1)
  widths = lines.width()

  if(len(widths) <= 0):
    assert False
  else:
    pass

def test_feature_crop():
  imgA = Image(logo)
  lines = imgA.findLines(1)
  croppedImages = lines.crop()

  if(len(croppedImages) <= 0):
    assert False
  else:
    pass

    
def test_color_conversion_func_BGR():
  #we'll just go through the space to make sure nothing blows up
  img = Image(testimage)
  bgr = img.toBGR()
  rgb = img.toRGB()
  hls = img.toHLS()
  hsv = img.toHSV()
  xyz = img.toXYZ()
  
  foo = bgr.toBGR()
  foo = bgr.toRGB()
  foo = bgr.toHLS()
  foo = bgr.toHSV()
  foo = bgr.toXYZ()
  
  
def test_color_conversion_func_RGB():
  img = Image(testimage)
  if( not img.isBGR() ):
    assert False
  rgb = img.toRGB()
  
  foo = rgb.toBGR()
  if( not foo.isBGR() ):
    assert False   
  
  foo = rgb.toRGB()
  if( not foo.isRGB() ):
    assert False   
  
  foo = rgb.toHLS()
  if( not foo.isHLS() ):
    assert False     
  
  foo = rgb.toHSV()
  if( not foo.isHSV() ):
    assert False 
  
  foo = rgb.toXYZ()
  if( not foo.isXYZ() ):
    assert False 

def test_color_conversion_func_HSV():
  img = Image(testimage)
  hsv = img.toHSV()
  foo = hsv.toBGR()
  foo = hsv.toRGB()
  foo = hsv.toHLS()
  foo = hsv.toHSV()
  foo = hsv.toXYZ()
  
def test_color_conversion_func_HLS():
  img = Image(testimage)
  hls = img.toHLS()
  foo = hls.toBGR()
  foo = hls.toRGB()
  foo = hls.toHLS()
  foo = hls.toHSV()
  foo = hls.toXYZ()   

def test_color_conversion_func_XYZ():
  img = Image(testimage)
  xyz = img.toXYZ()  
  foo = xyz.toBGR()
  foo = xyz.toRGB()
  foo = xyz.toHLS()
  foo = xyz.toHSV()
  foo = xyz.toXYZ()  

def test_blob_maker():
    img = Image("../sampleimages/blockhead.png")
    blobber = BlobMaker()
    results = blobber.extract(img)
    print(len(results))
    if( len(results) != 7 ):
        assert False
        
def test_blob_holes():
    img = Image("../sampleimages/blockhead.png")
    blobber = BlobMaker()
    blobs = blobber.extract(img)
    count = 0
    for b in blobs:
        if( b.mHoleContour is not None ):
            count = count + len(b.mHoleContour)
    if( count != 7 ):
        assert False
        
def test_blob_hull():
    img = Image("../sampleimages/blockhead.png")
    blobber = BlobMaker()
    blobs = blobber.extract(img)
    for b in blobs:
        if( len(b.mConvexHull) < 3 ):
            assert False

def test_blob_data():
    img = Image("../sampleimages/blockhead.png")
    blobber = BlobMaker()
    blobs = blobber.extract(img)
    for b in blobs:
        if(b.mArea > 0):
            pass
        if(b.mPerimeter > 0):
            pass
        if(sum(b.mAvgColor) > 0 ):
            pass
        if(sum(b.mBoundingBox) > 0 ):
            pass
        if(b.m00 is not 0 and
           b.m01 is not 0 and
           b.m10 is not 0 and
           b.m11 is not 0 and
           b.m20 is not 0 and
           b.m02 is not 0 and
           b.m21 is not 0 and
           b.m12 is not 0 ):
            pass
        if(sum(b.mHuMoments) > 0):
            pass
        
def test_blob_render():
    img = Image("../sampleimages/blockhead.png")
    blobber = BlobMaker()
    blobs = blobber.extract(img)
    dl = DrawingLayer((img.width,img.height))
    reimg = DrawingLayer((img.width,img.height))
    for b in blobs:        
        b.draw(color=Color.RED, alpha=128)
        b.drawHoles(width=2,color=Color.BLUE)
        b.drawHull(color=Color.ORANGE,width=2)
        b.draw(color=Color.RED, alpha=128,layer=dl)
        b.drawHoles(width=2,color=Color.BLUE,layer=dl)
        b.drawHull(color=Color.ORANGE,width=2,layer=dl)
        b.drawMaskToLayer(reimg,offset=b.topLeftCorner())
    pass

def test_blob_methods():
    img = Image("../sampleimages/blockhead.png")
    blobber = BlobMaker()
    blobs = blobber.extract(img)
    BL = (img.width,img.height)
    first = blobs[0]
    for b in blobs:
        b.width()
        b.height()
        b.area()
        b.maxX()
        b.minX()
        b.maxY()
        b.minY()
        b.minRectWidth()
        b.minRectHeight()
        b.minRectX()
        b.minRectY()
        b.aspectRatio()
        b.angle()
        if(not b.contains((b.x,b.y))):
           assert False
        if(b.below((0,0))):
           assert False
        if(not b.left((0,0))):
            assert False
        if(b.above(BL)):
            assert False
        if( not b.right(BL)):
            assert False
        b.overlaps(first)
        b.above(first)
        b.below(first)
        b.left(first)
        b.right(first)
        b.contains(first)
        b.overlaps(first)
        
#def test_get_holes()
#def test 
