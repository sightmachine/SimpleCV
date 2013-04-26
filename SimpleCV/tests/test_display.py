# /usr/bin/python
# To run this test you need python nose tools installed
# Run test just use:
#   nosetest test_display.py
#

import os, sys, pickle
from SimpleCV import *
from nose.tools import with_setup, nottest

VISUAL_TEST = True  # if TRUE we save the images - otherwise we DIFF against them - the default is False
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

#track images
trackimgs = ["../sampleimages/tracktest0.jpg",
        "../sampleimages/tracktest1.jpg",
        "../sampleimages/tracktest2.jpg",
        "../sampleimages/tracktest3.jpg",
        "../sampleimages/tracktest4.jpg",
        "../sampleimages/tracktest5.jpg",
        "../sampleimages/tracktest6.jpg",
        "../sampleimages/tracktest7.jpg",
        "../sampleimages/tracktest8.jpg",
        "../sampleimages/tracktest9.jpg",]

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
def perform_diff(result,name_stem,tolerance=2.0,path=standard_path):
    if(VISUAL_TEST): # save the correct images for a visual test
        imgSaves(result,name_stem,path)
    else: # otherwise we test our output against the visual test
        if( imgDiffs(result,name_stem,tolerance,path) ):
            assert False
        else:
            pass

#These function names are required by nose test, please leave them as is
def setup_context():
    img = Image(testimage)

def destroy_context():
    img = ""

@with_setup(setup_context, destroy_context)
def test_image_stretch():
    img = Image(greyscaleimage)
    stretched = img.stretch(100,200)
    if(stretched == None):
        assert False

    result = [stretched]
    name_stem = "test_stretch"
    perform_diff(result,name_stem)

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


def test_image_splitchannels():
    img = Image(testimageclr)
    (r, g, b) = img.splitChannels(True)
    (red, green, blue) = img.splitChannels()
    result = [r,g,b,red,green,blue]
    name_stem = "test_image_splitchannels"
    perform_diff(result,name_stem)
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
    c=test.meanColor()

    results = [ptrans,ptrans2]
    name_stem = "test_image_perspective"
    perform_diff(results,name_stem)
    if( c[0] > 1 or c[1] > 1 or c[2] > 1 ):
        assert False

def test_camera_undistort():
    
    fakeCamera = FrameSource()
    fakeCamera.loadCalibration("TestCalibration")
    img = Image("../sampleimages/CalibImage0.png")
    img2 = fakeCamera.undistort(img)

    results = [img2]
    name_stem = "test_camera_undistort"
    perform_diff(results,name_stem)

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

    kp.draw()
    results = [img]
    name_stem = "test_findKeypoints"
    perform_diff(results,name_stem)

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
    perform_diff(results,name_stem,tolerance=4.0)

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

    kp1 = img1.findKeypoints()
    kp2 = img2.findKeypoints(highQuality=True)
    kp3 = img3.findKeypoints(flavor="STAR")
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
    perform_diff(results,name_stem,tolerance=3.0)


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
        #f.meanColor()
        f.crop()
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

def test_skeletonize():
    img = Image(logo)
    s = img.skeletonize()
    s2 = img.skeletonize(10)

    results = [s,s2]
    name_stem = "test_skelotinze"
    perform_diff(results,name_stem)

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


def test_getDFTLogMagnitude():
    img = Image("../sampleimages/RedDog2.jpg")
    lm3 = img.getDFTLogMagnitude()
    lm1 = img.getDFTLogMagnitude(grayscale=True)

    results = [lm3,lm1]
    name_stem = "test_getDFTLogMagnitude"
    perform_diff(results,name_stem)

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

def test_findHaarFeatures():
    img = Image("../sampleimages/orson_welles.jpg")
    face = HaarCascade("face.xml")
    f = img.findHaarFeatures(face)
    f2 = img.findHaarFeatures("face.xml")
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
    perform_diff(results,name_stem,tolerance=7.0)

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
    perform_diff(results,name_stem,tolerance=9.0)

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

def test_sobel():
    img = Image("lenna")
    s = img.sobel()
    name_stem = "test_sobel"
    s = [s]
    perform_diff(s,name_stem)

def test_image_new_smooth():
    img = Image(testimage2)
    result = []
    result.append(img.medianFilter())
    result.append(img.medianFilter((3,3)))
    result.append(img.medianFilter((5,5),grayscale=True))
    result.append(img.bilateralFilter())
    result.append(img.bilateralFilter(diameter=14,sigmaColor=20, sigmaSpace=34))
    result.append(img.bilateralFilter(grayscale=True))
    result.append(img.blur())
    result.append(img.blur((5,5)))
    result.append(img.blur((3,5),grayscale=True))
    result.append(img.gaussianBlur())
    result.append(img.gaussianBlur((3,7), sigmaX=10 , sigmaY=12))
    result.append(img.gaussianBlur((7,9), sigmaX=10 , sigmaY=12, grayscale=True))
    name_stem = "test_image_new_smooth"
    perform_diff(result,name_stem)
    pass

def test_camshift():
    ts = []
    bb = (195, 160, 49, 46)
    imgs = [Image(img) for img in trackimgs]
    ts = imgs[0].track("camshift", ts, imgs[1:], bb)
    if ts:
        pass
    else:
        assert False

def test_lk():
    ts = []
    bb = (195, 160, 49, 46)
    imgs = [Image(img) for img in trackimgs]
    ts = imgs[0].track("LK", ts, imgs[1:], bb)
    if ts:
        pass
    else:
        assert False
