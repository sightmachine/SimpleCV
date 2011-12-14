SimpleCV Cookbook
===========================


Loading and Saving Images
----------------------------

The central class in SimpleCV is the Image() class, which wrappers OpenCV's iplImage (bitmap) and cvMat (matrix) classes and provides basic manipulation functions.

To load an image, specify the file path in the constructor::

    my_image = Image("path/to/image.jpg")

To save the image, use the save method.  It will automatically use the file you loaded the image from::

    my_image.save()

You can also specify a new file to save to, similar to a "Save As...", and future calls to save() will save to this new file::

     my_image.save("path/to/new_image.jpg")
     #...do some stuff...
     my_image.save() #saves to path/to/new_image.jpg


Image Manipulation
-----------------------

You can scale images using the "scale" function, so for instance to create a thumbnail.  Note that this will distort perspective if you change the width and height ratios::

    thumbnail = my_image.scale(90, 90)

You can also look at individual pixels::

    r, g, b = my_image[25, 45]  #get the color trio for pixel at x = 25, y = 45

If you use python slices, you can extract a portion of the image.  This section is returned as an Image object::

    my_section = myimage[25:50, 45:70]    #grab a 25x25 rectangle starting at x = 25, y = 45
    my_section.save("path/to/new_cropped_image.jpg")

You can also assign using direct pixel addressing, and draw on the image using this method::

    black = 0.0, 0.0, 0.0    #create a black color tuple
    my_image[25,45] = black  #set the pixel at x = 25, y = 45 to black
    my_image[25:50, 45] = black #draw 1px wide line
    my_image[25:50, 45:70] = black #create a 25x25 black rectange starting at x = 25, y = 45 

Using a Camera, Kinect, or VirtualCamera
--------------------------------------------

Addressing your `OpenCV supported webcam <http://opencv.willowgarage.com/wiki/Welcome/OS>`_ is extremely easy::

    mycam = Camera()
    img = mycam.getImage()

If you install the `OpenKinect <http://openkinect.org/wiki/Getting_Started>`_ library and python wrapper, you can use your Xbox Kinect to get a depth map::

    k = Kinect()
    img = k.getImage() #normal, full color webcam
    depth = k.getDepth() #greyscale depth map
    depthdata = k.getDepthMatrix() #raw depth map, 0-2048

Multiple Cameras
----------------
And you can even use multiple cameras, at different resolutions::

    mylaptopcam = Camera(0, {"width": 640, "height": 480})  #you can also control brightness, hue, gain, etc 
    myusbcam = Camera(1, {"width": 1280, "height": 720})

    mylaptopcam.getImage().save("okaypicture.jpg")
    myusbcam.getImage().save("nicepicture.jpg")

You can also initialize VirtualCameras from static data files::

    imgcam = VirtualCamera("apples.jpg", "image")
    vidcam = VirtualCamera("bananas.mpg", "video")

    imgcam.getImage().save("copy_of_apples.jpg")
    imgcam.getImage().save("frame_1_of_bananas.jpg")

You can also use a JpegStreamCamera to grab frames from an MJPG source (such as an IP Cam, the "IP Webcam" android application, or another SimpleCV JpegStream::   

    jc = JpegStreamCamera("http://myname:mypasswd@ipcamera_host/stream.mjpg")
    jc.getImage().save("seeyou.jpg")


Colors and Levels 
-----------------

You can also split channels, if you are interested in only processing a single color::

    (red, green, blue) = Camera().getImage().channels()
    red.save("redcam.jpg")
    green.save("greencam.jpg")
    blue.save("bluecam.jpg")

The Image class has a builtin `Histogram <http://en.wikipedia.org/wiki/Image_histogram>`_ function, thanks to `Numpy <http://numpy.scipy.org/>`_.  Histograms can show you the distribution of brightness or color in an image::

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

      
Features and FeatureSets
-----------------------------

SimpleCV has advanced feature-detection functions, which can let you find
different types of features.  These are returned in FeatureSets which can
be addressed as a group, or filtered::

    img = Camera.getImage()

    lines = img.findLines()

    corners = img.findCorners()

    lines.draw(Color.RED) #outline the line segments in red
    corners.draw(Color.BLUE) #outline corners detected in blue

    left_side_corners = corners.filter(corners.x() < img.width / 2)
    #only look at corners on the left half of the image

    longest_line = lines.sortLength()[0]
    #get the longest line returned


Blob Detection
-------------------

You can use SimpleCV to find connected components (blobs) of similarly-colored pixels:: 

    #find the green ball
    green_stuff = Camera().getImage().colorDistance(Color.GREEN)

    green_blobs = green_channel.findBlobs()
    #blobs are returned in order of area, smallest first

    print "largest green blob at " + str(green_blobs[-1].x) + ", " + str( green_blobs[-1].y)


Barcode Reading
-------------------

If you load the `python-zxing <https://github.com/oostendo/python-zxing>`_ library, you can use `Zebra Crossing <http://code.google.com/p/zxing>`_ to detect 2D and 1D barcodes in a number of various formats.  Note that you will need to specify
the location of the library either through the ZXING_LIBRARY %ENV variable, or
as a parameter to findBarcode()::

    i = Camera().getImage()
    barcode = i.findBarcode("/var/opt/zxing")

    barcode.draw(Color.GREEN) #draw the outline of the barcode in green

    i.save("barcode_found.png")
    print barcode.data

Haar Face Detection
---------------------

You can do Haar Cascade face detection with SimpleCV, but you will need to find your own `Haar Cascade File <http://www.google.com/search?q=haarcascade_frontalface_alt.xml>`_::

    i = Camera().getImage()
    faces = i.findHaarFeatures("/path/to/haarcascade_frontalface_alt.xml")
    
    #print locations 
    for f in faces:
      print "I found a face at " + str(f.coordinates())
    
    #outline who was drinking last night (or at least has the greenest pallor)
    faces.sortColorDistance(Color.GREEN)[0].draw(Color.GREEN)
    i.save("greenest_face_detected.png")


Output Streams
-----------------

SimpleCV uses PyGame as an interface to the Simple Directmedia Layer (SDL).
This makes it easy to create interfaces using SimpleCV's Display module::

    from SimpleCV.Display import Display
    
    c = Camera()
    d = Display()
    while not d.isDone():
        c.getImage().save(d)


SimpleCV has an integrated HTTP-based JPEG streamer.  It will use the old-school
multipart/replace content type to continuously feed jpgs to your browser.  
To send the data, you just save the image to the js.framebuffer location::

    import time
    c = Camera()
    js = JpegStreamer()  #starts up an http server (defaults to port 8080)

    while(1)
      c.getImage().save(js)
      time.sleep(0.1)
      

You can also write frames directly to video, using OpenCV's VideoWriter.  Note 
that your available formats may be dependent on your platform::

    import time
    c = Camera
    vs = VideoStream("out.avi", fps=15)

    framecount = 0
    while(framecount < 15 * 600): #record for 5 minutes @ 15fps
        c.getImage().save(vs)
        time.sleep(0.1)



