# SimpleCV Cameras & Devices

#load system libraries
from SimpleCV.base import *
from SimpleCV.ImageClass import Image 
import platform

#Globals
_cameras = [] 
_camera_polling_thread = ""
 

class FrameBufferThread(threading.Thread):
    """
    This is a helper thread which continually debuffers the camera frames.  If
    you don't do this, cameras may constantly give you a frame behind, which
    causes problems at low sample rates.  This makes sure the frames returned
    by your camera are fresh.
    """
    def run(self):
        global _cameras
        while (1):
            for cam in _cameras:
                cv.GrabFrame(cam.capture)
            time.sleep(0.04)    #max 25 fps, if you're lucky



class FrameSource:
    """
    An abstract Camera-type class, for handling multiple types of video input.
    Any sources of images inheirit from it
    """
    _calibMat = "" #Intrinsic calibration matrix 
    _distCoeff = "" #Distortion matrix
    def __init__(self):
        return
    
    def getPropery(self, p):
        return None
  
    def getAllProperties(self):
        return {}
  
    def getImage(self):
        return None

    def calibrate(self, imageList, grid_sz=0.03, dimensions=(8, 5)):
        """
        Camera calibration will help remove distortion and fisheye effects
        It is agnostic of the imagery source, and can be used with any camera
    
        imageList is a list of images of color calibration images. 
    
        grid_sz - is the actual grid size of the calibration grid, the unit used will be 
        the calibration unit value (i.e. if in doubt use meters, or U.S. standard)
    
        dimensions - is the the count of the *interior* corners in the calibration grid.
        So for a grid where there are 4x4 black grid squares has seven interior corners.

        The easiest way to run calibration is to run the
        calibrate.py file under the tools directory for SimpleCV.
        This will walk you through the calibration process.
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
            warnings.warn("FrameSource.calibrate: We suggest using 20 or more images to perform camera calibration!" ) 
    
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
            warnings.warn("FrameSource.calibrate: You have %s good images for calibration we recommend at least %s" % (successes, warn_thresh)) 
    
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
        This function returns a cvMat of the camera's intrinsic matrix. 
        If there is no matrix defined the function returns None. 
        """
        return self._calibMat

    def undistort(self, image_or_2darray):
        """
        If given an image, apply the undistortion given my the camera's matrix and return the result
        
        If given a 1xN 2D cvmat or a 2xN numpy array, it will un-distort points of
        measurement and return them in the original coordinate system.
        
        """
        if(type(self._calibMat) != cv.cvmat or type(self._distCoeff) != cv.cvmat ):
            warnings.warn("FrameSource.undistort: This operation requires calibration, please load the calibration matrix")
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
        Using the overridden getImage method we retrieve the image and apply the undistortion
        operation. 
        """
        return self.undistort(self.getImage())
  
  
    def saveCalibration(self, filename):
        """
        Save the calibration matrices to file. The file name should be without the extension.
        The default extension is .xml
        Returns true if the file was successful loaded, false otherwise. 
        """
        if( type(self._calibMat) != cv.cvmat ):
            warnings.warn("FrameSource.saveCalibration: No calibration matrix present, can't save.")
        else:
            intrFName = filename + "Intrinsic.xml"
            cv.Save(intrFName, self._calibMat)

        if( type(self._distCoeff) != cv.cvmat ):
            warnings.warn("FrameSource.saveCalibration: No calibration distortion present, can't save.")
        else:      
            distFName = filename + "Distortion.xml"
            cv.Save(distFName, self._distCoeff)
        
        return None

    def loadCalibration(self, filename):
        """
        Load a calibration matrix from file.
        The filename should be the stem of the calibration files names.
        e.g. If the calibration files are MyWebcamIntrinsic.xml and MyWebcamDistortion.xml
        then load the calibration file "MyWebcam"
    
    
        Returns true if the file was successful loaded, false otherwise. 
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
 
class Camera(FrameSource):
    """
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
  
  
    prop_map = {"width": cv.CV_CAP_PROP_FRAME_WIDTH,
        "height": cv.CV_CAP_PROP_FRAME_HEIGHT,
        "brightness": cv.CV_CAP_PROP_BRIGHTNESS,
        "contrast": cv.CV_CAP_PROP_CONTRAST,
        "saturation": cv.CV_CAP_PROP_SATURATION,
        "hue": cv.CV_CAP_PROP_HUE,
        "gain": cv.CV_CAP_PROP_GAIN,
        "exposure": cv.CV_CAP_PROP_EXPOSURE}
    #human readable to CV constant property mapping

    def __init__(self, camera_index = 0, prop_set = {}, threaded = True, calibrationfile = ''):
        global _cameras
        global _camera_polling_thread
        """
        In the camera onstructor, camera_index indicates which camera to connect to
        and props is a dictionary which can be used to set any camera attributes
        Supported props are currently: height, width, brightness, contrast,
        saturation, hue, gain, and exposure.

        You can also specify whether you want the FrameBufferThread to continuously
        debuffer the camera.  If you specify True, the camera is essentially 'on' at
        all times.  If you specify off, you will have to manage camera buffers.
        """
        self.capture = cv.CaptureFromCAM(camera_index)
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
        Retrieve the value of a given property, wrapper for cv.GetCaptureProperty
        """
        if prop in self.prop_map:
            return cv.GetCaptureProperty(self.capture, self.prop_map[prop])
        return False 

    def getAllProperties(self):
        """
        Return all properties from the camera 
        """
        props = {} 
        for p in self.prop_map:
            props[p] = self.getProperty(p)
    
        return props
 
    def getImage(self):
        """
        Retrieve an Image-object from the camera.  If you experience problems
        with stale frames from the camera's hardware buffer, increase the flushcache
        number to dequeue multiple frames before retrieval

        We're working on how to solve this problem.
        """
        if (not self.threaded):
            cv.GrabFrame(self.capture)

        frame = cv.RetrieveFrame(self.capture)
        newimg = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
        cv.Copy(frame, newimg)
        return Image(newimg, self)

class VirtualCamera(FrameSource):
    """
    The virtual camera lets you test algorithms or functions by providing 
    a Camera object which is not a physically connected device.
    
    Currently, VirtualCamera supports "image" and "video" source types.
    """
    source = ""
    sourcetype = ""
  
    def __init__(self, s, st):
        """
        The constructor takes a source, and source type.  ie:
        VirtualCamera("img.jpg", "image") or VirtualCamera("video.mpg", "video")
        """
        self.source = s
        self.sourcetype = st 
        
        if (self.sourcetype == 'video'):
            self.capture = cv.CaptureFromFile(self.source) 
    
    def getImage(self):
        """
        Retrieve the next frame of the video, or just a copy of the image
        """
        if (self.sourcetype == 'image'):
            return Image(self.source, self)
        
        if (self.sourcetype == 'video'):
            return Image(cv.QueryFrame(self.capture), self)
 
class Kinect(FrameSource):
    """
      This is an experimental wrapper for the Freenect python libraries
      you can getImage() and getDepth() for separate channel images
    """
    def __init__(self):
        if not FREENECT_ENABLED:
            warnings.warn("You don't seem to have the freenect library installed.  This will make it hard to use a Kinect.")
  
    #this code was borrowed from
    #https://github.com/amiller/libfreenect-goodies
    def getImage(self):
        video = freenect.sync_get_video()[0]
        #video = video[:, :, ::-1]  # RGB -> BGR
        return Image(video.transpose([1,0,2]), self)
  
    #low bits in this depth are stripped so it fits in an 8-bit image channel
    def getDepth(self):
        depth = freenect.sync_get_depth()[0]
        np.clip(depth, 0, 2**10 - 1, depth)
        depth >>= 2
        depth = depth.astype(np.uint8).transpose()
    
        return Image(depth, self) 
  
    #we're going to also support a higher-resolution (11-bit) depth matrix
    #if you want to actually do computations with the depth
    def getDepthMatrix(self):
        return freenect.sync_get_depth()[0]
  


class JpegStreamReader(threading.Thread):
    """
    Threaded class for pulling down JPEG streams and breaking up the images
    """
    url = ""
    currentframe = ""
  
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
            warnings.warn("Tried to load a JpegStream from " + self.url + ", but didn't find a content-type header!")
            return
    
        (multipart, boundary) = headers['Content-type'].split("boundary=")
        if not re.search("multipart", multipart, re.I):
            warnings.warn("Tried to load a JpegStream from " + self.url + ", but the content type header was " + multipart + " not multipart/replace!")
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
                self.currentframe = buff 
                buff = ''
      
            if (re.match("Content-Type", data, re.I)):
                #set the content type, if provided (default to jpeg)
                (header, typestring) = data.split(":")
                (junk, contenttype) = typestring.strip().split("/")
      
            if (re.match("Content-Length", data, re.I)):
                #once we have the content length, we know how far to go jfif
                (header, length) = data.split(":")
                length = int(length.strip())
               
            if (re.search("JFIF", data, re.I) or len(data) > 70):
                # we have reached the start of the image 
                buff = '' 
                if length:
                    buff += data + f.read(length - len(data)) #read the remainder of the image
                    self.currentframe = buff
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
    The JpegStreamCamera takes a URL of a JPEG stream and treats it like a camera.  The current frame can always be accessed with getImage() 

    Requires the [Python Imaging Library](http://www.pythonware.com/library/pil/handbook/index.htm)
    """
    url = ""
    camthread = ""
    
    def __init__(self, url):
        if not PIL_ENABLED:
            warnings.warn("You need the Python Image Library (PIL) to use the JpegStreamCamera")
            return
    
        self.url = url
        self.camthread = JpegStreamReader()
        self.camthread.url = self.url
        self.camthread.daemon = True
        self.camthread.start()
  
    def getImage(self):
        """
        Return the current frame of the JpegStream being monitored
        """
        return Image(pil.open(StringIO(self.camthread.currentframe)), self)

