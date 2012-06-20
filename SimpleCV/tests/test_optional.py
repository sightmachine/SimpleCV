# /usr/bin/python
# To run this test you need python nose tools installed
# Run test just use:
#   nosetest test_optional.py
#

import os, sys, pickle
from SimpleCV import * 
from nose.tools import with_setup, nottest

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

#These function names are required by nose test, please leave them as is
def setup_context():
  img = Image(testimage)
  
def destroy_context():
  img = ""

@with_setup(setup_context, destroy_context)
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
    
def test_detection_ocr():
    img = Image(ocrimage)
    
    foundtext = img.readText()
    print foundtext
    if(len(foundtext) <= 1):
        assert False
    else:
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
