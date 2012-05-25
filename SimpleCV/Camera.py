# SimpleCV Cameras & Devices

#load system libraries
from SimpleCV.base import *
from SimpleCV.ImageClass import Image, ImageSet
from SimpleCV.Display import Display
from SimpleCV.Color import Color
import platform

#Globals
_cameras = [] 
_camera_polling_thread = ""
 

class FrameBufferThread(threading.Thread):
    """
    **SUMMARY**

    This is a helper thread which continually debuffers the camera frames.  If
    you don't do this, cameras may constantly give you a frame behind, which
    causes problems at low sample rates.  This makes sure the frames returned
    by your camera are fresh.
    """
    def run(self):
        global _cameras
        while (1):
            for cam in _cameras:
                if cam.pygame_camera:
                    cam.pygame_buffer = cam.capture.get_image(cam.pygame_buffer)
                else:
                    cv.GrabFrame(cam.capture)
                cam._threadcapturetime = time.time()
            time.sleep(0.04)    #max 25 fps, if you're lucky



class FrameSource:
    """
    **SUMMARY**

    An abstract Camera-type class, for handling multiple types of video input.
    Any sources of images inheirit from it

    """
    _calibMat = "" #Intrinsic calibration matrix 
    _distCoeff = "" #Distortion matrix
    _threadcapturetime = '' #when the last picture was taken
    capturetime = '' #timestamp of the last aquired image
    
    def __init__(self):
        return
    
    def getProperty(self, p):
        return None
  
    def getAllProperties(self):
        return {}
  
    def getImage(self):
        return None

    def calibrate(self, imageList, grid_sz=0.03, dimensions=(8, 5)):
        """
        **SUMMARY**

        Camera calibration will help remove distortion and fisheye effects
        It is agnostic of the imagery source, and can be used with any camera

        The easiest way to run calibration is to run the
        calibrate.py file under the tools directory for SimpleCV.
        This will walk you through the calibration process.
    
        **PARAMETERS**

        * *imageList* - is a list of images of color calibration images. 
    
        * *grid_sz* - is the actual grid size of the calibration grid, the unit used will be 
          the calibration unit value (i.e. if in doubt use meters, or U.S. standard)
    
        * *dimensions* - is the the count of the *interior* corners in the calibration grid.
          So for a grid where there are 4x4 black grid squares has seven interior corners.
          
        **RETURNS**

        The camera's intrinsic matrix.

        **EXAMPLE**
        
        See :py:module:calibrate.py

        """
        # This routine was adapted from code originally written by:
        # Abid. K  -- abidrahman2@gmail.com
        # See: https://github.com/abidrahmank/OpenCV-Python/blob/master/Other_Examples/camera_calibration.py
    
        warn_thresh = 1
        n_boards = 0	#no of boards
        board_w = int(dimensions[0])	# number of horizontal corners
        board_h = int(dimensions[1])	# number of vertical corners
        n_boards = int(len(imageList))
        board_n = board_w * board_h		# no of total corners
        board_sz = (board_w, board_h)	#size of board
        if( n_boards < warn_thresh ):
            logger.warning("FrameSource.calibrate: We suggest using 20 or more images to perform camera calibration!" ) 
    
        #  creation of memory storages
        image_points = cv.CreateMat(n_boards * board_n, 2, cv.CV_32FC1)
        object_points = cv.CreateMat(n_boards * board_n, 3, cv.CV_32FC1)
        point_counts = cv.CreateMat(n_boards, 1, cv.CV_32SC1)
        intrinsic_matrix = cv.CreateMat(3, 3, cv.CV_32FC1)
        distortion_coefficient = cv.CreateMat(5, 1, cv.CV_32FC1)
    
        #	capture frames of specified properties and modification of matrix values
        i = 0
        z = 0		# to print number of frames
        successes = 0
        imgIdx = 0
        #	capturing required number of views
        while(successes < n_boards):
            found = 0
            img = imageList[imgIdx]
            (found, corners) = cv.FindChessboardCorners(img.getGrayscaleMatrix(), board_sz,
                                                     cv.CV_CALIB_CB_ADAPTIVE_THRESH | 
                                                     cv.CV_CALIB_CB_FILTER_QUADS)
            corners = cv.FindCornerSubPix(img.getGrayscaleMatrix(), corners,(11, 11),(-1, -1),
                                        (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 30, 0.1)) 	
            # if got a good image,draw chess board
            if found == 1:
                corner_count = len(corners)
                z = z + 1
      
            # if got a good image, add to matrix
            if len(corners) == board_n:
                step = successes * board_n
                k = step
                for j in range(board_n):
                    cv.Set2D(image_points, k, 0, corners[j][0])
                    cv.Set2D(image_points, k, 1, corners[j][1])
                    cv.Set2D(object_points, k, 0, grid_sz*(float(j)/float(board_w)))
                    cv.Set2D(object_points, k, 1, grid_sz*(float(j)%float(board_w)))
                    cv.Set2D(object_points, k, 2, 0.0)
                    k = k + 1
                cv.Set2D(point_counts, successes, 0, board_n)
                successes = successes + 1
    
        # now assigning new matrices according to view_count
        if( successes < warn_thresh ):
            logger.warning("FrameSource.calibrate: You have %s good images for calibration we recommend at least %s" % (successes, warn_thresh)) 
    
        object_points2 = cv.CreateMat(successes * board_n, 3, cv.CV_32FC1)
        image_points2 = cv.CreateMat(successes * board_n, 2, cv.CV_32FC1)
        point_counts2 = cv.CreateMat(successes, 1, cv.CV_32SC1)
    
        for i in range(successes * board_n):
            cv.Set2D(image_points2, i, 0, cv.Get2D(image_points, i, 0))
            cv.Set2D(image_points2, i, 1, cv.Get2D(image_points, i, 1))
            cv.Set2D(object_points2, i, 0, cv.Get2D(object_points, i, 0))
            cv.Set2D(object_points2, i, 1, cv.Get2D(object_points, i, 1))
            cv.Set2D(object_points2, i, 2, cv.Get2D(object_points, i, 2))
        for i in range(successes):
            cv.Set2D(point_counts2, i, 0, cv.Get2D(point_counts, i, 0))
    
        cv.Set2D(intrinsic_matrix, 0, 0, 1.0)
        cv.Set2D(intrinsic_matrix, 1, 1, 1.0)
        rcv = cv.CreateMat(n_boards, 3, cv.CV_64FC1)
        tcv = cv.CreateMat(n_boards, 3, cv.CV_64FC1)
        # camera calibration
        cv.CalibrateCamera2(object_points2, image_points2, point_counts2,
                            (img.width, img.height), intrinsic_matrix,distortion_coefficient,
                            rcv, tcv, 0)
        self._calibMat = intrinsic_matrix
        self._distCoeff = distortion_coefficient
        return intrinsic_matrix

    def getCameraMatrix(self):
        """
        **SUMMARY**

        This function returns a cvMat of the camera's intrinsic matrix. 
        If there is no matrix defined the function returns None. 

        """
        return self._calibMat

    def undistort(self, image_or_2darray):
        """
        **SUMMARY**

        If given an image, apply the undistortion given my the camera's matrix and return the result.
        
        If given a 1xN 2D cvmat or a 2xN numpy array, it will un-distort points of
        measurement and return them in the original coordinate system.
        
        **PARAMETERS**
        
        * *image_or_2darray* - an image or an ndarray.
        
        **RETURNS**
        
        The undistorted image or the undistorted points. If the camera is un-calibrated 
        we return None.

        **EXAMPLE**
        
        >>> img = cam.getImage()
        >>> result = cam.undistort(img)

        
        """
        if(type(self._calibMat) != cv.cvmat or type(self._distCoeff) != cv.cvmat ):
            logger.warning("FrameSource.undistort: This operation requires calibration, please load the calibration matrix")
            return None
           
        if (type(image_or_2darray) == InstanceType and image_or_2darray.__class__ == Image):
            inImg = image_or_2darray # we have an image
            retVal = inImg.getEmpty()
            cv.Undistort2(inImg.getBitmap(), retVal, self._calibMat, self._distCoeff)
            return Image(retVal)
        else:
            mat = ''
            if (type(image_or_2darray) == cv.cvmat):
                mat = image_or_2darray
            else:
                arr = cv.fromarray(np.array(image_or_2darray))
                mat = cv.CreateMat(cv.GetSize(arr)[1], 1, cv.CV_64FC2)
                cv.Merge(arr[:, 0], arr[:, 1], None, None, mat)
             
            upoints = cv.CreateMat(cv.GetSize(mat)[1], 1, cv.CV_64FC2)
            cv.UndistortPoints(mat, upoints, self._calibMat, self._distCoeff)
            
            #undistorted.x = (x* focalX + principalX);  
            #undistorted.y = (y* focalY + principalY);  
            return (np.array(upoints[:, 0]) *\
                [self.getCameraMatrix()[0, 0], self.getCameraMatrix()[1, 1]] +\
                [self.getCameraMatrix()[0, 2], self.getCameraMatrix()[1, 2]])[:, 0]

    def getImageUndistort(self):
        """
        **SUMMARY**

        Using the overridden getImage method we retrieve the image and apply the undistortion
        operation. 


        **RETURNS**
        
        The latest image from the camera after applying undistortion.

        **EXAMPLE**
        
        >>> cam = Camera()
        >>> cam.loadCalibration("mycam.xml")
        >>> while True:
        >>>    img = cam.getImageUndistort()
        >>>    img.show()

        """
        return self.undistort(self.getImage())
  
  
    def saveCalibration(self, filename):
        """
        **SUMMARY**

        Save the calibration matrices to file. The file name should be without the extension.
        The default extension is .xml.

        **PARAMETERS**
        
        * *fileneame* - The file name, without an extension, to which to save the calibration data.
        
        **RETURNS**

        Returns true if the file was saved , false otherwise. 

        **EXAMPLE**

        See :py:module:calibrate.py
        

        """
        if( type(self._calibMat) != cv.cvmat ):
            logger.warning("FrameSource.saveCalibration: No calibration matrix present, can't save.")
        else:
            intrFName = filename + "Intrinsic.xml"
            cv.Save(intrFName, self._calibMat)

        if( type(self._distCoeff) != cv.cvmat ):
            logger.warning("FrameSource.saveCalibration: No calibration distortion present, can't save.")
        else:      
            distFName = filename + "Distortion.xml"
            cv.Save(distFName, self._distCoeff)
        
        return None

    def loadCalibration(self, filename):
        """
        **SUMMARY**

        Load a calibration matrix from file.
        The filename should be the stem of the calibration files names.
        e.g. If the calibration files are MyWebcamIntrinsic.xml and MyWebcamDistortion.xml
        then load the calibration file "MyWebcam"

        **PARAMETERS**
        
        * *fileneame* - The file name, without an extension, to which to save the calibration data.
        
        **RETURNS**

        Returns true if the file was loaded , false otherwise. 

        **EXAMPLE**

        See :py:module:calibrate.py
 
        """
        retVal = False
        intrFName = filename + "Intrinsic.xml"
        self._calibMat = cv.Load(intrFName)
        distFName = filename + "Distortion.xml"
        self._distCoeff = cv.Load(distFName)
        if( type(self._distCoeff) == cv.cvmat
            and type(self._calibMat) == cv.cvmat):
            retVal = True
    
        return retVal
    
    def live(self):
        """
        **SUMMARY**

        This shows a live view of the camera.

        **EXAMPLE**

        To use it's as simple as:

        >>> cam = Camera()
        >>> cam.live()

        Left click will show mouse coordinates and color
        Right click will kill the live image
        """

        start_time = time.time()
        
        from SimpleCV.Display import Display
        i = self.getImage()
        d = Display(i.size())
        i.save(d)
        col = Color.RED

        while d.isNotDone():
          i = self.getImage()
          elapsed_time = time.time() - start_time
          

          if d.mouseLeft:
            txt = "coord: (" + str(d.mouseX) + "," + str(d.mouseY) + ")"
            i.dl().text(txt, (10,i.height / 2), color=col)
            txt = "color: " + str(i.getPixel(d.mouseX,d.mouseY))
            i.dl().text(txt, (10,(i.height / 2) + 10), color=col)
            print "coord: (" + str(d.mouseX) + "," + str(d.mouseY) + "), color: " + str(i.getPixel(d.mouseX,d.mouseY))


          if elapsed_time > 0 and elapsed_time < 5:
            
            i.dl().text("In live mode", (10,10), color=col)
            i.dl().text("Left click will show mouse coordinates and color", (10,20), color=col)
            i.dl().text("Right click will kill the live image", (10,30), color=col)

          
          i.save(d)
          if d.mouseRight:
            print "Closing Window"
            d.done = True

        
        pg.quit()
 
class Camera(FrameSource):
    """
    **SUMMARY**

    The Camera class is the class for managing input from a basic camera.  Note
    that once the camera is initialized, it will be locked from being used 
    by other processes.  You can check manually if you have compatable devices
    on linux by looking for /dev/video* devices.

    This class wrappers OpenCV's cvCapture class and associated methods.  
    Read up on OpenCV's CaptureFromCAM method for more details if you need finer
    control than just basic frame retrieval
    """
    capture = ""   #cvCapture object
    thread = ""
    pygame_camera = False
    pygame_buffer = ""
  
  
    prop_map = {"width": cv.CV_CAP_PROP_FRAME_WIDTH,
        "height": cv.CV_CAP_PROP_FRAME_HEIGHT,
        "brightness": cv.CV_CAP_PROP_BRIGHTNESS,
        "contrast": cv.CV_CAP_PROP_CONTRAST,
        "saturation": cv.CV_CAP_PROP_SATURATION,
        "hue": cv.CV_CAP_PROP_HUE,
        "gain": cv.CV_CAP_PROP_GAIN,
        "exposure": cv.CV_CAP_PROP_EXPOSURE}
    #human readable to CV constant property mapping

    def __init__(self, camera_index = -1, prop_set = {}, threaded = True, calibrationfile = ''):
        global _cameras
        global _camera_polling_thread
        """
        **SUMMARY**

        In the camera onstructor, camera_index indicates which camera to connect to
        and props is a dictionary which can be used to set any camera attributes
        Supported props are currently: height, width, brightness, contrast,
        saturation, hue, gain, and exposure.

        You can also specify whether you want the FrameBufferThread to continuously
        debuffer the camera.  If you specify True, the camera is essentially 'on' at
        all times.  If you specify off, you will have to manage camera buffers.

        **PARAMETERS**

        * *camera_index* - The index of the camera, these go from 0 upward, and are system specific. 
        * *prop_set* - The property set for the camera (i.e. a dict of camera properties). 

        .. Warning::
          For most web cameras only the width and height properties are supported. Support 
          for all of the other parameters varies by camera and operating system. 

        * *threaded* - If True we constantly debuffer the camera, otherwise the user 
          must do this manually.

        * *calibrationfile* - A calibration file to load. 

   
        """

        #This fixes bug with opencv not being able to grab frames from webcams on linux
        self.capture = cv.CaptureFromCAM(camera_index)
        if platform.system() == "Linux" and (prop_set.has_key("height") or cv.GrabFrame(self.capture) == False):
            import pygame.camera
            pygame.camera.init()
            threaded = True  #pygame must be threaded
            if camera_index == -1:
              camera_index = 0
            if(prop_set.has_key("height") and prop_set.has_key("width")):
                self.capture = pygame.camera.Camera("/dev/video" + str(camera_index), (prop_set['width'], prop_set['height']))
            else:
                self.capture = pygame.camera.Camera("/dev/video" + str(camera_index))

            try:
              self.capture.start()
            except:
              logger.warning("SimpleCV can't seem to find a camera on your system, or the drivers do not work with SimpleCV.")
              return
            time.sleep(0)
            self.pygame_buffer = self.capture.get_image()
            self.pygame_camera = True
        else:
            self.threaded = False
            if (platform.system() == "Windows"):
                threaded = False
        
            if (not self.capture):
                return None 

            #set any properties in the constructor
            for p in prop_set.keys():
                if p in self.prop_map:
                    cv.SetCaptureProperty(self.capture, self.prop_map[p], prop_set[p])

        if (threaded):
            self.threaded = True
            _cameras.append(self)
            if (not _camera_polling_thread):
                _camera_polling_thread = FrameBufferThread()
                _camera_polling_thread.daemon = True
                _camera_polling_thread.start()
                time.sleep(0) #yield to thread
        
        if calibrationfile:
            self.loadCalibration(calibrationfile)
          
        
    #todo -- make these dynamic attributes of the Camera class
    def getProperty(self, prop):
        """
        **SUMMARY**

        Retrieve the value of a given property, wrapper for cv.GetCaptureProperty

        .. Warning::
          For most web cameras only the width and height properties are supported. Support 
          for all of the other parameters varies by camera and operating system. 

        **PARAMETERS**

        * *prop* - The property to retrive.

        **RETURNS**

        The specified property. If it can't be found the method returns False.

        **EXAMPLE**

        >>> cam = Camera()
        >>> prop = cam.getProperty("width")
        """
        if self.pygame_camera:
          if prop.lower() == 'width':
            return self.capture.get_size()[0]
          elif prop.lower() == 'height':
            return self.capture.get_size()[1]
          else:
            return False
            
        if prop in self.prop_map:
            return cv.GetCaptureProperty(self.capture, self.prop_map[prop])
        return False 

    def getAllProperties(self):
        """
        **SUMMARY**

        Return all properties from the camera.

        **RETURNS**
        
        A dict of all the camera properties. 

        """
        if self.pygame_camera:
            return False
        props = {} 
        for p in self.prop_map:
            props[p] = self.getProperty(p)
    
        return props
 
    def getImage(self):
        """
        **SUMMARY**

        Retrieve an Image-object from the camera.  If you experience problems
        with stale frames from the camera's hardware buffer, increase the flushcache
        number to dequeue multiple frames before retrieval

        We're working on how to solve this problem.

        **RETURNS**
        
        A SimpleCV Image from the camera.

        **EXAMPLES**
        
        >>> cam = Camera()
        >>> while True:
        >>>    cam.getImage().show()

        """
        
        if self.pygame_camera:
            return Image(self.pygame_buffer.copy())
        
        if (not self.threaded):
            cv.GrabFrame(self.capture)
            self.capturetime = time.time()
        else:
            self.capturetime = self._threadcapturetime

        frame = cv.RetrieveFrame(self.capture)
        newimg = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
        cv.Copy(frame, newimg)
        return Image(newimg, self)


          
class VirtualCamera(FrameSource):
    """
    **SUMMARY**

    The virtual camera lets you test algorithms or functions by providing 
    a Camera object which is not a physically connected device.
    
    Currently, VirtualCamera supports "image", "imageset" and "video" source types.
   
    **USAGE**

    * For image, pass the filename or URL to the image
    * For the video, the filename
    * For imageset, you can pass either a path or a list of [path, extension]
    
    """
    source = ""
    sourcetype = ""
  
    def __init__(self, s, st):
        """
        **SUMMARY**

        The constructor takes a source, and source type. 
        
        **PARAMETERS**
        
        * *s* - the source of the imagery.
        * *st* - the type of the virtual camera. Valid strings include:
          
          * "image" - a single still image.
          * "video" - a video file.
          * "imageset" - a SimpleCV image set. 

        **EXAMPLE**
          
        >>> vc = VirtualCamera("img.jpg", "image")
        >>> vc = VirtualCamera("video.mpg", "video")

        """
        self.source = s
        self.sourcetype = st
        self.counter = 0
        
        if (self.sourcetype == "imageset"):
            self.source = ImageSet()
            if (type(s) == list):
                self.source.load(*s)
            else:
                self.source.load(s)
        
        if (self.sourcetype == 'video'):
            self.capture = cv.CaptureFromFile(self.source) 
    
    def getImage(self):
        """
        **SUMMARY**

        Retrieve an Image-object from the virtual camera.
        **RETURNS**
        
        A SimpleCV Image from the camera.

        **EXAMPLES**
        
        >>> cam = VirtualCamera()
        >>> while True:
        >>>    cam.getImage().show()

        """
        if (self.sourcetype == 'image'):
            return Image(self.source, self)
            
        if (self.sourcetype == 'imageset'):
            img = self.source[self.counter % len(self.source)]
            self.counter = self.counter + 1
            return img
        
        if (self.sourcetype == 'video'):
            return Image(cv.QueryFrame(self.capture), self)
 
class Kinect(FrameSource):
    """
    **SUMMARY**
    
    This is an experimental wrapper for the Freenect python libraries
    you can getImage() and getDepth() for separate channel images
    
    """
    def __init__(self):
        if not FREENECT_ENABLED:
            logger.warning("You don't seem to have the freenect library installed.  This will make it hard to use a Kinect.")
  
    #this code was borrowed from
    #https://github.com/amiller/libfreenect-goodies
    def getImage(self):
        """
        **SUMMARY**
        
        This method returns the Kinect camera image. 

        **RETURNS**
        
        The Kinect's color camera image. 

        **EXAMPLE**

        >>> k = Kinect()
        >>> while True:
        >>>   k.getImage().show()

        """
        video = freenect.sync_get_video()[0]
        self.capturetime = time.time()
        #video = video[:, :, ::-1]  # RGB -> BGR
        return Image(video.transpose([1,0,2]), self)
  
    #low bits in this depth are stripped so it fits in an 8-bit image channel
    def getDepth(self):
        """
        **SUMMARY**
        
        This method returns the Kinect depth image. 

        **RETURNS**
        
        The Kinect's depth camera image as a grayscale image. 

        **EXAMPLE**

        >>> k = Kinect()
        >>> while True:
        >>>   d = k.getDepth()
        >>>   img = k.getImage()
        >>>   result = img.sideBySide(d)
        >>>   result.show()
        """

        depth = freenect.sync_get_depth()[0]
        self.capturetime = time.time()
        np.clip(depth, 0, 2**10 - 1, depth)
        depth >>= 2
        depth = depth.astype(np.uint8).transpose()
    
        return Image(depth, self) 
  
    #we're going to also support a higher-resolution (11-bit) depth matrix
    #if you want to actually do computations with the depth
    def getDepthMatrix(self):
        self.capturetime = time.time()
        return freenect.sync_get_depth()[0]
  


class JpegStreamReader(threading.Thread):
    """
    **SUMMARY**

    A Threaded class for pulling down JPEG streams and breaking up the images. This
    is handy for reading the stream of images from a IP CAmera.

    """
    url = ""
    currentframe = ""
    _threadcapturetime = ""
  
    def run(self):
      
        f = ''
        
        if re.search('@', self.url):
            authstuff = re.findall('//(\S+)@', self.url)[0]
            self.url = re.sub("//\S+@", "//", self.url)
            user, password = authstuff.split(":")
            
            #thank you missing urllib2 manual 
            #http://www.voidspace.org.uk/python/articles/urllib2.shtml#id5
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.url, user, password)
            
            handler = urllib2.HTTPBasicAuthHandler(password_mgr)
            opener = urllib2.build_opener(handler)
            
            f = opener.open(self.url)
        else:
            f = urllib2.urlopen(self.url)
        
        headers = f.info()
        if (headers.has_key("content-type")):
            headers['Content-type'] = headers['content-type'] #force ucase first char
    
        if not headers.has_key("Content-type"):
            logger.warning("Tried to load a JpegStream from " + self.url + ", but didn't find a content-type header!")
            return
    
        (multipart, boundary) = headers['Content-type'].split("boundary=")
        if not re.search("multipart", multipart, re.I):
            logger.warning("Tried to load a JpegStream from " + self.url + ", but the content type header was " + multipart + " not multipart/replace!")
            return 
    
        buff = ''
        data = f.readline().strip()
        length = 0 
        contenttype = "jpeg"
    
        #the first frame contains a boundarystring and some header info
        while (1):
            #print data
            if (re.search(boundary, data.strip()) and len(buff)):
                #we have a full jpeg in buffer.  Convert to an image
                if contenttype == "jpeg":
                    self.currentframe = buff 
                    self._threadcapturetime = time.time()
                buff = ''
      
            if (re.match("Content-Type", data, re.I)):
                #set the content type, if provided (default to jpeg)
                (header, typestring) = data.split(":")
                (junk, contenttype) = typestring.strip().split("/")
      
            if (re.match("Content-Length", data, re.I)):
                #once we have the content length, we know how far to go jfif
                (header, length) = data.split(":")
                length = int(length.strip())
               
            if (re.search("JFIF", data, re.I) or re.search("\xff\xd8\xff\xdb", data) or len(data) > 55):
                # we have reached the start of the image 
                buff = '' 
                if length and length > len(data):
                    buff += data + f.read(length - len(data)) #read the remainder of the image
                    if contenttype == "jpeg":
                        self.currentframe = buff
                        self._threadcapturetime = time.time()
                else:
                    while (not re.search(boundary, data)):
                        buff += data 
                        data = f.readline()
          
                    endimg, junk = data.split(boundary) 
                    buff += endimg
                    data = boundary
                    continue
                    
            data = f.readline() #load the next (header) line
            time.sleep(0) #let the other threads go

class JpegStreamCamera(FrameSource):
    """
    **SUMMARY**

    The JpegStreamCamera takes a URL of a JPEG stream and treats it like a camera.  The current frame can always be accessed with getImage() 
    
    Requires the Python Imaging Library: http://www.pythonware.com/library/pil/handbook/index.htm
    
    **EXAMPLE**  
  
    Using your Android Phone as a Camera. Softwares like IP Webcam can be used.
    
    >>> cam = JpegStreamCamera("http://192.168.65.101:8080/videofeed") # your IP may be different.
    >>> img = cam.getImage()
    >>> img.show()
    
    """
    url = ""
    camthread = ""
    
    def __init__(self, url):
        if not PIL_ENABLED:
            logger.warning("You need the Python Image Library (PIL) to use the JpegStreamCamera")
            return
        if not url.startswith('http://'):
            url = "http://" + url
        self.url = url
        self.camthread = JpegStreamReader()
        self.camthread.url = self.url
        self.camthread.daemon = True
        self.camthread.start()
  
    def getImage(self):
        """
        **SUMMARY**

        Return the current frame of the JpegStream being monitored

        """
        if not self.camthread._threadcapturetime:
            now = time.time()
            while not self.camthread._threadcapturetime:
                if time.time() - now > 5:
                    warnings.warn("Timeout fetching JpegStream at " + self.url)
                    return
                time.sleep(0.1)
                
        self.capturetime = self.camthread._threadcapturetime
        return Image(pil.open(StringIO(self.camthread.currentframe)), self)



