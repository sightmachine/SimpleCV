# /usr/bin/python
# To run this test you need python nose tools installed
# Run test just use:
#   nosetest tests.py
#
# *Note: If you add additional test, please prefix the function name
# to the type of operation being performed.  For instance modifying an
# image, test_image_erode().  If you are looking for lines, then
# test_detection_lines().  This makes it easier to verify visually
# that all the correct test per operation exist

import os, sys, pickle
from SimpleCV import * 
from nose.tools import with_setup

VISUAL_TEST = True
SHOW_WARNING_TESTS = False  # show that warnings are working - tests will pass but warnings are generated. 

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
ocrimage = "../sampleimages/ocr-test.png"
circles = "../sampleimages/circles.png"
webp = "../sampleimages/simplecv.webp"

#alpha masking images
topImg = "../sampleimages/RatTop.png"
bottomImg = "../sampleimages/RatBottom.png"
maskImg = "../sampleimages/RatMask.png"
alphaMaskImg = "../sampleimages/RatAlphaMask.png"
alphaSrcImg = "../sampleimages/GreenMaskSource.png"


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
  if(stretched == None):
      assert False

  
def test_image_scale():
  img = Image(testimage)
  thumb = img.scale(30,30)
  if(thumb == None):
      assert False

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
  if(section == None):
      assert False



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
  img.smooth('bilateral', (3,3), 4, 1,grayscale=False)
  img.smooth('blur', (3, 3),grayscale=True)
  img.smooth('median', (3, 3),grayscale=True)
  img.smooth('gaussian', (5,5), 0,grayscale=True) 

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

    if(lines == 0 or lines == None):
        assert False

def test_detection_feature_measures():
    img = Image(testimage2)
  
    fs = FeatureSet()
    fs.append(Corner(img, 5, 5))
    fs.append(Line(img, ((2, 2), (3,3))))
    print(fs)
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
    img = Image(testbarcode)
    blobs = img.findBlobs()
    if blobs == None:
        assert False
        

def test_detection_blobs_adaptive():
    img = Image(testimage)
    blobs = img.findBlobs(-1, threshblocksize=99)
    if blobs == None:
        assert False


def test_detection_barcode():
  if not ZXING_ENABLED:
    return None

  if( SHOW_WARNING_TESTS ):
    nocode = Image(testimage).findBarcode()
    if nocode: #we should find no barcode in our test image 
      assert False
    code = Image(testbarcode).findBarcode() 
    if code.points:
      pass
  else:
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
00 
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
    print(px)
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
  crop6 = img.crop(0,0,10,10)
  if( SHOW_WARNING_TESTS ):
    crop7 = img.crop(0,0,-10,10)
    crop8 = img.crop(-50,-50,10,10)
    crop3 = img.crop(-3,-3,10,20)
    crop4 = img.crop(-10,10,20,20,centered=True)
    crop5 = img.crop(-10,-10,20,20)
 
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
        if(sum(b.mHu) > 0):
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
        b.getBlobImage()
        b.getBlobMask()
        b.getHullImage()
        b.getHullMask()
        b.rectifyMajorAxis()
        b.getBlobImage()
        b.getBlobMask()
        b.getHullImage()
        b.getHullMask()
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

def test_image_convolve():
    img = Image(testimageclr)
    kernel = np.array([[0,0,0],[0,1,0],[0,0,0]])
    img2 = img.convolve(kernel,center=(2,2))
    c=img.meanColor()
    d=img2.meanColor()
    e0 = abs(c[0]-d[0])
    e1 = abs(c[1]-d[1])
    e2 = abs(c[2]-d[2])
    if( e0 > 1 or e1 > 1 or e2 > 1 ):
        assert False


def test_detection_ocr():
    img = Image(ocrimage)
    print "TESTING OCR"
    foundtext = img.readText()
    print foundtext
    if(len(foundtext) <= 1):
        assert False
    else:
        pass
        
def test_template_match():
    source = Image("../sampleimages/templatetest.png")
    template = Image("../sampleimages/template.png")
    t = 4
    fs = source.findTemplate(template,threshold=t)
    pass


def test_image_intergralimage():
    img = Image(logo)
    ii = img.integralImage()
    if len(ii) == 0:
        assert False


def test_segmentation_diff():
    segmentor = DiffSegmentation()
    i1 = Image("logo")
    i2 = Image("logo_inverted")
    segmentor.addImage(i1)
    segmentor.addImage(i2)
    blobs = segmentor.getSegmentedBlobs()
    if(blobs == None):
        assert False
    else:
        pass

def test_segmentation_running():
    segmentor = RunningSegmentation()
    i1 = Image("logo")
    i2 = Image("logo_inverted")
    segmentor.addImage(i1)
    segmentor.addImage(i2)
    blobs = segmentor.getSegmentedBlobs()
    if(blobs == None):
        assert False
    else:
        pass

def test_segmentation_color():
    segmentor = ColorSegmentation()
    i1 = Image("logo")
    i2 = Image("logo_inverted")
    segmentor.addImage(i1)
    segmentor.addImage(i2)
    blobs = segmentor.getSegmentedBlobs()
    if(blobs == None):
        assert False
    else:
        pass

def test_embiggen():
  img = Image(logo)
  if VISUAL_TEST:
    img.embiggen(size=(100,100),color=Color.RED).save("embiggen_centered.png")
    img.embiggen(size=(100,100),color=Color.RED,pos=(30,30)).save("embiggen_centered2.png")
    #~ img.embiggen(size=(100,100),color=Color.RED,pos=(150,150)) #should warn

    img.embiggen(size=(100,100),color=Color.RED,pos=(-20,-20)).save("embiggen_tlcorner.png")
    img.embiggen(size=(100,100),color=Color.RED,pos=(30,-20)).save("embiggen_tcenter.png")
    img.embiggen(size=(100,100),color=Color.RED,pos=(60,-20)).save("embiggen_trcorner.png")
    img.embiggen(size=(100,100),color=Color.RED,pos=(60,30)).save("embiggen_right.png")

    img.embiggen(size=(100,100),color=Color.RED,pos=(80,80)).save("embiggen_brcorner.png")
    img.embiggen(size=(100,100),color=Color.RED,pos=(30,80)).save("embiggen_bottom.png")
    img.embiggen(size=(100,100),color=Color.RED,pos=(-20,80)).save("embiggen_blcorner.png")
    img.embiggen(size=(100,100),color=Color.RED,pos=(-20,30)).save("embiggen_left.png")
  else:
    img.embiggen(size=(100,100),color=Color.RED)
    img.embiggen(size=(100,100),color=Color.RED,pos=(30,30))
    #~ img.embiggen(size=(100,100),color=Color.RED,pos=(150,150)) #should warn

    img.embiggen(size=(100,100),color=Color.RED,pos=(-20,-20))
    img.embiggen(size=(100,100),color=Color.RED,pos=(30,-20))
    img.embiggen(size=(100,100),color=Color.RED,pos=(60,-20))
    img.embiggen(size=(100,100),color=Color.RED,pos=(60,30))

    img.embiggen(size=(100,100),color=Color.RED,pos=(80,80))
    img.embiggen(size=(100,100),color=Color.RED,pos=(30,80))
    img.embiggen(size=(100,100),color=Color.RED,pos=(-20,80))
    img.embiggen(size=(100,100),color=Color.RED,pos=(-20,30))
    
  pass

def test_createBinaryMask():
  img2 = Image(logo)
  if VISUAL_TEST:
    img2.createBinaryMask(color1=(0,100,100),color2=(255,200,200)).save("BinaryMask1.png")
    img2.createBinaryMask(color1=(0,0,0),color2=(128,128,128)).save('BinaryMask2.png')
    img2.createBinaryMask(color1=(0,0,128),color2=(255,255,255)).save('BinaryMask3.png')
  
  else:
    img2.createBinaryMask(color1=(0,100,100),color2=(255,200,200))
    img2.createBinaryMask(color1=(0,0,0),color2=(128,128,128))
    img2.createBinaryMask(color1=(0,0,128),color2=(255,255,255))
        
  pass

def test_applyBinaryMask():
  img = Image(logo)
  mask = img.createBinaryMask(color1=(0,128,128),color2=(255,255,255))
  if VISUAL_TEST:
    img.applyBinaryMask(mask).save("appliedMask1.png")
    img.applyBinaryMask(mask,bg_color=Color.RED).save("appliedMask2.png")

  else:
    img.applyBinaryMask(mask)
    img.applyBinaryMask(mask,bg_color=Color.RED)
    
  pass

def test_applyPixelFunc():
  img = Image(logo)
  def myFunc((r,g,b)):
    return( (b,g,r) )

  if VISUAL_TEST:
    img.applyPixelFunction(myFunc).save("pixelfunc.png")
  else:
    img.applyPixelFunction(myFunc)
    
  pass

def test_applySideBySide():
  img = Image(logo)
  img3 = Image(testimage2)

  #LB = little image big image
  #BL = big image little image  -> this is important to test all the possible cases.
  if VISUAL_TEST:
    img3.sideBySide(img,side='right',scale=False).save('SideBySideRightBL.png')
    img3.sideBySide(img,side='left',scale=False).save('SideBySideLeftBL.png')
    img3.sideBySide(img,side='top',scale=False).save('SideBySideTopBL.png')
    img3.sideBySide(img,side='bottom',scale=False).save('SideBySideBottomBL.png')

    img.sideBySide(img3,side='right',scale=False).save('SideBySideRightLB.png')
    img.sideBySide(img3,side='left',scale=False).save('SideBySideLeftLB.png')
    img.sideBySide(img3,side='top',scale=False).save('SideBySideTopLB.png')
    img.sideBySide(img3,side='bottom',scale=False).save('SideBySideBottomLB.png')

    img3.sideBySide(img,side='right',scale=True).save('SideBySideRightScaledBL.png')
    img3.sideBySide(img,side='left',scale=True).save('SideBySideLeftScaledBL.png')
    img3.sideBySide(img,side='top',scale=True).save('SideBySideTopScaledBL.png')
    img3.sideBySide(img,side='bottom',scale=True).save('SideBySideBottomScaledBL.png')

    img.sideBySide(img3,side='right',scale=True).save('SideBySideRightScaledLB.png')
    img.sideBySide(img3,side='left',scale=True).save('SideBySideLeftScaledLB.png')
    img.sideBySide(img3,side='top',scale=True).save('SideBySideTopScaledLB.png')
    img.sideBySide(img3,side='bottom',scale=True).save('SideBySideBottomScaledLB.png')
  else:
    img3.sideBySide(img,side='right',scale=False)
    img3.sideBySide(img,side='left',scale=False)
    img3.sideBySide(img,side='top',scale=False)
    img3.sideBySide(img,side='bottom',scale=False)

    img.sideBySide(img3,side='right',scale=False)
    img.sideBySide(img3,side='left',scale=False)
    img.sideBySide(img3,side='top',scale=False)
    img.sideBySide(img3,side='bottom',scale=False)

    img3.sideBySide(img,side='right',scale=True)
    img3.sideBySide(img,side='left',scale=True)
    img3.sideBySide(img,side='top',scale=True)
    img3.sideBySide(img,side='bottom',scale=True)

    img.sideBySide(img3,side='right',scale=True)
    img.sideBySide(img3,side='left',scale=True)
    img.sideBySide(img3,side='top',scale=True)
    img.sideBySide(img3,side='bottom',scale=True)
  pass

def test_resize():
  img = Image(logo)
  w = img.width
  h = img.height
  img2 = img.resize(w*2,None)
  if( img2.width != w*2 or img2.height != h*2):
    assert False
    
  img3 = img.resize(h=h*2)
  
  if( img3.width != w*2 or img3.height != h*2):
    assert False
    
  img4 = img.resize(h=h*2,w=w*2)
  
  if( img4.width != w*2 or img4.height != h*2):
    assert False
    
    pass

def test_createAlphaMask():
  alphaMask = Image(alphaSrcImg)
  mask = alphaMask.createAlphaMask(hue=60)
  if VISUAL_TEST: mask.save("AlphaMask.png")

  mask = alphaMask.createAlphaMask(hue_lb=59,hue_ub=61)
  if VISUAL_TEST: mask.save("AlphaMask2.png")

  top = Image(topImg)
  bottom = Image(bottomImg)
  if VISUAL_TEST:
    bottom.blit(top,alphaMask=mask).save("AlphaMask3.png")

  else:
    bottom.blit(top,alphaMask=mask)
  pass

def test_blit_regular(): 
  top = Image(topImg)
  bottom = Image(bottomImg)

  if VISUAL_TEST:
    bottom.blit(top).save("BlitNormal.png")
    bottom.blit(top,pos=(-10,-10)).save("BlitTL.png")
    bottom.blit(top,pos=(-10,10)).save("BlitBL.png")
    bottom.blit(top,pos=(10,-10)).save("BlitTR.png")
    bottom.blit(top,pos=(10,10)).save("BlitBR.png")
  else:
    bottom.blit(top)
    bottom.blit(top,pos=(-10,-10))
    bottom.blit(top,pos=(-10,10))
    bottom.blit(top,pos=(10,-10))
    bottom.blit(top,pos=(10,10))
    
  pass

def test_blit_mask():
  top = Image(topImg)
  bottom = Image(bottomImg)
  mask = Image(maskImg)
  if VISUAL_TEST:
    bottom.blit(top,mask=mask).save("BlitMaskNormal.png")
    bottom.blit(top,mask=mask,pos=(-50,-50)).save("BlitMaskTL.png")
    bottom.blit(top,mask=mask,pos=(-50,50)).save("BlitMaskBL.png")
    bottom.blit(top,mask=mask,pos=(50,-50)).save("BlitMaskTR.png")
    bottom.blit(top,mask=mask,pos=(50,50)).save("BlitMaskBR.png")
  else:
    bottom.blit(top,mask=mask)
    bottom.blit(top,mask=mask,pos=(-50,-50))
    bottom.blit(top,mask=mask,pos=(-50,50))
    bottom.blit(top,mask=mask,pos=(50,-50))
    bottom.blit(top,mask=mask,pos=(50,50))
  pass


def test_blit_alpha():
  top = Image(topImg)
  bottom = Image(bottomImg)
  a = 0.5
  if VISUAL_TEST:
    bottom.blit(top,alpha=a).save("BlitAlphaNormal.png")
    bottom.blit(top,alpha=a,pos=(-50,-50)).save("BlitAlphaTL.png")
    bottom.blit(top,alpha=a,pos=(-50,50)).save("BlitAlphaBL.png")
    bottom.blit(top,alpha=a,pos=(50,-50)).save("BlitAlphaTR.png")
    bottom.blit(top,alpha=a,pos=(50,50)).save("BlitAlphaBR.png")
  else:
    bottom.blit(top,alpha=a)
    bottom.blit(top,alpha=a,pos=(-50,-50))
    bottom.blit(top,alpha=a,pos=(-50,50))
    bottom.blit(top,alpha=a,pos=(50,-50))
    bottom.blit(top,alpha=a,pos=(50,50))

  pass


def test_blit_alpha_mask():
  top = Image(topImg)
  bottom = Image(bottomImg)
  aMask = Image(alphaMaskImg)
  if VISUAL_TEST:
    bottom.blit(top,alphaMask=aMask).save("BlitAlphaMaskNormal.png")
    bottom.blit(top,alphaMask=aMask,pos=(-10,-10)).save("BlitAlphaMaskTL.png")
    bottom.blit(top,alphaMask=aMask,pos=(-10,10)).save("BlitAlphaMaskBL.png")
    bottom.blit(top,alphaMask=aMask,pos=(10,-10)).save("BlitAlphaMaskTR.png")
    bottom.blit(top,alphaMask=aMask,pos=(10,10)).save("BlitAlphaMaskBR.png")
  else:
    bottom.blit(top,alphaMask=aMask)
    bottom.blit(top,alphaMask=aMask,pos=(-10,-10))
    bottom.blit(top,alphaMask=aMask,pos=(-10,10))
    bottom.blit(top,alphaMask=aMask,pos=(10,-10))
    bottom.blit(top,alphaMask=aMask,pos=(10,10))
  pass


def test_imageset():
    imgs = ImageSet()

    if(isinstance(imgs, ImageSet)):
      pass
    else:
      assert False

def test_hsv_conversion():
    px = Image((1,1))
    px[0,0] = Color.GREEN
    if (Color.hsv(Color.GREEN) == px.toHSV()[0,0]):
      pass
    else:
      assert False


def test_whiteBalance():
  img = Image("../sampleimages/BadWB2.jpg")
  output = img.whiteBalance()
  output2 = img.whiteBalance(method="GrayWorld")
  if VISUAL_TEST:
    output.save("white_balanced_simple.png")
    output2.save("white_balanced_grayworld.png")


def test_hough_circles():
  img = Image(circles)
  circs = img.findCircle(thresh=100)
  if( circs[0] < 1 ):
    assert False
  circs[0].coordinates()
  circs[0].width()
  circs[0].area()
  circs[0].perimeter()
  circs[0].height()
  circs[0].radius()
  circs[0].diameter()
  circs[0].colorDistance()
  circs[0].meanColor()
  circs[0].distanceFrom(point=(0,0))
  circs[0].draw()
  img2 = circs[0].crop()
  img3 = circs[0].crop(noMask=True)
  if( img2 is not None and img3 is not None ):
    pass
  else:
    assert False

def test_drawRectangle():
  img = Image(testimage2)
  img.drawRectangle(0,0,100,100,color=Color.BLUE,width=0,alpha=0)
  img.drawRectangle(1,1,100,100,color=Color.BLUE,width=2,alpha=128)
  img.drawRectangle(1,1,100,100,color=Color.BLUE,width=1,alpha=128)
  img.drawRectangle(2,2,100,100,color=Color.BLUE,width=1,alpha=255)
  img.drawRectangle(3,3,100,100,color=Color.BLUE)
  img.drawRectangle(4,4,100,100,color=Color.BLUE,width=12)
  img.drawRectangle(5,5,100,100,color=Color.BLUE,width=-1)
  pass


def test_BlobMinRect():
  img = Image(testimageclr)
  blobs = img.findBlobs()
  for b in blobs:
    b.drawMinRect(color=Color.BLUE,width=3,alpha=123)
  if VISUAL_TEST:
    img.save("blobMinRect.png")
   
  pass

def test_BlobRect():
  img = Image(testimageclr)
  blobs = img.findBlobs()
  for b in blobs:
    b.drawRect(color=Color.BLUE,width=3,alpha=123)
  if VISUAL_TEST:
    img.save("blobRect.png")
   
  pass

def test_blob_spatial_relationships():
  img = Image("../sampleimages/blockhead.png")
  #please see the image
  blobs = img.findBlobs()
  blobs = blobs.sortArea()
  t1 = blobs[-2].above(blobs[-1])
  f1 = blobs[-1].above(blobs[-2])
  t2 = blobs[-1].below(blobs[-2])
  f2 = blobs[-2].below(blobs[-1])
  t3 = blobs[-2].contains(blobs[-3])
  f3 = blobs[-3].contains(blobs[-2])
  t4 = blobs[-2].overlaps(blobs[-3])
  f4 = blobs[-3].overlaps(blobs[-2])
  f5 = blobs[-3].overlaps(blobs[-1])
  t5 = blobs[-2].overlaps(blobs[-3])
  #-4 right -5 left
  f6 = blobs[-4].right(blobs[-5])
  t6 = blobs[-5].right(blobs[-4])  
  f7 = blobs[-5].left(blobs[-4]) 
  t7 = blobs[-4].left(blobs[-5])
  
  myTuple = (0,0)
  t8 = blobs[-1].above(myTuple)
  f8 = blobs[-1].below(myTuple)
  t9 = blobs[-1].left(myTuple)
  f9 = blobs[-1].right(myTuple)
  f10 = blobs[-1].contains(myTuple)
  f11 = blobs[-1].contains(myTuple)

  myNPA = np.array([0,0])
  t10 = blobs[-1].above(myNPA)
  f12 = blobs[-1].below(myNPA)
  t11 = blobs[-1].left(myNPA)
  f13 = blobs[-1].right(myNPA)
  f14 = blobs[-1].contains(myNPA)

  myTrue = ( t1 and t2 and t3 and t4 and t5 and t6 and t7 and t8 and t9 and t10 and t11 )
  myFalse = (f1 or f2 or f3 or f4 or f5 or f6 or f7 or f8 or f9 or f10 or f11 or f12 or f13 or f14)

  if( myTrue and not myFalse ):
    pass
  else:
    assert False
  
def test_BlobPickle():
  img = Image(testimageclr)
  blobs = img.findBlobs()
  for b in blobs:
    p = pickle.dumps(b)
    ub = pickle.loads(p)
    if (ub.mMask - b.mMask).meanColor() != Color.BLACK:
      assert False 
   
  pass

def test_blob_isa_methods():
  img1 = Image(circles)
  img2 = Image("../sampleimages/blockhead.png")
  blobs = img1.findBlobs().sortArea()
  t1 = blobs[-1].isCircle()
  f1 = blobs[-1].isRectangle()
  blobs = img2.findBlobs().sortArea()
  f2 = blobs[-1].isCircle()
  t2 = blobs[-1].isRectangle()
  if( t1 and t2 and not f1 and not f2):
    pass
  else:
    assert False

def test_findKeypoints():
  img = Image(testimage2)
  kp = img.findKeypoints()
  for k in kp:
    k.getObject()
    k.descriptor()
    k.quality()
    k.octave()
    k.flavor()
    k.angle()
    k.coordinates()
    k.draw()
    k.distanceFrom()
    k.meanColor()
    k.area()
    k.perimeter()
    k.width()
    k.height()
    k.radius()
    k.crop()
  pass

def test_movement_feature():
  #~ current = Image("../sampleimages/flow1.png")
  #~ prev = Image("../sampleimages/flow2.png")
  current = Image("../sampleimages/flow_simple1.png")
  prev = Image("../sampleimages/flow_simple2.png")
  
  fs = current.findMotion(prev, window=7)  
  if( len(fs) > 0 ):
    fs.draw(color=Color.RED)
    if VISUAL_TEST:
      current.save("flowOutBM.png")
    img = fs[0].crop()
    color = fs[1].meanColor()
    wndw = fs[1].windowSz()
    for f in fs:
      f.vector()
      f.magnitude()
  else:
    assert False
  
  fs = current.findMotion(prev, window=7,method='HS')  
  if( len(fs) > 0 ):
    fs.draw(color=Color.RED)
    if VISUAL_TEST:
      current.save("flowOutHS.png")
    img = fs[0].crop()
    color = fs[1].meanColor()
    wndw = fs[1].windowSz()
    for f in fs:
      f.vector()
      f.magnitude()
  else:
    assert False
  
  fs = current.findMotion(prev, window=7,method='LK',aggregate=False)  
  if( len(fs) > 0 ):
    fs.draw(color=Color.RED)
    if VISUAL_TEST:
      current.save("flowOutLK.png")
    img = fs[0].crop()
    color = fs[1].meanColor()
    wndw = fs[1].windowSz()
    for f in fs:
      f.vector()
      f.magnitude()
  else:
    assert False

  pass 

def test_keypoint_extraction():
  img = Image("../sampleimages/KeypointTemplate2.png")
  kp1 = img.findKeypoints()
  kp2 = img.findKeypoints(highQuality=True)
  kp3 = img.findKeypoints(flavor="STAR")
  #TODO: Fix FAST binding
  #~ kp4 = img.findKeypoints(flavor="FAST",min_quality=10)
  if( len(kp1)==190 and 
      len(kp2)==190 and
      len(kp3)==37
      #~ and len(kp4)==521
    ):
    pass
  else:
    assert False


def test_keypoint_match():
  template = Image("../sampleimages/KeypointTemplate2.png")
  match0 = Image("../sampleimages/kptest0.png")
  match1 = Image("../sampleimages/kptest1.png")
  match2 = Image("../sampleimages/aerospace.jpg")

  fs0 = match0.findKeypointMatch(template)
  fs1 = match1.findKeypointMatch(template,quality=400.00,minDist=0.15,minMatch=0.2)
  fs2 = match2.findKeypointMatch(template,quality=500.00,minDist=0.1,minMatch=0.4)
  if( fs0 is not None and fs1 is not None and fs2 is None):
    if VISUAL_TEST:
      fs0.draw()
      match0.save("KPAffineMatch0.png")
    if VISUAL_TEST:
      fs1.draw()
      match1.save("KPAffineMatch1.png")
    f = fs0[0] 
    f.drawRect()
    f.draw()
    f.getHomography()
    f.getMinRect()
    f.meanColor()
    f.crop()
    f.x
    f.y
    f.coordinates()
    pass
  else:
    assert False

def test_draw_keypointt_matches():
  template = Image("../sampleimages/KeypointTemplate2.png")
  match0 = Image("../sampleimages/kptest0.png")
  result = match0.drawKeypointMatches(template,thresh=500.00,minDist=0.15,width=1)
  if VISUAL_TEST:
    result.save("KPMatch.png")
  pass


def test_basic_palette():
  img = Image(testimageclr)
  img._generatePalette(10,False)
  if( img._mPalette is not None and
      img._mPaletteMembers is not None and
      img._mPalettePercentages is not None and
      img._mPaletteBins == 10
      ):
    img._generatePalette(20,True)
    if( img._mPalette is not None and
        img._mPaletteMembers is not None and
        img._mPalettePercentages is not None and
        img._mPaletteBins == 20
        ):
      pass

def test_palettize():
  img = Image(testimageclr)
  img2 = img.palettize(bins=20,hue=False)
  img3 = img.palettize(bins=3,hue=True)
  pass

def test_repalette():
  img = Image(testimageclr)
  img2 = Image(bottomImg)
  p = img.getPalette()
  img3 = img2.rePalette(p)
  p = img.getPalette(hue=True)
  img4 = img2.rePalette(p,hue=True)
  pass

def test_drawPalette():
  img = Image(testimageclr)
  img1 = img.drawPaletteColors()
  img2 = img.drawPaletteColors(horizontal=False)
  img3 = img.drawPaletteColors(size=(69,420) )
  img4 = img.drawPaletteColors(size=(69,420),horizontal=False)
  img5 = img.drawPaletteColors(hue=True)
  img6 = img.drawPaletteColors(horizontal=False,hue=True)
  img7 = img.drawPaletteColors(size=(69,420),hue=True )
  img8 = img.drawPaletteColors(size=(69,420),horizontal=False,hue=True)

def test_palette_binarize():
  img = Image(testimageclr)
  p = img.getPalette()
  img2 = img.binarizeFromPalette(p[0:5])
  if VISUAL_TEST:
    img2.save("binary_palette_1.png")
  p = img.getPalette(hue=True)
  img2 = img.binarizeFromPalette(p[0:5])
  if VISUAL_TEST:
    img2.save("binary_palette_2.png")
  pass

def test_palette_blobs():
  img = Image(testimageclr)
  p = img.getPalette()
  b1 = img.findBlobsFromPalette(p[0:5])
  b1.draw()
  if VISUAL_TEST:
    img.save("blobs_palette_1.png")

  p = img.getPalette(hue=True)
  b2 = img.findBlobsFromPalette(p[0:5])
  b2.draw()
  if VISUAL_TEST:
    img.save("blobs_palette_2.png")

  if( len(b1) > 0 and len(b2) > 0 ):
    pass
  else:
    assert False

    

def test_skeletonize():
  img = Image(logo)
  s = img.skeletonize()
  s2 = img.skeletonize(10)

  pass


def test_threshold():
  img = Image(logo)
  for t in range(0,255):
    img.threshold(t)
  pass

def test_smartThreshold():
  img = Image("../sampleimages/RatTop.png")
  mask = Image((img.width,img.height))
  mask.dl().circle((100,100),80,color=Color.MAYBE_BACKGROUND,filled=True)
  mask.dl().circle((100,100),60,color=Color.MAYBE_FOREGROUND,filled=True)
  mask.dl().circle((100,100),40,color=Color.FOREGROUND,filled=True)
  mask = mask.applyLayers()
  new_mask = img.smartThreshold(mask=mask)
  if VISUAL_TEST:
    new_mask.save("SMART_THRESHOLD_MASK.png")
  
  new_mask = img.smartThreshold(rect=(30,30,150,185))
  if VISUAL_TEST:
    new_mask.save("SMART_THRESHOLD_RECT.png")

  pass

def test_smartFindBlobs():
  img = Image("../sampleimages/RatTop.png")
  mask = Image((img.width,img.height))
  mask.dl().circle((100,100),80,color=Color.MAYBE_BACKGROUND,filled=True)
  mask.dl().circle((100,100),60,color=Color.MAYBE_FOREGROUND,filled=True)
  mask.dl().circle((100,100),40,color=Color.FOREGROUND,filled=True)
  mask = mask.applyLayers()
  blobs = img.smartFindBlobs(mask=mask)
  blobs.draw()
  if VISUAL_TEST:
    img.save("SMART_BLOB_MASK.png")
  if( len(blobs) < 1 ):
    assert False

  for t in range(2,3):
    blobs2 = img.smartFindBlobs(rect=(30,30,150,185),thresh_level=t)
    if(blobs2 is not None):
      blobs2.draw()
      if VISUAL_TEST:
        fname = "SMART_BLOB_RECT" + str(t) + ".png"
        img.save(fname)
        
  pass


def test_image_webp_load():
  #only run if webm suppport exist on system
  try:
    import webm
  except:
    if( SHOW_WARNING_TESTS ):
      warnings.warn("Couldn't run the webp test as optional webm library required")
    pass

  else:
    img = Image(webp)

    if len(img.toString()) <= 1:
      assert False

    else:
      pass
    
def test_image_webp_save():
  #only run if webm suppport exist on system
  try:
    import webm
  except:
    if( SHOW_WARNING_TESTS ):
      warnings.warn("Couldn't run the webp test as optional webm library required")
    pass

  else:
    img = Image('simplecv')
    tf = tempfile.NamedTemporaryFile(suffix=".webp")
    if img.save(tf.name):
      pass
    else:
      assert False


def test_getEXIFData():
  img = Image("../sampleimages/OWS.jpg")
  img2 = Image(testimage)
  d1 = img.getEXIFData()
  d2 = img2.getEXIFData()
  if( len(d1) > 0 and len(d2) == 0 ):
    pass
  else:
    assert False

def test_get_raw_dft():
  img = Image("../sampleimages/RedDog2.jpg")
  raw3 = img.rawDFTImage()
  raw1 = img.rawDFTImage(grayscale=True)
  if( len(raw3) != 3 or
      len(raw1) != 1 or
      raw1[0].width != img.width or
      raw1[0].height != img.height or
      raw3[0].height != img.height or
      raw3[0].width != img.width or
      raw1[0].depth != 64L or
      raw3[0].depth != 64L or
      raw3[0].channels != 2 or
      raw3[0].channels != 2 ):
    assert False
  else:
    pass

def test_getDFTLogMagnitude():
  img = Image("../sampleimages/RedDog2.jpg")  
  lm3 = img.getDFTLogMagnitude()
  lm1 = img.getDFTLogMagnitude(grayscale=True)
  pass


def test_applyDFTFilter():
  img = Image("../sampleimages/RedDog2.jpg")
  flt = Image("../sampleimages/RedDogFlt.png")
  f1 = img.applyDFTFilter(flt)
  f2 = img.applyDFTFilter(flt,grayscale=True)
  if VISUAL_TEST:
    f1.save("DFTFilt.png")
    f2.save("DFTFiltGray.png")
  pass

def test_highPassFilter():
  img = Image("../sampleimages/RedDog2.jpg")
  a = img.highPassFilter(0.5)
  b = img.highPassFilter(0.5,grayscale=True)
  c = img.highPassFilter(0.5,yCutoff=0.4)
  d = img.highPassFilter(0.5,yCutoff=0.4,grayscale=True)
  e = img.highPassFilter([0.5,0.4,0.3])
  f = img.highPassFilter([0.5,0.4,0.3],yCutoff=[0.5,0.4,0.3])
  if VISUAL_TEST:
    a.save("DFT-hpf-A.png")
    b.save("DFT-hpf-B.png")
    c.save("DFT-hpf-C.png")
    d.save("DFT-hpf-D.png")
    e.save("DFT-hpf-E.png")
    f.save("DFT-hpf-F.png")
    
  pass

def test_lowPassFilter():
  img = Image("../sampleimages/RedDog2.jpg")
  a = img.lowPassFilter(0.5)
  b = img.lowPassFilter(0.5,grayscale=True)
  c = img.lowPassFilter(0.5,yCutoff=0.4)
  d = img.lowPassFilter(0.5,yCutoff=0.4,grayscale=True)
  e = img.lowPassFilter([0.5,0.4,0.3])
  f = img.lowPassFilter([0.5,0.4,0.3],yCutoff=[0.5,0.4,0.3])
  if VISUAL_TEST:
    a.save("DFT-lpf-A.png")
    b.save("DFT-lpf-B.png")
    c.save("DFT-lpf-C.png")
    d.save("DFT-lpf-D.png")
    e.save("DFT-lpf-E.png")
    f.save("DFT-lpf-F.png")
  pass

def test_findHaarFeatures():
  img = Image("../sampleimages/orson_welles.jpg")
  face = HaarCascade("../Features/HaarCascades/face.xml")
  f = img.findHaarFeatures(face)
  f2 = img.findHaarFeatures("../Features/HaarCascades/face.xml")
  if( len(f) > 0 and len(f2) > 0 ):
    f[0].width()
    f[0].height()
    f[0].draw()
    f[0].x
    f[0].y
    f[0].length()
    f[0].area()
    pass
  else:
    assert False


def test_biblical_flood_fill():
  img = Image(testimage2)
  b = img.findBlobs()
  img.floodFill(b.coordinates(),tolerance=3,color=Color.RED)
  img.floodFill(b.coordinates(),tolerance=(3,3,3),color=Color.BLUE)
  img.floodFill(b.coordinates(),tolerance=(3,3,3),color=Color.GREEN,fixed_range=False)
  img.floodFill((30,30),lower=3,upper=5,color=Color.ORANGE)
  img.floodFill((30,30),lower=3,upper=(5,5,5),color=Color.ORANGE)
  img.floodFill((30,30),lower=(3,3,3),upper=5,color=Color.ORANGE)
  img.floodFill((30,30),lower=(3,3,3),upper=(5,5,5))
  if VISUAL_TEST:
    img.save("biblical.png")
  pass
  
def test_flood_fill_to_mask():
  img = Image(testimage2)
  b = img.findBlobs()
  imask = img.edges()
  omask = img.floodFillToMask(b.coordinates(),tolerance=10)
  omask2 = img.floodFillToMask(b.coordinates(),tolerance=(3,3,3),mask=imask)
  omask3 = img.floodFillToMask(b.coordinates(),tolerance=(3,3,3),mask=imask,fixed_range=False)
  if VISUAL_TEST:
    omask.save("flood_fill_to_mask1.png")
    omask2.save("flood_fill_to_mask2.png")
    omask3.save("flood_fill_to_mask3.png")
  pass

def test_findBlobsFromMask():
  img = Image(testimage2)
  mask = img.binarize().invert()
  b1 = img.findBlobsFromMask(mask)
  b2 = img.findBlobs()
  if(len(b1) == len(b2) ):
    pass
  else:
    assert False


def test_bandPassFilter():
  img = Image("../sampleimages/RedDog2.jpg")
  a = img.bandPassFilter(0.1,0.3)
  b = img.bandPassFilter(0.1,0.3,grayscale=True)
  c = img.bandPassFilter(0.1,0.3,yCutoffLow=0.1,yCutoffHigh=0.3)
  d = img.bandPassFilter(0.1,0.3,yCutoffLow=0.1,yCutoffHigh=0.3,grayscale=True)
  e = img.bandPassFilter([0.1,0.2,0.3],[0.5,0.5,0.5])
  f = img.bandPassFilter([0.1,0.2,0.3],[0.5,0.5,0.5],yCutoffLow=[0.1,0.2,0.3],yCutoffHigh=[0.6,0.6,0.6])
  if VISUAL_TEST:
    a.save("DFT-bpf-A.png")
    b.save("DFT-bpf-B.png")
    c.save("DFT-bpf-C.png")
    d.save("DFT-bpf-D.png")
    e.save("DFT-bpf-E.png")
    f.save("DFT-bpf-F.png")

def test_image_slice():
  img = Image("../sampleimages/blockhead.png")
  I = img.findLines()
  I2 = I[0:10]
  if type(I2) == list:
    assert False
  else:
    pass

