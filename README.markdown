SimpleCV
================================================================================

_a kinder, gentler machine vision python library_

SimpleCV's goal is to provide a convenient, readable wrapper for OpenCV which will allow programmers who are linear-algebra illiterate to access the power of its functionality.  Whereas OpenCV's goals are power and performance, SimpleCV seeks to provide an easy to use programming interface for casual machine vision users.  Note that this is not a new(er) CTypes-style interface to OpenCV's native C/C++ libraries, but a pure-python wrapper on OpenCV's native SWIG python interfaces -- it is not designed to replace OpenCV's python libraries, just make them easy to use.

SimpleCV is developed against [Ubuntu 10.10](http://ubuntu.com), and uses the python infrastructure provided in this distribution: Python 2.6.6.  It uses the latest stable release of OpenCV, in this case 2.2.

##Installation

    sudo apt-get install python-numpy python-nose
    wget http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.2/OpenCV-2.2.0.tar.bz2
    bunzip OpenCV-2.2.0.tar.bz2
    tar xf OpenCV-2.2.0.tar
    cd OpenCV-2.2.0
    mkdir build
    cd build
    cmake -D CMAKE_BUILD_TYPE=RELEASE -D BUILD_PYTHON_SUPPORT=ON
    make
    sudo make install
    git clone git://git.code.sf.net/p/simplecv/git.git simplecv 

##Usage

The central class in SimpleCV is the Image() class, which wrappers OpenCV's iplImage (bitmap) and cvMat (matrix) classes and provides basic manipulation functions.

To load an image, specify the file path in the constructor:

    my_image = Image("path/to/image.jpg")

To save the image, use the save method.  It will automatically use the file you loaded the image from:

    my_image.save()

You can also specify a new file to save to, similar to a "Save As...", and future calls to save() will save to this new file:

     my_image.save("path/to/new_image.jpg")
     #...do some stuff...
     my_image.save() #saves to path/to/new_image.jpg

You can scale images using the "scale" function, so for instance to create a thumbnail.  Note that this will distort perspective if you change the width and height ratios:

    thumbnail = my_image.scale(90, 90)

You can also look at individual pixels:

    r, g, b = my_image[25, 45]  #get the color trio for pixel at x = 25, y = 45

If you use python slices, you can extract a portion of the image.  This section is returned as an Image object:

    my_section = myimage[25:50, 45:70]    #grab a 25x25 rectangle starting at x = 25, y = 45
    my_section.save("path/to/new_cropped_image.jpg")

You can also assign using direct pixel addressing, and draw on the image using this method:

    black = 0.0, 0.0, 0.0    #create a black color tuple
    my_image[25,45] = black  #set the pixel at x = 25, y = 45 to black
    my_image[25:50, 45] = black #draw 1px wide line
    my_image[25:50, 45:70] = black #create a 25x25 black rectange starting at x = 25, y = 45 

Addressing your [OpenCV supported webcam](http://opencv.willowgarage.com/wiki/Welcome/OS) is extremely easy:

    mycam = Camera()
    img = Camera.getImage()

And you can even use multiple cameras, at different resolutions:

    mylaptopcam = Camera(0, {"width": 640, "height": 480})  #you can also control brightness, hue, gain, etc 
    myusbcam = Camera(1, {"width": 1280, "height": 720})

    mylaptopcam.getImage().save("okaypicture.jpg")
    myusbcam.getImage().save("nicepicture.jpg")

You can also initialize VirtualCameras from static data files:

    imgcam = VirtualCamera("apples.jpg", "image")
    vidcam = VirtualCamera("bananas.mpg", "video")

    imgcam.getImage.save("copy_of_apples.jpg")
    imgcam.getImage.save("frame_1_of_bananas.jpg")


You can also split channels, if you are interested in only processing a single color:

    (red, green, blue) = Camera().getImage().channels()
    red.save("redcam.jpg")
    green.save("greencam.jpg")
    blue.save("bluecam.jpg")

The Image class has a builtin [Histogram](http://en.wikipedia.org/wiki/Image_histogram) function, thanks to [Numpy](http://numpy.scipy.org/).  Histograms can show you the distribution of brightness or color in an image:

    hist = Camera().getImage().histogram(20)
    brightpixels = 0
    darkpixels = 0
    i = 0

    while i < length(hist):
      if (i < 10):
        darkpixels = darkpixels + hist[i]
      else:
        brightpixels = brightpixels + hist[i]
      i = i + 1

    if (brightpixels > darkpixels):
      print "your room is bright"
    else:
      print "your room is dark"


##To do

- wrapper remaining openCV calls 
-- feature detection
--- GoodFeaturesToTrack (break out into harris vs eig corners?)
- handle buffer pages intelligently (and thread-safe)
- Django or Turbogears backend
- integrated (Mongo? Reddis?) data persistance
- images automatically converted to full depth OR carry around depth as metadata
- default parameters for most functions
- named parameters available for most functions
- extensions brought in
