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

import os, sys, pickle, operator
from SimpleCV import *
from nose.tools import with_setup, nottest

VISUAL_TEST = False  # if TRUE we save the images - otherwise we DIFF against them - the default is False
SHOW_WARNING_TESTS = False  # show that warnings are working - tests will pass but warnings are generated.

#colors
black = Color.BLACK
white = Color.WHITE
red = Color.RED
green = Color.GREEN
blue = Color.BLUE

###############
# TODO -
# Examples of how to do profiling
# Examples of how to do a single test -
# UPDATE THE VISUAL TESTS WITH EXAMPLES.
# Fix exif data
# Turn off test warnings using decorators.
# Write a use the tests doc.

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
logo = "../sampleimages/simplecv.png"
logo_inverted = "../sampleimages/simplecv_inverted.png"
ocrimage = "../sampleimages/ocr-test.png"
circles = "../sampleimages/circles.png"
webp = "../sampleimages/simplecv.webp"

#alpha masking images
topImg = "../sampleimages/RatTop.png"
bottomImg = "../sampleimages/RatBottom.png"
maskImg = "../sampleimages/RatMask.png"
alphaMaskImg = "../sampleimages/RatAlphaMask.png"
alphaSrcImg = "../sampleimages/GreenMaskSource.png"

#standards path
standard_path = "./standard/"


#Given a set of images, a path, and a tolerance do the image diff.
def imgDiffs(test_imgs,name_stem,tolerance,path):
    count = len(test_imgs)
    for idx in range(0,count):
        lhs = test_imgs[idx].applyLayers() # this catches drawing methods
        fname = standard_path+name_stem+str(idx)+".jpg"
        rhs = Image(fname)
        if( lhs.width == rhs.width and lhs.height == rhs.height ):
            diff = (lhs-rhs)
            val = np.average(diff.getNumpy())
            if( val > tolerance ):
                print val
                return True
    return False

#Save a list of images to a standard path.
def imgSaves(test_imgs, name_stem, path=standard_path):
    count = len(test_imgs)
    for idx in range(0,count):
        fname = standard_path+name_stem+str(idx)+".jpg"
        test_imgs[idx].save(fname)#,quality=95)

#perform the actual image save and image diffs.
def perform_diff(result,name_stem,tolerance=3.0,path=standard_path):
    if(VISUAL_TEST): # save the correct images for a visual test
        imgSaves(result,name_stem,path)
    else: # otherwise we test our output against the visual test
        if( imgDiffs(result,name_stem,tolerance,path) ):
            assert False
        else:
            pass

def test_image_stretch():
    img = Image(greyscaleimage)
    stretched = img.stretch(100,200)
    if(stretched == None):
        assert False

    result = [stretched]
    name_stem = "test_stretch"
    perform_diff(result,name_stem)


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
    img1 = Image("lenna")
    img2 = Image("lenna")
    img2 = img2.smooth()
    result = [img1,img2]
    name_stem = "test_image_bitmap"
    perform_diff(result,name_stem)

# # Image Class Test

def test_image_scale():
    img = Image(testimage)
    thumb = img.scale(30,30)
    if(thumb == None):
        assert False
    result = [thumb]
    name_stem = "test_image_scale"
    perform_diff(result,name_stem)

def test_image_copy():
    img = Image(testimage2)
    copy = img.copy()

    if (img[1,1] != copy[1,1] or img.size() != copy.size()):
        assert False

    result = [copy]
    name_stem = "test_image_copy"
    perform_diff(result,name_stem)

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

    result = [newimg]
    name_stem = "test_image_setitem"
    perform_diff(result,name_stem)


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
    result = [newimg]
    name_stem = "test_image_setslice"
    perform_diff(result,name_stem)


def test_detection_findCorners():
    img = Image(testimage2)
    corners = img.findCorners(25)
    corners.draw()
    if (len(corners) == 0):
        assert False
    result = [img]
    name_stem = "test_detection_findCorners"
    perform_diff(result,name_stem)


def test_color_meancolor():
    a = np.arange(0, 256)
    b = a[::-1]
    c = np.copy(a)/2
    a = a.reshape(16, 16)
    b = b.reshape(16, 16)
    c = c.reshape(16, 16)
    imgarr = np.dstack((a, b, c))
    img = Image(imgarr)

    b, g, r = img.meanColor('BGR')
    if not (127 < r < 128 and 127 < g < 128 and 63 < b < 64):
        assert False

    r, g, b = img.meanColor('RGB')
    if not (127 < r < 128 and 127 < g < 128 and 63 < b < 64):
        assert False

    h, s, v = img.meanColor('HSV')
    if not (83 < h < 84 and 191 < s < 192 and 191 < v < 192):
        assert False

    x, y, z = img.meanColor('XYZ')
    if not (109 < x < 110 and 122 < y < 123 and 77 < z < 79):
        assert False

    gray = img.meanColor('Gray')
    if not (120 < gray < 121):
        assert False

    y, cr, cb = img.meanColor('YCrCb')
    if not (120 < y < 121 and 133 < cr < 134 and 96 < cb < 97):
        assert False

    h, l, s = img.meanColor('HLS')
    if not (84 < h < 85 and 117 < l < 118 and 160 < s < 161):
        assert False
    pass

def test_image_smooth():
    img = Image(testimage2)
    result = []
    result.append(img.smooth())
    result.append(img.smooth('bilateral', (3,3), 4, 1))
    result.append(img.smooth('blur', (3, 3)))
    result.append(img.smooth('median', (3, 3)))
    result.append(img.smooth('gaussian', (5,5), 0))
    result.append(img.smooth('bilateral', (3,3), 4, 1,grayscale=False))
    result.append(img.smooth('blur', (3, 3),grayscale=True))
    result.append(img.smooth('median', (3, 3),grayscale=True))
    result.append(img.smooth('gaussian', (5,5), 0,grayscale=True))
    name_stem = "test_image_smooth"
    perform_diff(result,name_stem)
    pass

def test_image_gammaCorrect():
    img = Image(topImg)
    img2 = img.gammaCorrect(1)
    img3 = img.gammaCorrect(0.5)
    img4 = img.gammaCorrect(2)
    result = []
    result.append(img3)
    result.append(img4)
    name_stem = "test_image_gammaCorrect"
    perform_diff(result, name_stem)
    if ((img3.meanColor() >= img2.meanColor()) and (img4.meanColor() <= img2.meanColor())):
        pass
    else:
        assert False

def test_image_binarize():
    img =  Image(testimage2)
    binary = img.binarize()
    binary2 = img.binarize((60, 100, 200))
    hist = binary.histogram(20)
    hist2 = binary2.histogram(20)

    result = [binary,binary2]
    name_stem = "test_image_binarize"
    perform_diff(result,name_stem)

    if (hist[0] + hist[-1] == np.sum(hist) and hist2[0] + hist2[-1] == np.sum(hist2)):
        pass
    else:
        assert False

def test_image_binarize_adaptive():
    img =  Image(testimage2)
    binary = img.binarize(-1)
    hist = binary.histogram(20)

    result = [binary]
    name_stem = "test_image_binarize_adaptive"
    perform_diff(result,name_stem)

    if (hist[0] + hist[-1] == np.sum(hist)):
        pass
    else:
        assert False

def test_image_invert():
    img = Image(testimage2)
    clr = img[1,1]
    img = img.invert()

    result = [img]
    name_stem = "test_image_invert"
    perform_diff(result,name_stem)

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
    img.drawCircle((img.width/2, img.height/2), 10,thickness=3)
    img.drawCircle((img.width/2, img.height/2), 15,thickness=5,color=Color.RED)
    img.drawCircle((img.width/2, img.height/2), 20)
    img.drawLine((5, 5), (5, 8))
    img.drawLine((5, 5), (10, 10),thickness=3)
    img.drawLine((0, 0), (img.width, img.height),thickness=3,color=Color.BLUE)
    img.drawRectangle(20,20,10,5)
    img.drawRectangle(22,22,10,5,alpha=128)
    img.drawRectangle(24,24,10,15,width=-1,alpha=128)
    img.drawRectangle(28,28,10,15,width=3,alpha=128)
    result = [img]
    name_stem = "test_image_drawing"
    perform_diff(result,name_stem)

def test_image_draw():
    img = Image("lenna")
    newimg = Image("simplecv")
    lines = img.findLines()
    newimg.draw(lines)
    lines.draw()
    result = [newimg, img]
    name_stem = "test_image_draw"
    perform_diff(result, name_stem, 5)


def test_image_splitchannels():
    img = Image(testimageclr)
    (r, g, b) = img.splitChannels(True)
    (red, green, blue) = img.splitChannels()
    result = [r,g,b,red,green,blue]
    name_stem = "test_image_splitchannels"
    perform_diff(result,name_stem)
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
    result = [img]
    name_stem = "test_detection_lines"
    perform_diff(result,name_stem)

    if(lines == 0 or lines == None):
        assert False

def test_detection_lines_standard():
    img = Image(testimage2)
    lines = img.findLines(useStandard=True)
    lines.draw()
    result = [img]
    name_stem = "test_detection_lines_standard"
    perform_diff(result,name_stem)

    if(lines == 0 or lines == None):
        assert False

def test_detection_feature_measures():
    img = Image(testimage2)

    fs = FeatureSet()
    fs.append(Corner(img, 5, 5))
    fs.append(Line(img, ((2, 2), (3,3))))
    bm = BlobMaker()
    result = bm.extract(img)
    fs.extend(result)

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
    pass

def test_detection_blobs_appx():
    img = Image("lenna")
    blobs = img.findBlobs()
    blobs[-1].draw(color=Color.RED)
    blobs[-1].drawAppx(color=Color.BLUE)
    result = [img]

    img2 = Image("lenna")
    blobs = img2.findBlobs(appx_level=11)
    blobs[-1].draw(color=Color.RED)
    blobs[-1].drawAppx(color=Color.BLUE)
    result.append(img2)

    name_stem = "test_detection_blobs_appx"
    perform_diff(result,name_stem,5.00)
    if blobs == None:
        assert False

def test_detection_blobs():
    img = Image(testbarcode)
    blobs = img.findBlobs()
    blobs.draw(color=Color.RED)
    result = [img]
    #TODO - WE NEED BETTER COVERAGE HERE
    name_stem = "test_detection_blobs"
    perform_diff(result,name_stem,5.00)

    if blobs == None:
        assert False

def test_detection_blobs_lazy():

    img = Image("lenna")
    b = img.findBlobs()
    result = []

    s = pickle.dumps(b[-1]) # use two otherwise it w
    b2 =  pickle.loads(s)

    result.append(b[-1].mImg)
    result.append(b[-1].mMask)
    result.append(b[-1].mHullImg)
    result.append(b[-1].mHullMask)

    result.append(b2.mImg)
    result.append(b2.mMask)
    result.append(b2.mHullImg)
    result.append(b2.mHullMask)

    #TODO - WE NEED BETTER COVERAGE HERE
    name_stem = "test_detection_blobs_lazy"
    perform_diff(result,name_stem,6.00)


def test_detection_blobs_adaptive():
    img = Image(testimage)
    blobs = img.findBlobs(-1, threshblocksize=99)
    blobs.draw(color=Color.RED)
    result = [img]
    name_stem = "test_detection_blobs_adaptive"
    perform_diff(result,name_stem,5.00)

    if blobs == None:
        assert False

def test_detection_blobs_smallimages():
    # Check if segfault occurs or not
    img = Image("../sampleimages/blobsegfaultimage.png")
    blobs = img.findBlobs()
    # if no segfault, pass

def test_detection_blobs_convexity_defects():
    img = Image('lenna')
    blobs = img.findBlobs()
    b = blobs[-1]
    feat = b.getConvexityDefects()
    points = b.getConvexityDefects(returnPoints=True)
    if len(feat) <= 0 or len(points) <= 0:
        assert False
    pass

def test_detection_barcode():
    try:
        import zbar
    except:
        return None

    img1 = Image(testimage)
    img2 = Image(testbarcode)

    if( SHOW_WARNING_TESTS ):
        nocode = img1.findBarcode()
        if nocode: #we should find no barcode in our test image
            assert False
        code = img2.findBarcode()
        code.draw()
        if code.points:
            pass
        result = [img1,img2]
        name_stem = "test_detection_barcode"
        perform_diff(result,name_stem)


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

    result = [img2,img3]
    name_stem = "test_color_curve_HLS"
    perform_diff(result,name_stem)

    c = img3.meanColor()
    if( c[0] > 2.0 or c[1] > 2.0 or c[2] > 2.0 ): #there may be a bit of roundoff error
        assert False

def test_color_curve_RGB():
    y = np.array([[0,0],[64,128],[192,128],[255,255]])  #These are the weights
    curve = ColorCurve(y)
    img = Image(testimage)
    img2 = img.applyRGBCurve(curve,curve,curve)
    img3 = img-img2

    result = [img2,img3]
    name_stem = "test_color_curve_RGB"
    perform_diff(result,name_stem)

    c = img3.meanColor()
    if( c[0] > 1.0 or c[1] > 1.0 or c[2] > 1.0 ): #there may be a bit of roundoff error
        assert False

def test_color_curve_GRAY():
    y = np.array([[0,0],[64,128],[192,128],[255,255]])  #These are the weights
    curve = ColorCurve(y)
    img = Image(testimage)
    gray = img.grayscale()
    img2 = img.applyIntensityCurve(curve)

    result = [img2]
    name_stem = "test_color_curve_GRAY"
    perform_diff(result,name_stem)

    g=gray.meanColor()
    i2=img2.meanColor()
    if( g[0]-i2[0] > 1 ): #there may be a bit of roundoff error
        assert False

def test_image_dilate():
    img=Image(barcode)
    img2 = img.dilate(20)

    result = [img2]
    name_stem = "test_image_dilate"
    perform_diff(result,name_stem)
    c=img2.meanColor()

    if( c[0] < 254 or c[1] < 254 or c[2] < 254 ):
        assert False;

def test_image_erode():
    img=Image(barcode)
    img2 = img.erode(100)

    result = [img2]
    name_stem = "test_image_erode"
    perform_diff(result,name_stem)

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
    results = [result]
    name_stem = "test_image_morph_open"
    perform_diff(results,name_stem)

    if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
        assert False;

def test_image_morph_close():
    img = Image(barcode)
    dilate = img.dilate()
    erode = dilate.erode()
    result = img.morphClose()
    test = result-erode
    c=test.meanColor()

    results = [result]
    name_stem = "test_image_morph_close"
    perform_diff(results,name_stem)


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

    results = [result]
    name_stem = "test_image_morph_grad"
    perform_diff(results,name_stem)


    if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
        assert False

def test_image_rotate_fixed():
    img = Image(testimage2)
    img2=img.rotate(180, scale = 1)
    img3=img.flipVertical()
    img4=img3.flipHorizontal()
    img5 = img.rotate(70)
    img6 = img.rotate(70,scale=0.5)

    results = [img2,img3,img4,img5,img6]
    name_stem = "test_image_rotate_fixed"
    perform_diff(results,name_stem)

    test = img4-img2
    c=test.meanColor()
    print(c)
    if( c[0] > 5 or c[1] > 5 or c[2] > 5 ):
        assert False


def test_image_rotate_full():
    img = Image(testimage2)
    img2=img.rotate(180,"full",scale = 1)

    results = [img2]
    name_stem = "test_image_rotate_full"
    perform_diff(results,name_stem)

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

    results = [s,w]
    name_stem = "test_image_shear_warp"
    perform_diff(results,name_stem)

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

    results = [atrans,atrans2]

    name_stem = "test_image_affine"
    perform_diff(results,name_stem)

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
    np_test = test.getNumpy()
    mc=test.meanColor()
    results = [ptrans,ptrans2]
    name_stem = "test_image_perspective"
    # Threshold kept high, otherwise test will fail
    # difference between original image warped image will be always huge
    perform_diff(results,name_stem, 100)

    if( mc[0] > 100 or mc[1] > 100 or mc[2] > 100 ):
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
    fakeCamera.loadCalibration("./StereoVision/Default")
    img = Image("../sampleimages/CalibImage0.png")
    img2 = fakeCamera.undistort(img)

    results = [img2]
    name_stem = "test_camera_undistort"
    perform_diff(results,name_stem,tolerance=12)

    if (not img2): #right now just wait for this to return
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
    # if( SHOW_WARNING_TESTS ):
    #     crop7 = img.crop(0,0,-10,10)
    #     crop8 = img.crop(-50,-50,10,10)
    #     crop3 = img.crop(-3,-3,10,20)
    #     crop4 = img.crop(-10,10,20,20,centered=True)
    #     crop5 = img.crop(-10,-10,20,20)

    tests = []
    tests.append(img.crop((50,50),(10,10))) # 0
    tests.append(img.crop([10,10,40,40])) # 1
    tests.append(img.crop((10,10,40,40))) # 2
    tests.append(img.crop([50,50],[10,10])) # 3
    tests.append(img.crop([10,10],[50,50])) # 4

    roi = np.array([10,10,40,40])
    pts1 = np.array([[50,50],[10,10]])
    pts2 = np.array([[10,10],[50,50]])
    pt1 = np.array([10,10])
    pt2 = np.array([50,50])

    tests.append(img.crop(roi)) # 5
    tests.append(img.crop(pts1)) # 6
    tests.append(img.crop(pts2)) # 7
    tests.append(img.crop(pt1,pt2)) # 8
    tests.append(img.crop(pt2,pt1)) # 9

    xs = [10,10,10,20,20,20,30,30,40,40,40,50,50,50]
    ys = [10,20,50,20,30,40,30,10,40,50,10,50,10,42]
    lots = zip(xs,ys)

    tests.append(img.crop(xs,ys)) # 10
    tests.append(img.crop(lots)) # 11
    tests.append(img.crop(np.array(xs),np.array(ys))) # 12
    tests.append(img.crop(np.array(lots))) # 14

    i = 0
    failed = False
    for img in tests:
        if( img is None or img.width != 40 and img.height != 40 ):
            print "FAILED CROP TEST " + str(i) + " " + str(img)
            failed = True
        i = i + 1

    if(failed):
        assert False
    results = [crop,crop2,crop6]
    name_stem = "test_image_crop"
    perform_diff(results,name_stem)

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

    results = [crop]
    name_stem = "test_image_region_select"
    perform_diff(results,name_stem)

    diff = crop-img;
    c=diff.meanColor()
    if( c[0] > 0 or c[1] > 0 or c[2] > 0 ):
        assert False

def test_image_subtract():
    imgA = Image(logo)
    imgB = Image(logo_inverted)
    imgC = imgA - imgB
    results = [imgC]
    name_stem = "test_image_subtract"
    perform_diff(results,name_stem)

def test_image_negative():
    imgA = Image(logo)
    imgB = -imgA
    results = [imgB]
    name_stem = "test_image_negative"
    perform_diff(results,name_stem)


def test_image_divide():
    imgA = Image(logo)
    imgB = Image(logo_inverted)

    imgC = imgA / imgB

    results = [imgC]
    name_stem = "test_image_divide"
    perform_diff(results,name_stem)

def test_image_and():
    imgA = Image(barcode)
    imgB = imgA.invert()


    imgC = imgA & imgB # should be all black

    results = [imgC]
    name_stem = "test_image_and"
    perform_diff(results,name_stem)


def test_image_or():
    imgA = Image(barcode)
    imgB = imgA.invert()

    imgC = imgA | imgB #should be all white

    results = [imgC]
    name_stem = "test_image_or"
    perform_diff(results,name_stem)


def test_image_edgemap():
    imgA = Image(logo)
    imgB = imgA._getEdgeMap()
    #results = [imgB]
    #name_stem = "test_image_edgemap"
    #perform_diff(results,name_stem)


def test_color_colormap_build():
    cm = ColorModel()
    #cm.add(Image(logo))
    cm.add((127,127,127))
    if(cm.contains((127,127,127))):
        cm.remove((127,127,127))
    else:
        assert False

    cm.remove((0,0,0))
    cm.remove((255,255,255))
    cm.add((0,0,0))
    cm.add([(0,0,0),(255,255,255)])
    cm.add([(255,0,0),(0,255,0)])
    img = cm.threshold(Image(testimage))
    c=img.meanColor()

    #if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    #  assert False

    cm.save("temp.txt")
    cm2 = ColorModel()
    cm2.load("temp.txt")
    img = Image("logo")
    img2 = cm2.threshold(img)
    cm2.add((0,0,255))
    img3 = cm2.threshold(img)
    cm2.add((255,255,0))
    cm2.add((0,255,255))
    cm2.add((255,0,255))
    img4 = cm2.threshold(img)
    cm2.add(img)
    img5 = cm2.threshold(img)

    results = [img,img2,img3,img4,img5]
    name_stem = "test_color_colormap_build"
    perform_diff(results,name_stem)

    #c=img.meanColor()
    #if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
    #  assert False


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

    lines = imgA.findLines()

    croppedImages = lines.crop()

    if(len(croppedImages) <= 0):
        assert False
    else:
        pass


def test_color_conversion_func_BGR():
    #we'll just go through the space to make sure nothing blows up
    img = Image(testimage)
    results = []
    results.append(img.toBGR())
    results.append(img.toRGB())
    results.append(img.toHLS())
    results.append(img.toHSV())
    results.append(img.toXYZ())

    bgr = img.toBGR()

    results.append(bgr.toBGR())
    results.append(bgr.toRGB())
    results.append(bgr.toHLS())
    results.append(bgr.toHSV())
    results.append(bgr.toXYZ())

    name_stem = "test_color_conversion_func_BGR"
    perform_diff(results,name_stem,tolerance=4.0)


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
    results = [hsv]
    results.append(hsv.toBGR())
    results.append(hsv.toRGB())
    results.append(hsv.toHLS())
    results.append(hsv.toHSV())
    results.append(hsv.toXYZ())
    name_stem = "test_color_conversion_func_HSV"
    perform_diff(results,name_stem,tolerance=4.0 )


def test_color_conversion_func_HLS():
    img = Image(testimage)

    hls = img.toHLS()
    results = [hls]

    results.append(hls.toBGR())
    results.append(hls.toRGB())
    results.append(hls.toHLS())
    results.append(hls.toHSV())
    results.append(hls.toXYZ())

    name_stem = "test_color_conversion_func_HLS"
    perform_diff(results,name_stem,tolerance=4.0)


def test_color_conversion_func_XYZ():
    img = Image(testimage)

    xyz = img.toXYZ()
    results = [xyz]
    results.append(xyz.toBGR())
    results.append(xyz.toRGB())
    results.append(xyz.toHLS())
    results.append(xyz.toHSV())
    results.append(xyz.toXYZ())

    name_stem = "test_color_conversion_func_XYZ"
    perform_diff(results,name_stem,tolerance=8.0)


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
    blobs.draw()
    results = [img]
    name_stem = "test_blob_holes"
    perform_diff(results,name_stem,tolerance=3.0)


    for b in blobs:
        if( b.mHoleContour is not None ):
            count = count + len(b.mHoleContour)
    if( count != 7 ):
        assert False

def test_blob_hull():
    img = Image("../sampleimages/blockhead.png")
    blobber = BlobMaker()
    blobs = blobber.extract(img)
    blobs.draw()

    results = [img]
    name_stem = "test_blob_holes"
    perform_diff(results,name_stem,tolerance=3.0)

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
        if(b.perimeter() > 0):
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
        b.drawMaskToLayer(reimg)

    img.addDrawingLayer(dl)
    results = [img]
    name_stem = "test_blob_render"
    perform_diff(results,name_stem,tolerance=5.0)

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
        b.contour()
        b.aspectRatio()
        b.blobImage()
        b.blobMask()
        b.hullImage()
        b.hullMask()
        b.rectifyMajorAxis()
        b.blobImage()
        b.blobMask()
        b.hullImage()
        b.hullMask()
        b.angle()
        b.above(first)
        b.below(first)
        b.left(first)
        b.right(first)
        #b.contains(first)
        #b.overlaps(first)

def test_image_convolve():
    img = Image(testimageclr)
    kernel = np.array([[0,0,0],[0,1,0],[0,0,0]])
    img2 = img.convolve(kernel,center=(2,2))

    results = [img2]
    name_stem = "test_image_convolve"
    perform_diff(results,name_stem)

    c=img.meanColor()
    d=img2.meanColor()
    e0 = abs(c[0]-d[0])
    e1 = abs(c[1]-d[1])
    e2 = abs(c[2]-d[2])
    if( e0 > 1 or e1 > 1 or e2 > 1 ):
        assert False


def test_detection_ocr():
    img = Image(ocrimage)

    foundtext = img.readText()
    print foundtext
    if(len(foundtext) <= 1):
        assert False
    else:
        pass

def test_template_match():
    source = Image("../sampleimages/templatetest.png")
    template = Image("../sampleimages/template.png")
    t = 2
    fs = source.findTemplate(template,threshold=t)
    fs.draw()
    results = [source]
    name_stem = "test_template_match"
    perform_diff(results,name_stem)

    pass

def test_template_match_once():
    source = Image("../sampleimages/templatetest.png")
    template = Image("../sampleimages/template.png")
    t = 2
    fs = source.findTemplateOnce(template,threshold=t)
    if( len(fs) ==  0 ):
        assert False

    fs = source.findTemplateOnce(template,threshold=t,grayscale=False)
    if( len(fs) ==  0 ):
        assert False

    fs = source.findTemplateOnce(template,method='CCORR_NORM')
    if( len(fs) ==  0 ):
        assert False

    pass

def test_template_match_RGB():
    source = Image("../sampleimages/templatetest.png")
    template = Image("../sampleimages/template.png")
    t = 2
    fs = source.findTemplate(template,threshold=t, grayscale=False)
    fs.draw()
    results = [source]
    name_stem = "test_template_match"
    perform_diff(results,name_stem)

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

    results = []
    w = int(img.width*1.2)
    h = int(img.height*1.2)

    results.append(img.embiggen(size=(w,h),color=Color.RED))
    results.append(img.embiggen(size=(w,h),color=Color.RED,pos=(30,30)))

    results.append(img.embiggen(size=(w,h),color=Color.RED,pos=(-20,-20)))
    results.append(img.embiggen(size=(w,h),color=Color.RED,pos=(30,-20)))
    results.append(img.embiggen(size=(w,h),color=Color.RED,pos=(60,-20)))
    results.append(img.embiggen(size=(w,h),color=Color.RED,pos=(60,30)))

    results.append(img.embiggen(size=(w,h),color=Color.RED,pos=(80,80)))
    results.append(img.embiggen(size=(w,h),color=Color.RED,pos=(30,80)))
    results.append(img.embiggen(size=(w,h),color=Color.RED,pos=(-20,80)))
    results.append(img.embiggen(size=(w,h),color=Color.RED,pos=(-20,30)))

    name_stem = "test_embiggen"
    perform_diff(results,name_stem)

    pass

def test_createBinaryMask():
    img2 = Image(logo)
    results = []
    results.append(img2.createBinaryMask(color1=(0,100,100),color2=(255,200,200)))
    results.append(img2.createBinaryMask(color1=(0,0,0),color2=(128,128,128)))
    results.append(img2.createBinaryMask(color1=(0,0,128),color2=(255,255,255)))

    name_stem = "test_createBinaryMask"
    perform_diff(results,name_stem)

    pass

def test_applyBinaryMask():
    img = Image(logo)
    mask = img.createBinaryMask(color1=(0,128,128),color2=(255,255,255))
    results = []
    results.append(img.applyBinaryMask(mask))
    results.append(img.applyBinaryMask(mask,bg_color=Color.RED))

    name_stem = "test_applyBinaryMask"
    perform_diff(results,name_stem,tolerance=3.0)

    pass

def test_applyPixelFunc():
    img = Image(logo)
    def myFunc((r,g,b)):
        return( (b,g,r) )

    img = img.applyPixelFunction(myFunc)
    name_stem = "test_applyPixelFunc"
    results = [img]
    perform_diff(results,name_stem)
    pass

def test_applySideBySide():
    img = Image(logo)
    img3 = Image(testimage2)

    #LB = little image big image
    #BL = big image little image  -> this is important to test all the possible cases.
    results = []

    results.append(img3.sideBySide(img,side='right',scale=False))
    results.append(img3.sideBySide(img,side='left',scale=False))
    results.append(img3.sideBySide(img,side='top',scale=False))
    results.append(img3.sideBySide(img,side='bottom',scale=False))

    results.append(img.sideBySide(img3,side='right',scale=False))
    results.append(img.sideBySide(img3,side='left',scale=False))
    results.append(img.sideBySide(img3,side='top',scale=False))
    results.append(img.sideBySide(img3,side='bottom',scale=False))

    results.append(img3.sideBySide(img,side='right',scale=True))
    results.append(img3.sideBySide(img,side='left',scale=True))
    results.append(img3.sideBySide(img,side='top',scale=True))
    results.append(img3.sideBySide(img,side='bottom',scale=True))

    results.append(img.sideBySide(img3,side='right',scale=True))
    results.append(img.sideBySide(img3,side='left',scale=True))
    results.append(img.sideBySide(img3,side='top',scale=True))
    results.append(img.sideBySide(img3,side='bottom',scale=True))

    name_stem = "test_applySideBySide"
    perform_diff(results,name_stem)

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

    results = [img2,img3,img4]
    name_stem = "test_resize"
    perform_diff(results,name_stem)


def test_createAlphaMask():
    alphaMask = Image(alphaSrcImg)
    mask = alphaMask.createAlphaMask(hue=60)
    mask2 = alphaMask.createAlphaMask(hue_lb=59,hue_ub=61)
    top = Image(topImg)
    bottom = Image(bottomImg)
    bottom = bottom.blit(top,alphaMask=mask2)
    results = [mask,mask2,bottom]
    name_stem = "test_createAlphaMask"
    perform_diff(results,name_stem)


def test_blit_regular():
    top = Image(topImg)
    bottom = Image(bottomImg)
    results = []
    results.append(bottom.blit(top))
    results.append(bottom.blit(top,pos=(-10,-10)))
    results.append(bottom.blit(top,pos=(-10,10)))
    results.append(bottom.blit(top,pos=(10,-10)))
    results.append(bottom.blit(top,pos=(10,10)))

    name_stem = "test_blit_regular"
    perform_diff(results,name_stem)

    pass

def test_blit_mask():
    top = Image(topImg)
    bottom = Image(bottomImg)
    mask = Image(maskImg)
    results = []
    results.append(bottom.blit(top,mask=mask))
    results.append(bottom.blit(top,mask=mask,pos=(-50,-50)))
    results.append(bottom.blit(top,mask=mask,pos=(-50,50)))
    results.append(bottom.blit(top,mask=mask,pos=(50,-50)))
    results.append(bottom.blit(top,mask=mask,pos=(50,50)))

    name_stem = "test_blit_mask"
    perform_diff(results,name_stem)

    pass


def test_blit_alpha():
    top = Image(topImg)
    bottom = Image(bottomImg)
    a = 0.5
    results = []
    results.append(bottom.blit(top,alpha=a))
    results.append(bottom.blit(top,alpha=a,pos=(-50,-50)))
    results.append(bottom.blit(top,alpha=a,pos=(-50,50)))
    results.append(bottom.blit(top,alpha=a,pos=(50,-50)))
    results.append(bottom.blit(top,alpha=a,pos=(50,50)))
    name_stem = "test_blit_alpha"
    perform_diff(results,name_stem)

    pass


def test_blit_alpha_mask():
    top = Image(topImg)
    bottom = Image(bottomImg)
    aMask = Image(alphaMaskImg)
    results = []

    results.append(bottom.blit(top,alphaMask=aMask))
    results.append(bottom.blit(top,alphaMask=aMask,pos=(-10,-10)))
    results.append(bottom.blit(top,alphaMask=aMask,pos=(-10,10)))
    results.append(bottom.blit(top,alphaMask=aMask,pos=(10,-10)))
    results.append(bottom.blit(top,alphaMask=aMask,pos=(10,10)))

    name_stem = "test_blit_alpha_mask"
    perform_diff(results,name_stem)

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
    results = [output,output2]
    name_stem = "test_whiteBalance"
    perform_diff(results,name_stem)

def test_hough_circles():
    img = Image(circles)
    circs = img.findCircle(thresh=100)
    circs.draw()
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

    results = [img,img2,img3]
    name_stem = "test_hough_circle"
    perform_diff(results,name_stem)


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

    results = [img]
    name_stem = "test_drawRectangle"
    perform_diff(results,name_stem)

    pass


def test_BlobMinRect():
    img = Image(testimageclr)
    blobs = img.findBlobs()
    for b in blobs:
        b.drawMinRect(color=Color.BLUE,width=3,alpha=123)
    results = [img]
    name_stem = "test_BlobMinRect"
    perform_diff(results,name_stem)
    pass

def test_BlobRect():
    img = Image(testimageclr)
    blobs = img.findBlobs()
    for b in blobs:
        b.drawRect(color=Color.BLUE,width=3,alpha=123)

    results = [img]
    name_stem = "test_BlobRect"
    perform_diff(results,name_stem)
    pass


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
    try:
        import cv2
    except:
        pass
        return
    img = Image(testimage2)
    if cv2.__version__.startswith('$Rev:'):
        flavors = ['SURF','STAR','SIFT'] # supported in 2.3.1
    elif cv2.__version__ == '2.4.0' or cv2.__version__ == '2.4.1':
        flavors = ['SURF','STAR','FAST','MSER','ORB','BRISK','SIFT','Dense']
    else:
        flavors = ['SURF','STAR','FAST','MSER','ORB','BRISK','FREAK','SIFT','Dense']
    for flavor in flavors:
        try:
            print "trying to find " + flavor + " keypoints."
            kp = img.findKeypoints(flavor=flavor)
        except:
            continue
        if( kp is not None ):
            print "Found: " + str(len(kp))
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
            kp.draw()
        else:
            print "Found None."
    results = [img]
    name_stem = "test_findKeypoints"
    #~ perform_diff(results,name_stem)

    pass

def test_movement_feature():
    current1 = Image("../sampleimages/flow_simple1.png")
    prev = Image("../sampleimages/flow_simple2.png")

    fs = current1.findMotion(prev, window=7)
    if( len(fs) > 0 ):
        fs.draw(color=Color.RED)
        img = fs[0].crop()
        color = fs[1].meanColor()
        wndw = fs[1].windowSz()
        for f in fs:
            f.vector()
            f.magnitude()
    else:
        assert False


    current2 = Image("../sampleimages/flow_simple1.png")
    fs = current2.findMotion(prev, window=7,method='HS')
    if( len(fs) > 0 ):
        fs.draw(color=Color.RED)
        img = fs[0].crop()
        color = fs[1].meanColor()
        wndw = fs[1].windowSz()
        for f in fs:
            f.vector()
            f.magnitude()
    else:
        assert False

    current3 = Image("../sampleimages/flow_simple1.png")
    fs = current3.findMotion(prev, window=7,method='LK',aggregate=False)
    if( len(fs) > 0 ):
        fs.draw(color=Color.RED)
        img = fs[0].crop()
        color = fs[1].meanColor()
        wndw = fs[1].windowSz()
        for f in fs:
            f.vector()
            f.magnitude()
    else:
        assert False

    results = [current1,current2,current3]
    name_stem = "test_movement_feature"
    #~ perform_diff(results,name_stem,tolerance=4.0)

    pass

def test_keypoint_extraction():
    try:
        import cv2
    except:
        pass
        return

    img1 = Image("../sampleimages/KeypointTemplate2.png")
    img2 = Image("../sampleimages/KeypointTemplate2.png")
    img3 = Image("../sampleimages/KeypointTemplate2.png")
    img4 = Image("../sampleimages/KeypointTemplate2.png")

    kp1 = img1.findKeypoints()
    kp2 = img2.findKeypoints(highQuality=True)
    kp3 = img3.findKeypoints(flavor="STAR")
    if not cv2.__version__.startswith("$Rev:"):
        kp4 = img4.findKeypoints(flavor="BRISK")
        kp4.draw()
        if len(kp4) == 0:
            assert False
    kp1.draw()
    kp2.draw()
    kp3.draw()



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
    results = [img1,img2,img3]
    name_stem = "test_keypoint_extraction"
    perform_diff(results,name_stem,tolerance=4.0)


def test_keypoint_match():
    try:
        import cv2
    except:
        pass
        return

    template = Image("../sampleimages/KeypointTemplate2.png")
    match0 = Image("../sampleimages/kptest0.png")
    match1 = Image("../sampleimages/kptest1.png")
    match3 = Image("../sampleimages/kptest2.png")
    match2 = Image("../sampleimages/aerospace.jpg")# should be none

    fs0 = match0.findKeypointMatch(template)#test zero
    fs1 = match1.findKeypointMatch(template,quality=300.00,minDist=0.5,minMatch=0.2)
    fs3 = match3.findKeypointMatch(template,quality=300.00,minDist=0.5,minMatch=0.2)
    print "This should fail"
    fs2 = match2.findKeypointMatch(template,quality=500.00,minDist=0.2,minMatch=0.1)
    if( fs0 is not None and fs1 is not None and fs2 is None and  fs3 is not None):
        fs0.draw()
        fs1.draw()
        fs3.draw()
        f = fs0[0]
        f.drawRect()
        f.draw()
        f.getHomography()
        f.getMinRect()
        f.x
        f.y
        f.coordinates()
    else:
        assert False

    results = [match0,match1,match2,match3]
    name_stem = "test_find_keypoint_match"
    perform_diff(results,name_stem)


def test_draw_keypoint_matches():
    try:
        import cv2
    except:
        pass
        return
    template = Image("../sampleimages/KeypointTemplate2.png")
    match0 = Image("../sampleimages/kptest0.png")
    result = match0.drawKeypointMatches(template,thresh=500.00,minDist=0.15,width=1)

    results = [result]
    name_stem = "test_draw_keypoint_matches"
    perform_diff(results,name_stem,tolerance=4.0)


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
    img4 = img.palettize(centroids=[Color.WHITE,Color.RED,Color.BLUE,Color.GREEN,Color.BLACK])
    img4 = img.palettize(hue=True,centroids=[(0),(30),(60),(180)])
    #UHG@! can't diff because of the kmeans initial conditions causes
    # things to bounce around... otherwise we need to set a friggin huge tolerance

    #results = [img2,img3]
    #name_stem = "test_palettize"
    #perform_diff(results,name_stem)
    pass

def test_repalette():
    img = Image(testimageclr)
    img2 = Image(bottomImg)
    p = img.getPalette()
    img3 = img2.rePalette(p)
    p = img.getPalette(hue=True)
    img4 = img2.rePalette(p,hue=True)

    #results = [img3,img4]
    #name_stem = "test_repalette"
    #perform_diff(results,name_stem)

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
    p = img.getPalette(hue=True)
    img2 = img.binarizeFromPalette(p[0:5])

    pass

def test_palette_blobs():
    img = Image(testimageclr)
    p = img.getPalette()
    b1 = img.findBlobsFromPalette(p[0:5])
    b1.draw()


    p = img.getPalette(hue=True)
    b2 = img.findBlobsFromPalette(p[0:5])
    b2.draw()

    if( len(b1) > 0 and len(b2) > 0 ):
        pass
    else:
        assert False



def test_skeletonize():
    img = Image(logo)
    s = img.skeletonize()
    s2 = img.skeletonize(10)

    results = [s,s2]
    name_stem = "test_skelotinze"
    perform_diff(results,name_stem)

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
    new_mask1 = img.smartThreshold(mask=mask)
    new_mask2 = img.smartThreshold(rect=(30,30,150,185))


    results = [new_mask1,new_mask2]
    name_stem = "test_smartThreshold"
    perform_diff(results,name_stem)

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
    results = [img]

    if( len(blobs) < 1 ):
        assert False

    for t in range(2,3):
        img = Image("../sampleimages/RatTop.png")
        blobs2 = img.smartFindBlobs(rect=(30,30,150,185),thresh_level=t)
        if(blobs2 is not None):
            blobs2.draw()
            results.append(img)

    name_stem = "test_smartFindBlobs"
    perform_diff(results,name_stem)

    pass


def test_image_webp_load():
    #only run if webm suppport exist on system
    try:
        import webm
    except:
        if( SHOW_WARNING_TESTS ):
            logger.warning("Couldn't run the webp test as optional webm library required")
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
            logger.warning("Couldn't run the webp test as optional webm library required")
        pass

    else:
        img = Image('simplecv')
        tf = tempfile.NamedTemporaryFile(suffix=".webp")
        if img.save(tf.name):
            pass
        else:
            assert False

def test_detection_spatial_relationships():
    img = Image(testimageclr)
    template = img.crop(200,200,50,50)
    motion = img.embiggen((img.width+10,img.height+10),pos=(10,10))
    motion = motion.crop(0,0,img.width,img.height)
    blobFS = img.findBlobs()
    lineFS = img.findLines()
    cornFS = img.findCorners()
    moveFS = img.findMotion(motion)
    moveFS = FeatureSet(moveFS[42:52]) # l337 s5p33d h4ck - okay not really
    tempFS = img.findTemplate(template,threshold=1)
    aCirc = (img.width/2,img.height/2,np.min([img.width/2,img.height/2]))
    aRect = (50,50,200,200)
    aPoint = (img.width/2,img.height/2)
    aPoly =  [(0,0),(img.width/2,0),(0,img.height/2)] # a triangle


    feats  = [blobFS,lineFS,cornFS,tempFS,moveFS]

    for f in feats:
        print str(len(f))

    for f in feats:
        for g in feats:

            sample = f[0]
            sample2 = f[1]
            print type(f[0])
            print type(g[0])

            g.above(sample)
            g.below(sample)
            g.left(sample)
            g.right(sample)
            g.overlaps(sample)
            g.inside(sample)
            g.outside(sample)

            g.inside(aRect)
            g.outside(aRect)

            g.inside(aCirc)
            g.outside(aCirc)

            g.inside(aPoly)
            g.outside(aPoly)

            g.above(aPoint)
            g.below(aPoint)
            g.left(aPoint)
            g.right(aPoint)


    pass

def test_getEXIFData():
    img = Image("../sampleimages/cat.jpg")
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

    results = [lm3,lm1]
    name_stem = "test_getDFTLogMagnitude"
    perform_diff(results,name_stem,tolerance=6.0)

    pass


def test_applyDFTFilter():
    img = Image("../sampleimages/RedDog2.jpg")
    flt = Image("../sampleimages/RedDogFlt.png")
    f1 = img.applyDFTFilter(flt)
    f2 = img.applyDFTFilter(flt,grayscale=True)
    results = [f1,f2]
    name_stem = "test_applyDFTFilter"
    perform_diff(results,name_stem)
    pass

def test_highPassFilter():
    img = Image("../sampleimages/RedDog2.jpg")
    a = img.highPassFilter(0.5)
    b = img.highPassFilter(0.5,grayscale=True)
    c = img.highPassFilter(0.5,yCutoff=0.4)
    d = img.highPassFilter(0.5,yCutoff=0.4,grayscale=True)
    e = img.highPassFilter([0.5,0.4,0.3])
    f = img.highPassFilter([0.5,0.4,0.3],yCutoff=[0.5,0.4,0.3])

    results = [a,b,c,d,e,f]
    name_stem = "test_HighPassFilter"
    perform_diff(results,name_stem)
    pass

def test_lowPassFilter():
    img = Image("../sampleimages/RedDog2.jpg")
    a = img.lowPassFilter(0.5)
    b = img.lowPassFilter(0.5,grayscale=True)
    c = img.lowPassFilter(0.5,yCutoff=0.4)
    d = img.lowPassFilter(0.5,yCutoff=0.4,grayscale=True)
    e = img.lowPassFilter([0.5,0.4,0.3])
    f = img.lowPassFilter([0.5,0.4,0.3],yCutoff=[0.5,0.4,0.3])

    results = [a,b,c,d,e,f]
    name_stem = "test_LowPassFilter"
    perform_diff(results,name_stem)

    pass

def test_DFT_gaussian():
    img = Image("../sampleimages/RedDog2.jpg")
    flt = DFT.createGaussianFilter(dia=300, size=(300, 300), highpass=False)
    fltimg = img.filter(flt)
    fltimggray = img.filter(flt, grayscale=True)
    flt = DFT.createGaussianFilter(dia=300, size=(300, 300), highpass=True)
    fltimg1 = img.filter(flt)
    fltimggray1 = img.filter(flt, grayscale=True)
    results = [fltimg, fltimggray, fltimg1, fltimggray1]
    name_stem = "test_DFT_gaussian"
    perform_diff(results, name_stem)
    pass

def test_DFT_butterworth():
    img = Image("../sampleimages/RedDog2.jpg")
    flt = DFT.createButterworthFilter(dia=300, size=(300, 300), order=3, highpass=False)
    fltimg = img.filter(flt)
    fltimggray = img.filter(flt, grayscale=True)
    flt = DFT.createButterworthFilter(dia=100, size=(300, 300), order=3, highpass=True)
    fltimg1 = img.filter(flt)
    fltimggray1 = img.filter(flt, grayscale=True)
    results = [fltimg, fltimggray, fltimg1, fltimggray1]
    name_stem = "test_DFT_butterworth"
    perform_diff(results, name_stem)
    pass

def test_DFT_lowpass():
    img = Image("../sampleimages/RedDog2.jpg")
    flt = DFT.createLowpassFilter(xCutoff=150, size=(600, 600))
    fltimg = img.filter(flt)
    fltimggray = img.filter(flt, grayscale=True)
    results = [fltimg, fltimggray]
    name_stem = "test_DFT_lowpass"
    perform_diff(results, name_stem, 20)
    pass

def test_DFT_highpass():
    img = Image("../sampleimages/RedDog2.jpg")
    flt = DFT.createLowpassFilter(xCutoff=10, size=(600, 600))
    fltimg = img.filter(flt)
    fltimggray = img.filter(flt, grayscale=True)
    results = [fltimg, fltimggray]
    name_stem = "test_DFT_highpass"
    perform_diff(results, name_stem, 20)
    pass

def test_DFT_notch():
    img = Image("../sampleimages/RedDog2.jpg")
    flt = DFT.createNotchFilter(dia1=500, size=(512, 512), type="lowpass")
    fltimg = img.filter(flt)
    fltimggray = img.filter(flt, grayscale=True)
    flt = DFT.createNotchFilter(dia1=300, size=(512, 512), type="highpass")
    fltimg1 = img.filter(flt)
    fltimggray1 = img.filter(flt, grayscale=True)
    results = [fltimg, fltimggray, fltimg1, fltimggray1]
    name_stem = "test_DFT_notch"
    perform_diff(results, name_stem, 20)

def test_findHaarFeatures():
    img = Image("../sampleimages/orson_welles.jpg")
    face = HaarCascade("face.xml") #old HaarCascade
    f = img.findHaarFeatures(face)
    f2 = img.findHaarFeatures("face_cv2.xml") #new cv2 HaarCascade
    if( len(f) > 0 and len(f2) > 0 ):
        f.draw()
        f2.draw()
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

    results = [img]
    name_stem = "test_findHaarFeatures"
    perform_diff(results,name_stem)


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
    img.floodFill((30,30),lower=(3,3,3),upper=(5,5,5),color=np.array([255,0,0]))
    img.floodFill((30,30),lower=(3,3,3),upper=(5,5,5),color=[255,0,0])

    results = [img]
    name_stem = "test_biblical_flood_fill"
    perform_diff(results,name_stem)

    pass

def test_flood_fill_to_mask():
    img = Image(testimage2)
    b = img.findBlobs()
    imask = img.edges()
    omask = img.floodFillToMask(b.coordinates(),tolerance=10)
    omask2 = img.floodFillToMask(b.coordinates(),tolerance=(3,3,3),mask=imask)
    omask3 = img.floodFillToMask(b.coordinates(),tolerance=(3,3,3),mask=imask,fixed_range=False)

    results = [omask,omask2,omask3]
    name_stem = "test_flood_fill_to_mask"
    perform_diff(results,name_stem)

    pass

def test_findBlobsFromMask():
    img = Image(testimage2)
    mask = img.binarize().invert()
    b1 = img.findBlobsFromMask(mask)
    b2 = img.findBlobs()
    b1.draw()
    b2.draw()

    results = [img]
    name_stem = "test_findBlobsFromMask"
    perform_diff(results,name_stem)


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
    results = [a,b,c,d,e,f]
    name_stem = "test_bandPassFilter"
    perform_diff(results,name_stem)


def test_image_slice():
    img = Image("../sampleimages/blockhead.png")
    I = img.findLines()
    I2 = I[0:10]
    if type(I2) == list:
        assert False
    else:
        pass

def test_blob_spatial_relationships():
    img = Image("../sampleimages/spatial_relationships.png")
    #please see the image
    blobs = img.findBlobs(threshval=1)
    blobs = blobs.sortArea()
    print(len(blobs))

    center = blobs[-1]
    top = blobs[-2]
    right = blobs[-3]
    bottom = blobs[-4]
    left = blobs[-5]
    inside = blobs[-7]
    overlap = blobs[-6]

    if( not top.above(center) ):
        assert False
    if( not bottom.below(center)):
        assert False
    if( not right.right(center)):
        assert False
    if( not left.left(center)):
        assert False

    if( not center.contains(inside)):
        assert False

    if( center.contains(left) ):
        assert False

    if( not center.overlaps(overlap) ):
        assert False

    if( not overlap.overlaps(center) ):
        assert False

    myTuple = (img.width/2,img.height/2)

    if( not top.above(myTuple) ):
        assert False
    if( not bottom.below(myTuple)):
        assert False
    if( not right.right(myTuple)):
        assert False
    if( not left.left(myTuple)):
        assert False

    if( not top.above(myTuple) ):
        assert False
    if( not bottom.below(myTuple)):
        assert False
    if( not right.right(myTuple)):
        assert False
    if( not left.left(myTuple)):
        assert False
    if( not center.contains(myTuple)):
        assert False

    myNPA = np.array([img.width/2,img.height/2])
    if( not top.above(myNPA) ):
        assert False
    if( not bottom.below(myNPA)):
        assert False
    if( not right.right(myNPA)):
        assert False
    if( not left.left(myNPA)):
        assert False
    if( not center.contains(myNPA)):
        assert False

    if( not center.contains(inside) ):
        assert False

def test_get_aspectratio():
    img = Image("../sampleimages/EdgeTest1.png")
    img2 = Image("../sampleimages/EdgeTest2.png")
    b = img.findBlobs()
    l = img2.findLines()
    c = img2.findCircle(thresh=200)
    c2 = img2.findCorners()
    kp = img2.findKeypoints()
    bb = b.aspectRatios()
    ll = l.aspectRatios()
    cc = c.aspectRatios()
    c22 = c2.aspectRatios()
    kp2 = kp.aspectRatios()

    if( len(bb) > 0 and
        len(ll) > 0 and
        len(cc) > 0 and
        len(c22) > 0 and
        len(kp2) > 0 ):
        pass
    else:
        assert False

def test_line_crop():
    img = Image("../sampleimages/EdgeTest2.png")
    l = img.findLines().sortArea()
    l = l[-5:-1]
    results = []
    for ls in l:
        results.append( ls.crop() )
    name_stem = "test_lineCrop"
    perform_diff(results,name_stem,tolerance=3.0)
    pass

def test_get_corners():
    img = Image("../sampleimages/EdgeTest1.png")
    img2 = Image("../sampleimages/EdgeTest2.png")
    b = img.findBlobs()
    tl = b.topLeftCorners()
    tr = b.topRightCorners()
    bl = b.bottomLeftCorners()
    br = b.bottomRightCorners()

    l = img2.findLines()
    tl2 = l.topLeftCorners()
    tr2 = l.topRightCorners()
    bl2 = l.bottomLeftCorners()
    br2 = l.bottomRightCorners()

    if( tl is not None and
        tr is not None and
        bl is not None and
        br is not None and
        tl2 is not None and
        tr2 is not None and
        bl2 is not None and
        br2 is not None ):
        pass
    else:
        assert False

def test_save_kwargs():
    img = Image("lenna")
    l95 = "l95.jpg"
    l90 = "l90.jpg"
    l80 ="l80.jpg"
    l70="l70.jpg"

    img.save(l95,quality=95)
    img.save(l90,quality=90)
    img.save(l80,quality=80)
    img.save(l70,quality=75)

    s95 = os.stat(l95).st_size
    s90 = os.stat(l90).st_size
    s80 = os.stat(l80).st_size
    s70 = os.stat(l70).st_size

    if( s70 < s80 and s80 < s90 and s90 < s95 ):
        pass
    else:
        assert False

    s95 = os.remove(l95)
    s90 = os.remove(l90)
    s80 = os.remove(l80)
    s70 = os.remove(l70)

def test_on_edge():
    img1 = "./../sampleimages/EdgeTest1.png"
    img2 = "./../sampleimages/EdgeTest2.png"
    imgA = Image(img1)
    imgB = Image(img2)
    imgC = Image(img2)
    imgD = Image(img2)
    imgE = Image(img2)

    blobs = imgA.findBlobs()
    circs = imgB.findCircle(thresh=200)
    corners = imgC.findCorners()
    kp = imgD.findKeypoints()
    lines = imgE.findLines()

    rim =  blobs.onImageEdge()
    inside = blobs.notOnImageEdge()
    rim.draw(color=Color.RED)
    inside.draw(color=Color.BLUE)

    rim =  circs.onImageEdge()
    inside = circs.notOnImageEdge()
    rim.draw(color=Color.RED)
    inside.draw(color=Color.BLUE)

    #rim =  corners.onImageEdge()
    inside = corners.notOnImageEdge()
    #rim.draw(color=Color.RED)
    inside.draw(color=Color.BLUE)

    #rim =  kp.onImageEdge()
    inside = kp.notOnImageEdge()
    #rim.draw(color=Color.RED)
    inside.draw(color=Color.BLUE)

    rim =  lines.onImageEdge()
    inside = lines.notOnImageEdge()
    rim.draw(color=Color.RED)
    inside.draw(color=Color.BLUE)

    results = [imgA,imgB,imgC,imgD,imgE]
    name_stem = "test_onEdge_Features"
    #~ perform_diff(results,name_stem,tolerance=8.0)

def test_feature_angles():
    img = Image("../sampleimages/rotation2.png")
    img2 = Image("../sampleimages/rotation.jpg")
    img3 = Image("../sampleimages/rotation.jpg")
    b = img.findBlobs()
    l = img2.findLines()
    k = img3.findKeypoints()

    for bs in b:
        tl = bs.topLeftCorner()
        img.drawText(str(bs.angle()),tl[0],tl[1],color=Color.RED)

    for ls in l:
        tl = ls.topLeftCorner()
        img2.drawText(str(ls.angle()),tl[0],tl[1],color=Color.GREEN)

    for ks in k:
        tl = ks.topLeftCorner()
        img3.drawText(str(ks.angle()),tl[0],tl[1],color=Color.BLUE)

    results = [img,img2,img3]
    name_stem = "test_feature_angles"
    perform_diff(results,name_stem,tolerance=11.0)

def test_feature_angles_rotate():
    img = Image("../sampleimages/rotation2.png")
    b = img.findBlobs()
    results = []

    for bs in b:
        temp = bs.crop()
        derp = temp.rotate(bs.angle(),fixed=False)
        derp.drawText(str(bs.angle()),10,10,color=Color.RED)
        results.append(derp)
        bs.rectifyMajorAxis()
        results.append(bs.blobImage())

    name_stem = "test_feature_angles_rotate"
    perform_diff(results,name_stem,tolerance=7.0)


def test_nparray2cvmat():
    img = Image('logo')
    gray = img.getGrayNumpy()
    gf32 = np.array(gray,dtype='float32')
    gf64 = np.array(gray,dtype='float64')

    a = npArray2cvMat(gray)
    b = npArray2cvMat(gf32)
    c = npArray2cvMat(gf64)

    a = npArray2cvMat(gray,cv.CV_8UC1)
    b = npArray2cvMat(gf32,cv.CV_8UC1)
    c = npArray2cvMat(gf64,cv.CV_8UC1)

def test_minrect_blobs():
    img = Image("../sampleimages/bolt.png")
    img = img.invert()
    results = []
    for i in range(-10,10):
        ang = float(i*18.00)
        print ang
        t = img.rotate(ang)
        b = t.findBlobs(threshval=128)
        b[-1].drawMinRect(color=Color.RED,width=5)
        results.append(t)

    name_stem = "test_minrect_blobs"
    perform_diff(results,name_stem,tolerance=11.0)

def test_pixelize():
    img = Image("../sampleimages/The1970s.png")
    img1 = img.pixelize(4)
    img2 = img.pixelize((5,13))
    img3 = img.pixelize((img.width/10,img.height))
    img4 = img.pixelize((img.width,img.height/10))
    img5 = img.pixelize((12,12),(200,180,250,250))
    img6 = img.pixelize((12,12),(600,80,250,250))
    img7 = img.pixelize((12,12),(600,80,250,250),levels=4)
    img8 = img.pixelize((12,12),levels=6)
    #img9 = img.pixelize(4, )
    #img10 = img.pixelize((5,13))
    #img11 = img.pixelize((img.width/10,img.height), mode=True)
    #img12 = img.pixelize((img.width,img.height/10), mode=True)
    #img13 = img.pixelize((12,12),(200,180,250,250), mode=True)
    #img14 = img.pixelize((12,12),(600,80,250,250), mode=True)
    #img15 = img.pixelize((12,12),(600,80,250,250),levels=4, mode=True)
    #img16 = img.pixelize((12,12),levels=6, mode=True)

    results = [img1,img2,img3,img4,img5,img6,img7,img8] #img9,img10,img11,img12,img13,img14,img15,img16]
    name_stem = "test_pixelize"
    perform_diff(results,name_stem,tolerance=6.0)

def test_hueFromRGB():
    img = Image("lenna")
    img_hsv = img.toHSV()
    h,s,r = img_hsv[100,300]
    err = 2
    hue = Color.getHueFromRGB(img[100,300])
    if hue > h - err and hue < h + err:
        pass
    else:
        assert False

def test_hueFromBGR():
    img = Image("lenna")
    img_hsv = img.toHSV()
    h,s,r = img_hsv[150,400]
    err = 2
    color_tuple = tuple(reversed(img[150,400]))
    hue = Color.getHueFromBGR(color_tuple)
    if hue > h - err and hue < h + err:
        pass
    else:
        assert False

def test_hueToRGB():
    r,g,b = Color.hueToRGB(0)
    if (r,g,b)== (255,0,0):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(15)
    if (r,g,b) == (255,128,0):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(30)
    if (r,g,b) == (255,255,0):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(45)
    if (r,g,b) == (128,255,0):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(60)
    if (r,g,b) == (0,255,0):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(75)
    if (r,g,b) == (0,255,128):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(90)
    if (r,g,b) == (0,255,255):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(105)
    if (r,g,b) == (0,128,255):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(120)
    if (r,g,b) == (0,0,255):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(135)
    if (r,g,b) == (128,0,255):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(150)
    if (r,g,b) == (255,0,255):
        pass
    else:
        assert False
    r,g,b = Color.hueToRGB(165)
    if (r,g,b) == (255,0,128):
        pass
    else:
        assert False

def test_hueToBGR():
    b,g,r = Color.hueToBGR(0)
    if (r,g,b)== (255,0,0):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(15)
    if (r,g,b) == (255,128,0):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(30)
    if (r,g,b) == (255,255,0):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(45)
    if (r,g,b) == (128,255,0):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(60)
    if (r,g,b) == (0,255,0):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(75)
    if (r,g,b) == (0,255,128):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(90)
    if (r,g,b) == (0,255,255):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(105)
    if (r,g,b) == (0,128,255):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(120)
    if (r,g,b) == (0,0,255):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(135)
    if (r,g,b) == (128,0,255):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(150)
    if (r,g,b) == (255,0,255):
        pass
    else:
        assert False
    b,g,r= Color.hueToBGR(165)
    if (r,g,b) == (255,0,128):
        pass
    else:
        assert False



def test_point_intersection():
    img = Image("simplecv")
    e = img.edges(0,100)
    for x in range(25,225,25):
        a = (x,25)
        b = (125,125)
        pts = img.edgeIntersections(a,b,width=1)
        e.drawLine(a,b,color=Color.RED)
        e.drawCircle(pts[0],10,color=Color.GREEN)

    for x in range(25,225,25):
        a = (25,x)
        b = (125,125)
        pts = img.edgeIntersections(a,b,width=1)
        e.drawLine(a,b,color=Color.RED)
        e.drawCircle(pts[0],10,color=Color.GREEN)

    for x in range(25,225,25):
        a = (x,225)
        b = (125,125)
        pts = img.edgeIntersections(a,b,width=1)
        e.drawLine(a,b,color=Color.RED)
        e.drawCircle(pts[0],10,color=Color.GREEN)

    for x in range(25,225,25):
        a = (225,x)
        b = (125,125)
        pts = img.edgeIntersections(a,b,width=1)
        e.drawLine(a,b,color=Color.RED)
        e.drawCircle(pts[0],10,color=Color.GREEN)

    results = [e]
    name_stem = "test_point_intersection"
    perform_diff(results,name_stem,tolerance=6.0)

def test_findSkintoneBlobs():
    img = Image('../sampleimages/04000.jpg')

    blobs = img.findSkintoneBlobs()
    for b in blobs:
        if(b.mArea > 0):
            pass
        if(b.perimeter() > 0):
            pass
        if(b.mAvgColor[0] > 5 and b.mAvgColor[1]>140 and b.mAvgColor[1]<180 and b.mAvgColor[2]>77 and b.mAvgColor[2]<135):
            pass


def test_getSkintoneMask():
    imgSet = []
    imgSet.append(Image('../sampleimages/040000.jpg'))
    imgSet.append(Image('../sampleimages/040001.jpg'))
    imgSet.append(Image('../sampleimages/040002.jpg'))
    imgSet.append(Image('../sampleimages/040003.jpg'))
    imgSet.append(Image('../sampleimages/040004.jpg'))
    imgSet.append(Image('../sampleimages/040005.jpg'))
    imgSet.append(Image('../sampleimages/040006.jpg'))
    imgSet.append(Image('../sampleimages/040007.jpg'))
    masks = [img.getSkintoneMask() for img in imgSet]
    VISUAL_TEST = True
    name_stem = 'test_skintone'
    perform_diff(masks,name_stem,tolerance=17)

def test_findKeypoints_all():
    try:
        import cv2
    except:
        pass
        return
    img = Image(testimage2)
    methods = ["ORB", "SIFT", "SURF","FAST", "STAR", "MSER", "Dense"]
    for i in methods :
        print i
        try:
            kp = img.findKeypoints(flavor = i)
        except:
            continue
        if kp!=None :
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
            kp.draw()
        results = [img]
        name_stem = "test_findKeypoints"
        #~ perform_diff(results,name_stem,tolerance=8)
    pass


def test_upload_flickr():
    try:
        import flickrapi
    except:
        if( SHOW_WARNING_TESTS ):
            logger.warning("Couldn't run the upload test as optional flickr library required")
        pass
    else:
        img = Image('simplecv')
        api_key = None
        api_secret = None
        if api_key==None or api_secret==None :
            pass
        else :
            try:
                ret=img.upload('flickr',api_key,api_secret)
                if ret :
                    pass
                else :
                    assert False
            except: # we will chock this up to key errors
                pass

def test_image_new_crop():
    img = Image(logo)
    x = 5
    y = 6
    w = 10
    h = 20
    crop = img.crop((x,y,w,h))
    crop1 = img.crop([x,y,w,h])
    crop2 = img.crop((x,y),(x+w,y+h))
    crop3 = img.crop([(x,y),(x+w,y+h)])
    if( SHOW_WARNING_TESTS ):
        crop7 = img.crop((0,0,-10,10))
        crop8 = img.crop((-50,-50),(10,10))
        crop3 = img.crop([(-3,-3),(10,20)])
        crop4 = img.crop((-10,10,20,20),centered=True)
        crop5 = img.crop([-10,-10,20,20])

    results = [crop,crop1,crop2,crop3]
    name_stem = "test_image_new_crop"
    perform_diff(results,name_stem)

    diff = crop-crop1;
    c=diff.meanColor()
    if( c[0] > 0 or c[1] > 0 or c[2] > 0 ):
        assert False

def test_image_temp_save():
    img1 = Image("lenna")
    img2 = Image(logo)
    path = []
    path.append(img1.save(temp=True))
    path.append(img2.save(temp=True))
    for i in path :
        if i==None :
            assert False

    assert True



def test_image_set_average():
    iset = ImageSet()
    iset.append(Image("./../sampleimages/tracktest0.jpg"))
    iset.append(Image("./../sampleimages/tracktest1.jpg"))
    iset.append(Image("./../sampleimages/tracktest2.jpg"))
    iset.append(Image("./../sampleimages/tracktest3.jpg"))
    iset.append(Image("./../sampleimages/tracktest4.jpg"))
    iset.append(Image("./../sampleimages/tracktest5.jpg"))
    iset.append(Image("./../sampleimages/tracktest6.jpg"))
    iset.append(Image("./../sampleimages/tracktest7.jpg"))
    iset.append(Image("./../sampleimages/tracktest8.jpg"))
    iset.append(Image("./../sampleimages/tracktest9.jpg"))
    avg = iset.average()
    result = [avg]
    name_stem = "test_image_set_average"
    perform_diff(result,name_stem)



def test_save_to_gif():
    imgs = ImageSet()
    imgs.append(Image('../sampleimages/tracktest0.jpg'))
    imgs.append(Image('../sampleimages/tracktest1.jpg'))
    imgs.append(Image('../sampleimages/tracktest2.jpg'))
    imgs.append(Image('../sampleimages/tracktest3.jpg'))
    imgs.append(Image('../sampleimages/tracktest4.jpg'))
    imgs.append(Image('../sampleimages/tracktest5.jpg'))
    imgs.append(Image('../sampleimages/tracktest6.jpg'))
    imgs.append(Image('../sampleimages/tracktest7.jpg'))
    imgs.append(Image('../sampleimages/tracktest8.jpg'))
    imgs.append(Image('../sampleimages/tracktest9.jpg'))

    filename = "test_save_to_gif.gif"
    saved = imgs.save(filename)

    os.remove(filename)

    assert saved == len(imgs)


def sliceinImageSet():
    imgset = ImageSet("../sampleimages/")
    imgset = imgset[8::-2]
    if isinstance(imgset,ImageSet):
        assert True
    else :
        assert False


def test_upload_dropbox():
    try:
        import dropbox
    except:
        if( SHOW_WARNING_TESTS ):
            logger.warning("Couldn't run the upload test as optional dropbox library required")
        pass
    else:
        img = Image('simplecv')
        api_key = ''
        api_secret = ''
        if api_key==None or api_secret==None :
            pass
        else :
            ret=img.upload('dropbox',api_key,api_secret)
            if ret :
                pass
            else :
                assert False

def test_builtin_rotations():
    img = Image('lenna')
    r1 = img - img.rotate180().rotate180()
    r2 = img - img.rotate90().rotate90().rotate90().rotate90()
    r3 = img - img.rotateLeft().rotateLeft().rotateLeft().rotateLeft()
    r4 = img - img.rotateRight().rotateRight().rotateRight().rotateRight()
    r5 = img - img.rotate270().rotate270().rotate270().rotate270()
    if( r1.meanColor() == Color.BLACK and
        r2.meanColor() == Color.BLACK and
        r3.meanColor() == Color.BLACK and
        r4.meanColor() == Color.BLACK and
        r5.meanColor() == Color.BLACK ):
        pass
    else:
        assert False

def test_histograms():
    img = Image('lenna')
    img.verticalHistogram()
    img.horizontalHistogram()

    img.verticalHistogram(bins=3)
    img.horizontalHistogram(bins=3)

    img.verticalHistogram(threshold=10)
    img.horizontalHistogram(threshold=255)

    img.verticalHistogram(normalize=True)
    img.horizontalHistogram(normalize=True)

    img.verticalHistogram(forPlot=True,normalize=True)
    img.horizontalHistogram(forPlot=True,normalize=True)

    pass

def test_blob_full_masks():
    img = Image('lenna')
    b = img.findBlobs()
    m1 = b[-1].getFullMaskedImage()
    m2 = b[-1].getFullHullMaskedImage()
    m3 = b[-1].getFullMask()
    m4 = b[-1].getFullHullMask()
    if(  m1.width == img.width and
         m2.width == img.width and
         m3.width == img.width and
         m4.width == img.width and
         m1.height == img.height and
         m2.height == img.height and
         m3.height == img.height and
         m4.height == img.height ):
        pass
    else:
        assert False


def test_blob_edge_images():
    img = Image('lenna')
    b = img.findBlobs()
    m1 = b[-1].getEdgeImage()
    m2 = b[-1].getHullEdgeImage()
    m3 = b[-1].getFullEdgeImage()
    m4 = b[-1].getFullHullEdgeImage()
    pass

def test_LineScan():
    def lsstuff(ls):
        def aLine(x,m,b):
            return m*x+b
        ls2 = ls.smooth(degree=4).normalize().scale(value_range=[-1,1]).derivative().resample(100).convolve([.25,0.25,0.25,0.25])
        ls2.minima()
        ls2.maxima()
        ls2.localMinima()
        ls2.localMaxima()
        fft,f = ls2.fft()
        ls3 = ls2.ifft(fft)
        ls4 = ls3.fitToModel(aLine)
        ls4.getModelParameters(aLine)
    img = Image("lenna")
    ls = img.getLineScan(x=128,channel=1)
    lsstuff(ls)
    ls = img.getLineScan(y=128)
    lsstuff(ls)
    ls = img.getLineScan(pt1 = (0,0), pt2=(128,128),channel=2)
    lsstuff(ls)
    pass

def test_uncrop():
    img = Image('lenna')
    croppedImg = img.crop(10,20,250,500)
    sourcePts = croppedImg.uncrop([(2,3),(56,23),(24,87)])
    if sourcePts:
        pass

def test_grid():
    img = Image("simplecv")
    img1 = img.grid((10,10),(0,255,0),1)
    img2 = img.grid((20,20),(255,0,255),1)
    img3 = img.grid((20,20),(255,0,255),2)
    result = [img1,img2,img3]
    name_stem = "test_image_grid"
    perform_diff(result,name_stem,12.0)

def test_removeGrid():
    img = Image("lenna")
    gridImage = img.grid()
    dlayer = gridImage.removeGrid()
    if dlayer is None:
        assert False
    dlayer1 = gridImage.removeGrid()
    if dlayer1 is not None:
        assert False
    pass

def test_cluster():
    img = Image("lenna")
    blobs = img.findBlobs()
    clusters1 = blobs.cluster(method="kmeans",k=5,properties=["color"])
    clusters2 = blobs.cluster(method="hierarchical")
    if clusters1 and clusters2:
        pass

def test_line_parallel():
    img = Image("lenna")
    l1 = Line(img, ((100,200), (300,400)))
    l2 = Line(img, ((200,300), (400,500)))
    if l1.isParallel(l2):
        pass
    else:
        assert False

def test_line_perp():
    img = Image("lenna")
    l1 = Line(img, ((100,200), (100,400)))
    l2 = Line(img, ((200,300), (400,300)))
    if l1.isPerpendicular(l2):
        pass
    else:
        assert False

def test_line_imgIntersection():
    img = Image((512, 512))
    for x in range(200, 400):
        img[x, 200] = (255.0, 255.0, 255.0)
    l = Line(img, ((300, 100),(300, 500)))
    if l.imgIntersections(img) == [(300, 200)]:
        pass
    else:
        assert False

def test_line_cropToEdges():
    img = Image((512, 512))
    l = Line(img, ((-10, -5), (400, 400)))
    l_cr = l.cropToImageEdges()
    if l_cr.end_points == ((0, 5), (400, 400)):
        pass
    else:
        assert False

def test_line_extendToEdges():
    img = Image((512, 512))
    l = Line(img, ((10, 10), (30, 30)))
    l_ext = l.extendToImageEdges()
    if l_ext.end_points == [(0, 0), (511, 511)]:
        pass
    else:
        assert False

def test_findGridLines():
    img = Image("simplecv")
    img = img.grid((10,10),(0,255,255))
    lines = img.findGridLines()
    lines.draw()
    result = [img]
    name_stem = "test_image_gridLines"
    perform_diff(result,name_stem,5)

    if(lines == 0 or lines == None):
        assert False

def test_logicalAND():
    img = Image("lenna")
    img1 = img.logicalAND(img.invert())
    if not img1.getNumpy().all():
        pass
    else:
        assert False

def test_logicalOR():
    img = Image("lenna")
    img1 = img.logicalOR(img.invert())
    if img1.getNumpy().all():
        pass
    else:
        assert False

def test_logicalNAND():
    img = Image("lenna")
    img1 = img.logicalNAND(img.invert())
    if img1.getNumpy().all():
        pass
    else:
        assert False

def test_logicalXOR():
    img = Image("lenna")
    img1 = img.logicalXOR(img.invert())
    if img1.getNumpy().all():
        pass
    else:
        assert False

def test_matchSIFTKeyPoints():
    try:
        import cv2
    except ImportError:
        pass
        return
    if not "2.4.3" in cv2.__version__:
        pass
        return
    img = Image("lenna")
    skp, tkp =  img.matchSIFTKeyPoints(img)
    if len(skp) == len(tkp):
        for i in range(len(skp)):
            if (skp[i].x == tkp[i].x and skp[i].y == tkp[i].y):
                pass
            else:
                assert False
    else:
        assert False

def test_findFeatures():
    img = Image('../sampleimages/mtest.png')
    h_features = img.findFeatures("harris", threshold=500)
    s_features = img.findFeatures("szeliski", threshold=500)
    if h_features and s_features:
        pass
    else:
        assert False

def test_ColorMap():
    img = Image('../sampleimages/mtest.png')
    blobs = img.findBlobs()
    cm = ColorMap((Color.RED,Color.YELLOW,Color.BLUE),min(blobs.area()),max(blobs.area()))
    for b in blobs:
        b.draw(cm[b.area()])
    result = [img]
    name_stem = "test_color_map"
    perform_diff(result,name_stem,1.0)


def test_Steganograpy():
    img = Image(logo)
    msg = 'How do I SimpleCV?'
    img.stegaEncode(msg)
    img.save(logo)
    img2 = Image(logo)
    msg2 = img2.stegaDecode()
    pass

def test_watershed():
    img = Image('../sampleimages/wshed.jpg')
    img1 = img.watershed()
    img2 = img.watershed(dilate=3,erode=2)
    img3 = img.watershed(mask=img.threshold(128),erode=1,dilate=1)
    myMask = Image((img.width,img.height))
    myMask = myMask.floodFill((0,0),color=Color.WATERSHED_BG)
    mask = img.threshold(128)
    myMask = (myMask-mask.dilate(2)+mask.erode(2))
    img4 = img.watershed(mask=myMask,useMyMask=True)
    blobs = img.findBlobsFromWatershed(dilate=3,erode=2)
    blobs = img.findBlobsFromWatershed()
    blobs = img.findBlobsFromWatershed(mask=img.threshold(128),erode=1,dilate=1)
    blobs = img.findBlobsFromWatershed(mask=img.threshold(128),erode=1,dilate=1,invert=True)
    blobs = img.findBlobsFromWatershed(mask=myMask,useMyMask=True)
    result = [img1,img2,img3,img4]
    name_stem = "test_watershed"
    perform_diff(result,name_stem,3.0)

def test_minmax():
    img = Image('../sampleimages/wshed.jpg')
    min = img.minValue()
    min,pts = img.minValue(locations=True)
    max = img.maxValue()
    max,pts = img.maxValue(locations=True)
    pass

def testROIFeature():
    img = Image(testimageclr)
    mask = img.threshold(248).dilate(5)
    blobs = img.findBlobsFromMask(mask,minsize=1)
    x,y = np.where(mask.getGrayNumpy()>0)
    xmin = np.min(x)
    xmax = np.max(x)
    ymin = np.min(y)
    ymax = np.max(y)
    w = xmax-xmin
    h = ymax-ymin
    roiList = []

    def subtest(data,effect):
        broke = False
        first = effect(data[0])
        i = 0
        for d in data:
            e = effect(d)
            print (i,e)
            i = i + 1
            if( first != e ):
                broke = True
        return broke

    broi = ROI(blobs)
    broi2 = ROI(blobs,image=img)

    roiList.append(ROI(x=x,y=y,image=img))
    roiList.append(ROI(x=list(x),y=list(y),image=img))
    roiList.append(ROI(x=tuple(x),y=tuple(y),image=img))
    roiList.append(ROI(zip(x,y),image=img))
    roiList.append(ROI((xmin,ymin),(xmax,ymax),image=img))
    roiList.append(ROI(xmin,ymin,w,h,image=img))
    roiList.append(ROI([(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax)],image=img))
    roiList.append(ROI(roiList[0]))

    # test the basics
    def toXYWH( roi ):
        return roi.toXYWH()

    if( subtest(roiList,toXYWH) ):
        assert False
    broi.translate(10,10)
    broi.translate(-10)
    broi.translate(y=-10)
    broi.toTLAndBR()
    broi.toPoints()
    broi.toUnitXYWH()
    broi.toUnitTLAndBR()
    broi.toUnitPoints()
    roiList[0].crop()
    newROI=ROI(zip(x,y),image=mask)
    test = newROI.crop()
    xroi,yroi = np.where(test.getGrayNumpy()>128)
    roiPts = zip(xroi,yroi)
    realPts = newROI.CoordTransformPts(roiPts)
    unitROI = newROI.CoordTransformPts(roiPts,output="ROI_UNIT")
    unitSRC = newROI.CoordTransformPts(roiPts,output="SRC_UNIT")
    src1 = newROI.CoordTransformPts(roiPts,intype="SRC_UNIT",output='SRC')
    src2 = newROI.CoordTransformPts(roiPts,intype="ROI_UNIT",output='SRC')
    src3 = newROI.CoordTransformPts(roiPts,intype="SRC_UNIT",output='ROI')
    src4 = newROI.CoordTransformPts(roiPts,intype="ROI_UNIT",output='ROI')
    fs = newROI.splitX(10)
    fs = newROI.splitX(.5,unitVals=True)
    for f in fs:
        f.draw(color=Color.BLUE)
    fs = newROI.splitX(newROI.xtl+10,srcVals=True)
    xs = newROI.xtl
    fs = newROI.splitX([10,20])
    fs = newROI.splitX([xs+10,xs+20,xs+30],srcVals=True)
    fs = newROI.splitX([0.3,0.6,0.9],unitVals=True)
    fs = newROI.splitY(10)
    fs = newROI.splitY(.5,unitVals=True)
    for f in fs:
        f.draw(color=Color.BLUE)
    fs = newROI.splitY(newROI.ytl+30,srcVals=True)
    testROI = ROI(blobs[0],mask)
    for b in blobs[1:]:
        testROI.merge(b)

def test_findKeypointClusters():
    img = Image('simplecv')
    kpc = img.findKeypointClusters()
    if len(kpc) <= 0:
      assert False
    else:
      pass

def test_replaceLineScan():
    img = Image("lenna")
    ls = img.getLineScan(x=100)
    ls[50] = 0
    newimg = img.replaceLineScan(ls)
    if newimg[100, 50][0] == 0:
        pass
    else:
        assert False
    ls = img.getLineScan(x=100,channel=1)
    ls[50] = 0
    newImg = img.replaceLineScan(ls)
    if newImg[100,50][1] == 0:
        pass
    else:
        assert False

def test_runningAverage():
    img = Image('lenna')
    ls = img.getLineScan(y=120)
    ra=ls.runningAverage(5)
    if ra[50] == sum(ls[48:53])/5:
        pass
    else:
        assert False

def lineScan_perform_diff(oLineScan, pLineScan, func, **kwargs):
    nLineScan = func(oLineScan, **kwargs)
    diff = sum([(i - j) for i, j in zip(pLineScan, nLineScan)])
    if diff > 10 or diff < -10:
        return False
    return True

def test_linescan_smooth():
    img = Image("lenna")
    l1 = img.getLineScan(x=60)
    l2 = l1.smooth(degree=7)
    if lineScan_perform_diff(l1, l2, LineScan.smooth, degree=7):
        pass
    else:
        assert False

def test_linescan_normalize():
    img = Image("lenna")
    l1 = img.getLineScan(x=90)
    l2 = l1.normalize()
    if lineScan_perform_diff(l1, l2, LineScan.normalize):
        pass
    else:
        assert False

def test_linescan_scale():
    img = Image("lenna")
    l1 = img.getLineScan(y=90)
    l2 = l1.scale()
    if lineScan_perform_diff(l1, l2, LineScan.scale):
        pass
    else:
        assert False

def test_linescan_derivative():
    img = Image("lenna")
    l1 = img.getLineScan(y=140)
    l2 = l1.derivative()
    if lineScan_perform_diff(l1, l2, LineScan.derivative):
        pass
    else:
        assert False

def test_linescan_resample():
    img = Image("lenna")
    l1 = img.getLineScan(pt1=(300, 300), pt2=(450, 500))
    l2 = l1.resample(n=50)
    if lineScan_perform_diff(l1, l2, LineScan.resample, n=50):
        pass
    else:
        assert False

def test_linescan_fitToModel():
    def aLine(x, m, b):
        return x*m+b
    img = Image("lenna")
    l1 = img.getLineScan(y=200)
    l2 = l1.fitToModel(aLine)
    if lineScan_perform_diff(l1, l2, LineScan.fitToModel, f=aLine):
        pass
    else:
        assert False

def test_linescan_convolve():
    kernel = [0, 2, 0, 4, 0, 2, 0]
    img = Image("lenna")
    l1 = img.getLineScan(x=400)
    l2 = l1.convolve(kernel)
    if lineScan_perform_diff(l1, l2, LineScan.convolve, kernel=kernel):
        pass
    else:
        assert False

def test_linescan_threshold():
    img = Image("lenna")
    l1 = img.getLineScan(x=350)
    l2 = l1.threshold(threshold=200, invert=True)
    if lineScan_perform_diff(l1, l2, LineScan.threshold, threshold=200, invert=True):
        pass
    else:
        assert False

def test_linescan_invert():
    img = Image("lenna")
    l1 = img.getLineScan(y=200)
    l2 = l1.invert(max=40)
    if lineScan_perform_diff(l1, l2, LineScan.invert, max=40):
        pass
    else:
        assert False

def test_linescan_median():
    img = Image("lenna")
    l1 = img.getLineScan(x=120)
    l2 = l1.median(sz=9)
    if lineScan_perform_diff(l1, l2, LineScan.median, sz=9):
        pass
    else:
        assert False

def test_linescan_medianFilter():
    img = Image("lenna")
    l1 = img.getLineScan(y=250)
    l2 = l1.medianFilter(kernel_size=7)
    if lineScan_perform_diff(l1, l2, LineScan.medianFilter, kernel_size=7):
        pass
    else:
        assert False

def test_linescan_detrend():
    img = Image("lenna")
    l1 = img.getLineScan(y=90)
    l2 = l1.detrend()
    if lineScan_perform_diff(l1, l2, LineScan.detrend):
        pass
    else:
        assert False

def test_getFREAKDescriptor():
    try:
        import cv2
    except ImportError:
        pass
    if '$Rev' in cv2.__version__:
        pass
    else:
        if int(cv2.__version__.replace('.','0'))>=20402:
            img = Image("lenna")
            flavors = ["SIFT", "SURF", "BRISK", "ORB", "STAR", "MSER", "FAST", "Dense"]
            for flavor in flavors:
                f, d = img.getFREAKDescriptor(flavor)
                if len(f) == 0:
                    assert False
                if d.shape[0] != len(f) and d.shape[1] != 64:
                    assert False
        else:
            pass
    pass

def test_grayPeaks():
    i = Image('lenna')
    peaks = i.grayPeaks()
    if peaks == None:
        assert False
    else:
        pass

def test_findPeaks():
    img = Image('lenna')
    ls = img.getLineScan(x=150)
    peaks = ls.findPeaks()
    if peaks == None:
        assert False
    else:
        pass

def test_LineScan_sub():
    img = Image('lenna')
    ls = img.getLineScan(x=200)
    ls1 = ls - ls
    if ls1[23] == 0:
        pass
    else:
        assert False

def test_LineScan_add():
    img = Image('lenna')
    ls = img.getLineScan(x=20)
    l = ls + ls
    a = int(ls[20]) + int(ls[20])
    if a == l[20]:
        pass
    else:
        assert False

def test_LineScan_mul():
    img = Image('lenna')
    ls = img.getLineScan(x=20)
    l = ls * ls
    a = int(ls[20]) * int(ls[20])
    if a == l[20]:
        pass
    else:
        assert False

def test_LineScan_div():
    img = Image('lenna')
    ls = img.getLineScan(x=20)
    l = ls / ls
    a = int(ls[20]) / int(ls[20])
    if a == l[20]:
        pass
    else:
        assert False

def test_tvDenoising():
    return # this is way too slow.
    try:
        from skimage.filter import denoise_tv_chambolle
        img = Image('lenna')
        img1 = img.tvDenoising(gray=False,weight=20)
        img2 = img.tvDenoising(weight=50,max_iter=250)
        img3 = img.toGray()
        img3 = img3.tvDenoising(gray=True,weight=20)
        img4 = img.tvDenoising(resize=0.5)
        result = [img1,img2,img3,img4]
        name_stem = "test_tvDenoising"
        perform_diff(result,name_stem,3)
    except ImportError:
        pass

def test_motionBlur():
    i = Image('lenna')
    d = ('n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw')
    i0 = i.motionBlur(intensity = 20, direction = d[0])
    i1 = i.motionBlur(intensity = 20, direction = d[1])
    i2 = i.motionBlur(intensity = 20, direction = d[2])
    i3 = i.motionBlur(intensity = 20, direction = d[3])
    i4 = i.motionBlur(intensity = 10, direction = d[4])
    i5 = i.motionBlur(intensity = 10, direction = d[5])
    i6 = i.motionBlur(intensity = 10, direction = d[6])
    i7 = i.motionBlur(intensity = 10, direction = d[7])
    a = i.motionBlur(intensity = 0)
    c = 0
    img = (i0, i1, i2, i3, i4, i5, i6, i7)
    for im in img:
        if im is not i:
            c += 1

    if c == 8 and a is i:
        pass
    else:
        assert False

def test_faceRecognize():
    try:
        import cv2
        if hasattr(cv2, "createFisherFaceRecognizer"):
            f = FaceRecognizer()
            images1 = ["../sampleimages/ff1.jpg",
                       "../sampleimages/ff2.jpg",
                       "../sampleimages/ff3.jpg",
                       "../sampleimages/ff4.jpg",
                        "../sampleimages/ff5.jpg"]

            images2 = ["../sampleimages/fm1.jpg",
                       "../sampleimages/fm2.jpg",
                       "../sampleimages/fm3.jpg",
                       "../sampleimages/fm4.jpg",
                       "../sampleimages/fm5.jpg"]

            images3 = ["../sampleimages/fi1.jpg",
                       "../sampleimages/fi2.jpg",
                       "../sampleimages/fi3.jpg",
                       "../sampleimages/fi4.jpg"]

            imgset1 = []
            imgset2 = []
            imgset3 = []

            for img in images1:
                imgset1.append(Image(img))
            label1 = ["female"]*len(imgset1)

            for img in images2:
                imgset2.append(Image(img))
            label2 = ["male"]*len(imgset2)

            imgset = imgset1 + imgset2
            labels = label1 + label2
            imgset[4] = imgset[4].resize(400,400)
            f.train(imgset, labels)

            for img in images3:
                imgset3.append(Image(img))
            imgset[2].resize(300, 300)
            label = []
            for img in imgset3:
                name, confidence = f.predict(img)
                label.append(name)

            if label == ["male", "male", "female", "female"]:
                pass
            else:
                assert False
        else:
            pass
    except ImportError:
        pass

def test_channelMixer():
    i = Image('lenna')
    r = i.channelMixer()
    g = i.channelMixer(channel='g', weight = (100,20,30))
    b = i.channelMixer(channel='b', weight = (30,200,10))
    if i != r and i != g and i != b:
        pass
    else:
        assert False

def test_prewitt():
    i = Image('lenna')
    p = i.prewitt()
    if i != p :
        pass
    else:
        assert False

def test_edgeSnap():
    img = Image('shapes.png',sample=True).edges()

    list1 = [(129,32),(19,88),(124,135)]
    list2 = [(484,294),(297,437)]
    list3 = [(158,357),(339,82)]

    for list_ in list1,list2,list3:
        edgeLines = img.edgeSnap(list_)
        edgeLines.draw(color = Color.YELLOW,width = 4)

    name_stem = "test_edgeSnap"
    result = [img]
    perform_diff(result,name_stem,0.7)

def test_motionBlur():
    image = Image('lenna')
    d = (-70, -45, -30, -10, 100, 150, 235, 420)
    p = ( 10,20,30,40,50,60,70,80)
    img = []

    a = image.motionBlur(0)
    for i in range(8):
        img += [image.motionBlur(p[i],d[i])]
    c = 0
    for im in img:
        if im is not i:
            c += 1

    if c == 8 and a is image:
        pass
    else:
        assert False

def test_grayscalmatrix():
    img = Image("lenna")
    graymat = img.getGrayscaleMatrix()
    newimg = Image(graymat, colorSpace=ColorSpace.GRAY)
    from numpy import array_equal
    if not array_equal(img.getGrayNumpy(), newimg.getGrayNumpy()):
        assert False
    pass

def test_getLightness():
    img = Image('lenna')
    i = img.getLightness()
    if int(i[27,42][0]) == int((max(img[27,42])+min(img[27,42]))/2):
        pass
    else:
        assert False

def test_getLuminosity():
    img = Image('lenna')
    i = img.getLuminosity()
    a = np.array(img[27,42],dtype=np.int)
    if int(i[27,42][0]) == int(np.average(a,0,(0.21,0.71,0.07))):
        pass
    else:
        assert False

def test_getAverage():
    img = Image('lenna')
    i = img.getAverage()
    if int(i[0,0][0]) == int((img[0,0][0]+img[0,0][1]+img[0,0][2])/3):
        pass
    else:
        assert False

def test_smartRotate():
    import time
    img = Image('kptest2.png',sample = True)

    st1 = img.smartRotate(auto = False,fixed = False).resize(500,500)
    st2 = img.rotate(27,fixed = False).resize(500,500)
    diff = np.average((st1-st2).getNumpy())
    if (diff > 1.7):
        print diff
        assert False
    else:
        assert True

def test_normalize():
    img = Image("lenna")
    img1 = img.normalize()
    img2 = img.normalize(minCut = 0,maxCut = 0)
    result = [img1,img2]
    name_stem = "test_image_normalize"
    perform_diff(result,name_stem,5)
    pass

def test_getNormalizedHueHistogram():
    img = Image('lenna')
    a = img.getNormalizedHueHistogram((0,0,100,100))
    b = img.getNormalizedHueHistogram()
    blobs = img.findBlobs()
    c = img.getNormalizedHueHistogram(blobs[-1])
    if( a.shape == (180,256) and b.shape == (180,256)
        and c.shape == (180,256) ):
        pass
    else:
        assert False

def test_backProjecHueHistogram():
    img = Image('lenna')
    img2 = Image('lyle')
    a = img2.getNormalizedHueHistogram()
    imgA = img.backProjectHueHistogram(a)
    imgB = img.backProjectHueHistogram((10,10,50,50),smooth=False,fullColor=True)
    imgC = img.backProjectHueHistogram(img2,threshold=1)
    result = [imgA,imgB,imgC]
    name_stem = "test_image_histBackProj"
    perform_diff(result,name_stem,5)

def test_findBlobsFromHueHistogram():
    img = Image('lenna')
    img2 = Image('lyle')
    a = img2.getNormalizedHueHistogram()
    A = img.findBlobsFromHueHistogram(a)
    B = img.findBlobsFromHueHistogram((10,10,50,50),smooth=False)
    C = img.findBlobsFromHueHistogram(img2,threshold=1)
    pass

def test_drawingLayerToSVG():
    img = Image('lenna')
    dl = img.dl()
    dl.line((0, 0), (100, 100))
    svg = dl.getSVG()
    if svg == '<svg baseProfile="full" height="512" version="1.1" width="512" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink"><defs /><line x1="0" x2="100" y1="0" y2="100" /></svg>':
        pass
    else:
        assert False
