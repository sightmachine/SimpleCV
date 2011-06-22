#!/usr/bin/python
# *To run this test you need python nose tools installed
# Run test just use:
#   nosetest tests.py

import os, sys
from SimpleCV import * 
from nose.tools import with_setup

#colors
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)


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


def setup_context():
  img = Image(testimage)
  
def destroy_context():
  img = ""

@with_setup(setup_context, destroy_context)
def test_loadsave():
  img = Image(testimage)
  img.save(testoutput)  
  if (os.path.isfile(testoutput)):
    os.remove(testoutput)
    pass
  else: 
    assert False
  
def test_numpy_constructor():
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


def test_bitmap():
  img = Image(testimage)
  bmp = img.getBitmap();
  if bmp.width > 0:
    pass
  else:
    assert False

#TODO: get this test working
#def test_matrix():
#  img = Image(testimage)
#  m = img.getMatrix()
#  if (m.rows == img.getBitmap().width):
#    pass
#  assert False

def test_stretch():
  img = Image(greyscaleimage)
  stretched = img.stretch(100,200)
  img.save(tmpimg)

  
def test_scale():
  img = Image(testimage)
  thumb = img.scale(30,30)
  thumb.save(testoutput)

def test_copy():
  img = Image(testimage2)
  copy = img.copy()

  if (img[1,1] != copy[1,1] or img.size() != copy.size()):
    assert False 
  pass
  

def test_getitem():
  img = Image(testimage)
  colors = img[1,1]
  if (colors[0] == 255 and colors[1] == 255 and colors[2] == 255):
    pass
  else: 
    assert False

def test_getslice():
  img = Image(testimage)
  section = img[1:10,1:10]
  section.save(testoutput)
  pass


def test_setitem():
  img = Image(testimage)
  img[1,1] = (0, 0, 0)
  newimg = Image(img.getBitmap())
  colors = newimg[1,1]
  if (colors[0] == 0 and colors[1] == 0 and colors[2] == 0):
    pass
  else:
    assert False

def test_setslice():
  img = Image(testimage)
  img[1:10,1:10] = (0,0,0) #make a black box
  newimg = Image(img.getBitmap())
  section = newimg[1:10,1:10]
  for i in range(5):
    colors = section[i,0]
    if (colors[0] != 0 or colors[1] != 0 or colors[2] != 0):
      assert False  
  pass

def test_findCorners():
  img = Image(testimage2)
  corners = img.findCorners(25)
  if (len(corners) == 0):
    assert False 
  corners.draw()
  img.save(testoutput)
  
def test_meancolor():
  img = Image(testimage2)
  roi = img[1:50,1:50]
  
  r, g, b = roi.meanColor()

  if (r >= 0 and r <= 255 and g >= 0 and g <= 255 and b >= 0 and b <= 255):
    pass 

def test_smooth():
  img = Image(testimage2)
  img.smooth()
  img.smooth('bilateral', (3,3), 4, 1)
  img.smooth('blur', (3, 3))
  img.smooth('median', (3, 3))
  img.smooth('gaussian', (5,5), 0) 
  pass

def test_binarize():
  img =  Image(testimage2)
  binary = img.binarize()
  binary2 = img.binarize((60, 100, 200))
  hist = binary.histogram(20)
  hist2 = binary2.histogram(20)
  if (hist[0] + hist[-1] == np.sum(hist) and hist2[0] + hist2[-1] == np.sum(hist2)):
    pass
  else:
    assert False

def test_invert():
  img = Image(testimage2)
  clr = img[1,1]
  img = img.invert()

  if (clr[0] == (255 - img[1,1][0])):
    pass
  else:
    assert False


def test_size():
  img = Image(testimage2)
  (width, height) = img.size()
  if type(width) == int and type(height) == int and width > 0 and height > 0:
    pass
  else:
    assert False

def test_drawing():
  img = Image(testimageclr)
  img.drawCircle((5, 5), 3)
  img.drawLine((5, 5), (5, 8))
  
def test_splitchannels():  
  img = Image(testimageclr)
  (r, g, b) = img.splitChannels(True)
  (red, green, blue) = img.splitChannels()
  pass

def test_histogram():
  img = Image(testimage2)
  h = img.histogram(25)

  for i in h:
    if type(i) != int:
      assert False

  pass

def test_lines():
  img = Image(testimage2)
  lines = img.findLines()

  lines.draw()
  img.save(testoutput)

def test_feature_measures():
  img = Image(testimage2)
  
  fs = FeatureSet()
  fs.append(Corner(img, 5, 5))
  fs.append(Line(img, ((2, 2), (3,3))))

  if BLOBS_ENABLED:
    fs.append(img.findBlobs()[0])

  if ZXING_ENABLED:
    fake_barcode = Barcode(img, zxing.BarCode("""
file:default.png (format: FAKE_DATA, type: TEXT):
Raw result:
foo-bar|the bar of foo
Parsed result:
foo-bar 
the bar of foo
Also, there were 4 result points:
  Point 0: (24.0,18.0)
  Point 1: (21.0,196.0)
  Point 2: (201.0,198.0)
  Point 3: (205.23952,21.0)
"""))
    fs.append(fake_barcode) 

  for f in fs:
    a = f.area()
    l = f.length()
    c = f.meanColor()
    d = f.colorDistance()
    th = f.angle()
    pts = f.coordinates()
    dist = f.distanceFrom() #distance from center of image 

  fs1 = fs.sortDistance()
  fs2 = fs.sortAngle()
  fs3 = fs.sortLength()
  fs4 = fs.sortColorDistance()
  fs5 = fs.sortArea()
  

def test_blobs():
  if not BLOBS_ENABLED:
    return None 
  img = Image(testbarcode)
  blobs = img.findBlobs()

  blobs[0].draw((0, 255, 0))
  img.save(testoutput)  

  pass




def test_barcode():
  if not ZXING_ENABLED:
    return None

  nocode = Image(testimage).findBarcode()
  if nocode: #we should find no barcode in our test image 
    assert False
  code = Image(testbarcode).findBarcode() 
  
  if code.points:
    pass
    
def test_x():
  tmpX = Image(testimage).findLines().x()[0]

  if (tmpX > 0 and Image(testimage).size()[0]):
    pass
  else:
    assert False

def test_y():
  tmpY = Image(testimage).findLines().y()[0]

  if (tmpY > 0 and Image(testimage).size()[0]):
    pass
  else:
    assert False

def test_area():
  area_val = Image(testimage).findBlobs().area()[0]
  
  if(area_val > 0):
    pass
  else:
    assert False

def test_angle():
  angle_val = Image(testimage).findLines().angle()[0]

def test_image():
  img = Image(testimage)
  if(isinstance(img, Image)):
    pass
  else:
    assert False

def test_colordistance():
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
  
def test_length():
  img = Image(testimage)
  val = img.findLines().length()

  if (val == None):
    assert False
  if (not isinstance(val, np.ndarray)):
    assert False
  if (len(val) < 0):
    assert False

  pass


  
  
def test_sortangle():
  img = Image(testimage)
  val = img.findLines().sortAngle()

  if(val[0].x < val[1].x):
    pass
  else:
    assert False
    
def test_sortarea():
  img = Image(testimage)
  val = img.findBlobs().sortArea()
  #FIXME: Find blobs may appear to be broken. Returning type none

def test_sortLength():
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

def test_dilate():
  img=Image(barcode)
  img2 = img.dilate(20)
  c=img2.meanColor()
  print(c)
  if( c[0] < 254 or c[1] < 254 or c[2] < 254 ):
    assert False;

def test_erode():
  img=Image(barcode)
  img2 = img.erode(100)
  c=img2.meanColor()
  print(c)
  if( c[0] > 0 or c[1] > 0 or c[2] > 0 ):
    assert False;
  
def test_morph_open():
  img = Image(barcode);
  erode= img.erode()
  dilate = erode.dilate()
  result = img.morphOpen()
  test = result-dilate
  c=test.meanColor()
  print(c)
  if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    assert False;

def test_morph_close():
  img = Image(barcode)
  dilate = img.dilate()
  erode = dilate.erode()
  result = img.morphClose()
  test = result-erode
  c=test.meanColor()
  print(c)
  if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    assert False;

def test_morph_grad():
  img = Image(barcode)
  dilate = img.dilate()
  erode = img.erode()
  dif = dilate-erode
  result = img.morphGradient()
  test = result-dif
  c=test.meanColor()
  if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    assert False

def test_rotate_fixed():
  img = Image(testimage2)
  img2=img.rotate(180, scale = 1)
  img3=img.flipVertical()
  img4=img3.flipHorizontal()
  test = img4-img2
  c=test.meanColor()
  print(c)
  if( c[0] > 5 or c[1] > 5 or c[2] > 5 ):
    assert False


def test_rotate_full():
  img = Image(testimage2)
  img2=img.rotate(180,"full",scale = 1)
  c1=img.meanColor()
  c2=img2.meanColor()
  if( abs(c1[0]-c2[0]) > 5 or abs(c1[1]-c2[1]) > 5 or abs(c1[2]-c2[2]) > 5 ):
    assert False

def test_shear_warp():
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

def test_affine():
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

def test_perspective():
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
    
def test_horz_scanline():
  img = Image(logo)
  sl = img.getHorzScanline(10)
  if( sl.shape[0]!=img.width or sl.shape[1]!=3 ):
    assert False

def test_vert_scanline():
  img = Image(logo)
  sl = img.getVertScanline(10)
  if( sl.shape[0]!=img.height or sl.shape[1]!=3 ):
    assert False
    
def test_horz_scanline_gray():
  img = Image(logo)
  sl = img.getHorzScanlineGray(10)
  if( sl.shape[0]!=img.width or sl.shape[1]!=1 ):
    assert False

def test_vert_scanline_gray():
  img = Image(logo)
  sl = img.getVertScanlineGray(10)
  if( sl.shape[0]!=img.height or sl.shape[1]!=1 ):
    assert False

def test_get_pixel():
    img = Image(logo)
    px = img.getPixel(0,0)
    if(px[0] != 0 or px[1] != 0 or px[2] != 0 ):
      assert False
      
def test_get_gray_pixel():
    img = Image(logo)
    px = img.getGrayPixel(0,0)
    if(px != 0):
      assert False
      
def test_calibration():
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

def test_undistort():
  fakeCamera = FrameSource()
  fakeCamera.loadCalibration("Default")
  img = Image("../sampleimages/CalibImage0.png") 
  img2 = fakeCamera.undistort(img)
  if( not img2 ): #right now just wait for this to return 
    assert False
    
def test_crop():
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

def test_region_select():
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

def test_subtract():
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
