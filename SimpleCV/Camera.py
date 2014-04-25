# SimpleCV Cameras & Devices

#load system libraries
from SimpleCV.base import *
from SimpleCV.ImageClass import Image, ImageSet, ColorSpace
from SimpleCV.Display import Display
from SimpleCV.Color import Color
from collections import deque
import time
import ctypes as ct
import subprocess
import cv2
import numpy as np
import traceback
import sys

#Globals
_cameras = []
_camera_polling_thread = ""
_index = []

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
        n_boards = 0    #no of boards
        board_w = int(dimensions[0])    # number of horizontal corners
        board_h = int(dimensions[1])    # number of vertical corners
        n_boards = int(len(imageList))
        board_n = board_w * board_h             # no of total corners
        board_sz = (board_w, board_h)   #size of board
        if( n_boards < warn_thresh ):
            logger.warning("FrameSource.calibrate: We suggest using 20 or more images to perform camera calibration!" )

        #  creation of memory storages
        image_points = cv.CreateMat(n_boards * board_n, 2, cv.CV_32FC1)
        object_points = cv.CreateMat(n_boards * board_n, 3, cv.CV_32FC1)
        point_counts = cv.CreateMat(n_boards, 1, cv.CV_32SC1)
        intrinsic_matrix = cv.CreateMat(3, 3, cv.CV_32FC1)
        distortion_coefficient = cv.CreateMat(5, 1, cv.CV_32FC1)

        #       capture frames of specified properties and modification of matrix values
        i = 0
        z = 0           # to print number of frames
        successes = 0
        imgIdx = 0
        #       capturing required number of views
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

        If given an image, apply the undistortion given by the camera's matrix and return the result.

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

        * *filename* - The file name, without an extension, to which to save the calibration data.

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

        * *filename* - The file name, without an extension, to which to save the calibration data.

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
    by other processes.  You can check manually if you have compatible devices
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
        global _index
        """
        **SUMMARY**

        In the camera constructor, camera_index indicates which camera to connect to
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
        self.index = None
        self.threaded = False
        self.capture = None

        if platform.system() == "Linux" and -1 in _index and camera_index != -1 and camera_index not in _index:
            process = subprocess.Popen(["lsof /dev/video"+str(camera_index)],shell=True,stdout=subprocess.PIPE)
            data = process.communicate()
            if data[0]:
                camera_index = -1

        elif platform.system() == "Linux" and camera_index == -1 and -1 not in _index:
            process = subprocess.Popen(["lsof /dev/video*"],shell=True,stdout=subprocess.PIPE)
            data = process.communicate()
            if data[0]:
                camera_index = int(data[0].split("\n")[1].split()[-1][-1])

        for cam in _cameras:
            if camera_index == cam.index:
                self.threaded = cam.threaded
                self.capture = cam.capture
                self.index = cam.index
                _cameras.append(self)
                return

        #This is to add support for XIMEA cameras.
        if isinstance(camera_index, str):
            if camera_index.lower() == 'ximea':
                camera_index = 1100
                _index.append(camera_index)

        self.capture = cv.CaptureFromCAM(camera_index) #This fixes bug with opencv not being able to grab frames from webcams on linux
        self.index = camera_index
        if "delay" in prop_set:
            time.sleep(prop_set['delay'])

        if platform.system() == "Linux" and (prop_set.has_key("height") or cv.GrabFrame(self.capture) == False):
            import pygame.camera
            pygame.camera.init()
            threaded = True  #pygame must be threaded
            if camera_index == -1:
                camera_index = 0
                self.index = camera_index
                _index.append(camera_index)
                print _index
            if(prop_set.has_key("height") and prop_set.has_key("width")):
                self.capture = pygame.camera.Camera("/dev/video" + str(camera_index), (prop_set['width'], prop_set['height']))
            else:
                self.capture = pygame.camera.Camera("/dev/video" + str(camera_index))

            try:
                self.capture.start()
            except Exception as exc:
                msg = "caught exception: %r" % exc
                logger.warning(msg)
                logger.warning("SimpleCV can't seem to find a camera on your system, or the drivers do not work with SimpleCV.")
                return
            time.sleep(0)
            self.pygame_buffer = self.capture.get_image()
            self.pygame_camera = True
        else:
            _index.append(camera_index)
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
    * For directory you treat a directory to show the latest file, an example would be where a security camera logs images to the directory, calling .getImage() will get the latest in the directory

    """
    source = ""
    sourcetype = ""
    lastmtime = 0

    def __init__(self, s, st, start=1):
        """
        **SUMMARY**

        The constructor takes a source, and source type.

        **PARAMETERS**

        * *s* - the source of the imagery.
        * *st* - the type of the virtual camera. Valid strings include:
        * *start* - the number of the frame that you want to start with.

          * "image" - a single still image.
          * "video" - a video file.
          * "imageset" - a SimpleCV image set.
          * "directory" - a VirtualCamera for loading a directory

        **EXAMPLE**

        >>> vc = VirtualCamera("img.jpg", "image")
        >>> vc = VirtualCamera("video.mpg", "video")
        >>> vc = VirtualCamera("./path_to_images/", "imageset")
        >>> vc = VirtualCamera("video.mpg", "video", 300)
        >>> vc = VirtualCamera("./imgs", "directory")


        """
        self.source = s
        self.sourcetype = st
        self.counter = 0
        if start==0:
            start=1
        self.start = start

        if self.sourcetype not in ["video", "image", "imageset", "directory"]:
            print 'Error: In VirtualCamera(), Incorrect Source option. "%s" \nUsage:' % self.sourcetype
            print '\tVirtualCamera("filename","video")'
            print '\tVirtualCamera("filename","image")'
            print '\tVirtualCamera("./path_to_images","imageset")'
            print '\tVirtualCamera("./path_to_images","directory")'
            return None

        else:
            if isinstance(self.source,str) and not os.path.exists(self.source):
                print 'Error: In VirtualCamera()\n\t"%s" was not found.' % self.source
                return None

        if (self.sourcetype == "imageset"):
            if( isinstance(s,ImageSet) ):
                self.source = s
            elif( isinstance(s,(list,str)) ):
                self.source = ImageSet()
                if (isinstance(s,list)):
                    self.source.load(*s)
                else:
                    self.source.load(s)
            else:
                warnings.warn('Virtual Camera is unable to figure out the contents of your ImageSet, it must be a directory, list of directories, or an ImageSet object')
            

        elif (self.sourcetype == 'video'):
         
            self.capture = cv.CaptureFromFile(self.source)
            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES, self.start-1)

        elif (self.sourcetype == 'directory'):
            pass


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
            self.counter = self.counter + 1
            return Image(self.source, self)

        elif (self.sourcetype == 'imageset'):
            print len(self.source)
            img = self.source[self.counter % len(self.source)]
            self.counter = self.counter + 1
            return img

        elif (self.sourcetype == 'video'):
            # cv.QueryFrame returns None if the video is finished
            frame = cv.QueryFrame(self.capture)
            if frame:
                img = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 3)
                cv.Copy(frame, img)
                return Image(img, self)
            else:
                return None

        elif (self.sourcetype == 'directory'):
            img = self.findLastestImage(self.source, 'bmp')
            self.counter = self.counter + 1
            return Image(img, self)

    def rewind(self, start=None):
        """
        **SUMMARY**

        Rewind the Video source back to the given frame.
        Available for only video sources.

        **PARAMETERS**

        start - the number of the frame that you want to rewind to.
                if not provided, the video source would be rewound
                to the starting frame number you provided or rewound
                to the beginning.

        **RETURNS**

        None

        **EXAMPLES**

        >>> cam = VirtualCamera("filename.avi", "video", 120)
        >>> i=0
        >>> while i<60:
            ... cam.getImage().show()
            ... i+=1
        >>> cam.rewind()

        """
        if (self.sourcetype == 'video'):
            if not start:
                cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES, self.start-1)
            else:
                if start==0:
                    start=1
                cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES, start-1)

        else:
            self.counter = 0

    def getFrame(self, frame):
        """
        **SUMMARY**

        Get the provided numbered frame from the video source.
        Available for only video sources.

        **PARAMETERS**

        frame -  the number of the frame

        **RETURNS**

        Image

        **EXAMPLES**

        >>> cam = VirtualCamera("filename.avi", "video", 120)
        >>> cam.getFrame(400).show()

        """
        if (self.sourcetype == 'video'):
            number_frame = int(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES))
            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES, frame-1)
            img = self.getImage()
            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES, number_frame)
            return img
        elif (self.sourcetype == 'imageset'):
            img = None
            if( frame < len(self.source)):
                img = self.source[frame]
            return img
        else:
            return None


    def skipFrames(self, n):
        """
        **SUMMARY**

        Skip n number of frames.
        Available for only video sources.

        **PARAMETERS**

        n - number of frames to be skipped.

        **RETURNS**

        None

        **EXAMPLES**

        >>> cam = VirtualCamera("filename.avi", "video", 120)
        >>> i=0
        >>> while i<60:
            ... cam.getImage().show()
            ... i+=1
        >>> cam.skipFrames(100)
        >>> cam.getImage().show()

        """
        if (self.sourcetype == 'video'):
            number_frame = int(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES))
            cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES, number_frame + n - 1)
        elif (self.sourcetype == 'imageset'):
            self.counter = (self.counter + n) % len(self.source)
        else:
            self.counter = self.counter + n

    def getFrameNumber(self):
        """
        **SUMMARY**

        Get the current frame number of the video source.
        Available for only video sources.

        **RETURNS**

        * *int* - number of the frame

        **EXAMPLES**

        >>> cam = VirtualCamera("filename.avi", "video", 120)
        >>> i=0
        >>> while i<60:
            ... cam.getImage().show()
            ... i+=1
        >>> cam.skipFrames(100)
        >>> cam.getFrameNumber()

        """
        if (self.sourcetype == 'video'):
            number_frame = int(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_FRAMES))
            return number_frame
        else:
            return self.counter

    def getCurrentPlayTime(self):
        """
        **SUMMARY**

        Get the current play time in milliseconds of the video source.
        Available for only video sources.

        **RETURNS**

        * *int* - milliseconds of time from beginning of file.

        **EXAMPLES**

        >>> cam = VirtualCamera("filename.avi", "video", 120)
        >>> i=0
        >>> while i<60:
            ... cam.getImage().show()
            ... i+=1
        >>> cam.skipFrames(100)
        >>> cam.getCurrentPlayTime()

        """
        if (self.sourcetype == 'video'):
            milliseconds = int(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_POS_MSEC))
            return milliseconds
        else:
            raise ValueError('sources other than video do not have play time property')

    def findLastestImage(self, directory='.', extension='png'):
        """
        **SUMMARY**

        This function finds the latest file in a directory
        with a given extension.

        **PARAMETERS**

        directory - The directory you want to load images from (defaults to current directory)
        extension - The image extension you want to use (defaults to .png)

        **RETURNS**

        The filename of the latest image

        **USAGE**

        >>> cam = VirtualCamera('imgs/', 'png') #find all .png files in 'img' directory
        >>> cam.getImage() # Grab the latest image from that directory

        """
        max_mtime = 0
        max_dir = None
        max_file = None
        max_full_path = None
        for dirname,subdirs,files in os.walk(directory):
            for fname in files:
                if fname.split('.')[-1] == extension:
                    full_path = os.path.join(dirname, fname)
                    mtime = os.stat(full_path).st_mtime
                    if mtime > max_mtime:
                        max_mtime = mtime
                        max_dir = dirname
                        max_file = fname
                        self.lastmtime = mtime
                        max_full_path = os.path.abspath(os.path.join(dirname, fname))

        #if file is being written, block until mtime is at least 100ms old
        while time.mktime(time.localtime()) - os.stat(max_full_path).st_mtime < 0.1:
            time.sleep(0)

        return max_full_path

class Kinect(FrameSource):
    """
    **SUMMARY**

    This is an experimental wrapper for the Freenect python libraries
    you can getImage() and getDepth() for separate channel images

    """
    def __init__(self, device_number=0):
        """
        **SUMMARY**

        In the kinect contructor, device_number indicates which kinect to
        connect to. It defaults to 0.

        **PARAMETERS**

        * *device_number* - The index of the kinect, these go from 0 upward.
        """
        self.deviceNumber = device_number
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
        video = freenect.sync_get_video(self.deviceNumber)[0]
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

        depth = freenect.sync_get_depth(self.deviceNumber)[0]
        self.capturetime = time.time()
        np.clip(depth, 0, 2**10 - 1, depth)
        depth >>= 2
        depth = depth.astype(np.uint8).transpose()

        return Image(depth, self)

    #we're going to also support a higher-resolution (11-bit) depth matrix
    #if you want to actually do computations with the depth
    def getDepthMatrix(self):
        self.capturetime = time.time()
        return freenect.sync_get_depth(self.deviceNumber)[0]



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


_SANE_INIT = False

class Scanner(FrameSource):
    """
    **SUMMARY**

    The Scanner lets you use any supported SANE-compatable scanner as a SimpleCV camera
    List of supported devices: http://www.sane-project.org/sane-supported-devices.html

    Requires the PySANE wrapper for libsane.  The sane scanner object
    is available for direct manipulation at Scanner.device

    This scanner object is heavily modified from
    https://bitbucket.org/DavidVilla/pysane

    Constructor takes an index (default 0) and a list of SANE options
    (default is color mode).

    **EXAMPLE**

    >>> scan = Scanner(0, { "mode": "gray" })
    >>> preview = scan.getPreview()
    >>> stuff = preview.findBlobs(minsize = 1000)
    >>> topleft = (np.min(stuff.x()), np.min(stuff.y()))
    >>> bottomright = (np.max(stuff.x()), np.max(stuff.y()))
    >>> scan.setROI(topleft, bottomright)
    >>> scan.setProperty("resolution", 1200) #set high resolution
    >>> scan.setProperty("mode", "color")
    >>> img = scan.getImage()
    >>> scan.setROI() #reset region of interest
    >>> img.show()


    """
    usbid = None
    manufacturer = None
    model = None
    kind = None
    device = None
    max_x = None
    max_y = None

    def __init__(self, id = 0, properties = { "mode": "color"}):
        global _SANE_INIT
        import sane
        if not _SANE_INIT:
            try:
                sane.init()
                _SANE_INIT = True
            except:
                warn("Initializing pysane failed, do you have pysane installed?")
                return

        devices = sane.get_devices()
        if not len(devices):
            warn("Did not find a sane-compatable device")
            return

        self.usbid, self.manufacturer, self.model, self.kind = devices[id]

        self.device = sane.open(self.usbid)
        self.max_x = self.device.br_x
        self.max_y = self.device.br_y #save our extents for later

        for k, v in properties.items():
            setattr(self.device, k, v)

    def getImage(self):
        """
        **SUMMARY**

        Retrieve an Image-object from the scanner.  Any ROI set with
        setROI() is taken into account.
        **RETURNS**

        A SimpleCV Image.  Note that whatever the scanner mode is,
        SimpleCV will return a 3-channel, 8-bit image.

        **EXAMPLES**
        >>> scan = Scanner()
        >>> scan.getImage().show()
        """
        return Image(self.device.scan())

    def getPreview(self):
        """
        **SUMMARY**

        Retrieve a preview-quality Image-object from the scanner.
        **RETURNS**

        A SimpleCV Image.  Note that whatever the scanner mode is,
        SimpleCV will return a 3-channel, 8-bit image.

        **EXAMPLES**
        >>> scan = Scanner()
        >>> scan.getPreview().show()
        """
        self.preview = True
        img = Image(self.device.scan())
        self.preview = False
        return img

    def getAllProperties(self):
        """
        **SUMMARY**

        Return a list of all properties and values from the scanner
        **RETURNS**

        Dictionary of active options and values.  Inactive options appear
        as "None"

        **EXAMPLES**
        >>> scan = Scanner()
        >>> print scan.getAllProperties()
        """
        props = {}
        for prop in self.device.optlist:
            val = None
            if hasattr(self.device, prop):
                val = getattr(self.device, prop)
            props[prop] = val

        return props

    def printProperties(self):

        """
        **SUMMARY**

        Print detailed information about the SANE device properties
        **RETURNS**

        Nothing

        **EXAMPLES**
        >>> scan = Scanner()
        >>> scan.printProperties()
        """
        for prop in self.device.optlist:
            try:
                print self.device[prop]
            except:
                pass

    def getProperty(self, prop):
        """
        **SUMMARY**
        Returns a single property value from the SANE device
        equivalent to Scanner.device.PROPERTY

        **RETURNS**
        Value for option or None if missing/inactive

        **EXAMPLES**
        >>> scan = Scanner()
        >>> print scan.getProperty('mode')
        color
        """
        if hasattr(self.device, prop):
            return getattr(self.device, prop)
        return None


    def setROI(self, topleft = (0,0), bottomright = (-1,-1)):
        """
        **SUMMARY**
        Sets an ROI for the scanner in the current resolution.  The
        two parameters, topleft and bottomright, will default to the
        device extents, so the ROI can be reset by calling setROI with
        no parameters.

        The ROI is set by SANE in resolution independent units (default
        MM) so resolution can be changed after ROI has been set.

        **RETURNS**
        None

        **EXAMPLES**
        >>> scan = Scanner()
        >>> scan.setROI((50, 50), (100,100))
        >>> scan.getImage().show() # a very small crop on the scanner


        """
        self.device.tl_x = self.px2mm(topleft[0])
        self.device.tl_y = self.px2mm(topleft[1])
        if bottomright[0] == -1:
            self.device.br_x = self.max_x
        else:
            self.device.br_x = self.px2mm(bottomright[0])

        if bottomright[1] == -1:
            self.device.br_y = self.max_y
        else:
            self.device.br_y = self.px2mm(bottomright[1])

    def setProperty(self, prop, val):
        """
        **SUMMARY**
        Assigns a property value from the SANE device
        equivalent to Scanner.device.PROPERTY = VALUE

        **RETURNS**
        None

        **EXAMPLES**
        >>> scan = Scanner()
        >>> print scan.getProperty('mode')
        color
        >>> scan.setProperty("mode") = "gray"
        """
        setattr(self.device, prop, val)



    def px2mm(self, pixels = 1):
        """
        **SUMMARY**
        Helper function to convert native scanner resolution to millimeter units

        **RETURNS**
        Float value

        **EXAMPLES**
        >>> scan = Scanner()
        >>> scan.px2mm(scan.device.resolution) #return DPI in DPMM
        """
        return float(pixels * 25.4 / float(self.device.resolution))

class DigitalCamera(FrameSource):
    """
    **SUMMARY**

    The DigitalCamera takes a point-and-shoot camera or high-end slr and uses it as a Camera.  The current frame can always be accessed with getPreview()

    Requires the PiggyPhoto Library: https://github.com/alexdu/piggyphoto

    **EXAMPLE**

    >>> cam = DigitalCamera()
    >>> pre = cam.getPreview()
    >>> pre.findBlobs().show()
    >>>
    >>> img = cam.getImage()
    >>> img.show()

    """
    camera = None
    usbid = None
    device = None

    def __init__(self, id = 0):
        try:
            import piggyphoto
        except:
            warn("Initializing piggyphoto failed, do you have piggyphoto installed?")
            return

        devices = piggyphoto.cameraList(autodetect=True).toList()
        if not len(devices):
            warn("No compatible digital cameras attached")
            return

        self.device, self.usbid = devices[id]
        self.camera = piggyphoto.camera()

    def getImage(self):
        """
        **SUMMARY**

        Retrieve an Image-object from the camera with the highest quality possible.
        **RETURNS**

        A SimpleCV Image.

        **EXAMPLES**
        >>> cam = DigitalCamera()
        >>> cam.getImage().show()
        """
        fd, path = tempfile.mkstemp()
        self.camera.capture_image(path)
        img = Image(path)
        os.close(fd)
        os.remove(path)
        return img

    def getPreview(self):
        """
        **SUMMARY**

        Retrieve an Image-object from the camera with the preview quality from the camera.
        **RETURNS**

        A SimpleCV Image.

        **EXAMPLES**
        >>> cam = DigitalCamera()
        >>> cam.getPreview().show()
        """
        fd, path = tempfile.mkstemp()
        self.camera.capture_preview(path)
        img = Image(path)
        os.close(fd)
        os.remove(path)

        return img

class ScreenCamera():
    """
    **SUMMARY**
    ScreenCapture is a camera class would allow you to capture all or part of the screen and return it as a color image.

    Requires the pyscreenshot Library: https://github.com/vijaym123/pyscreenshot

    **EXAMPLE**
    >>> sc = ScreenCamera()
    >>> res = sc.getResolution()
    >>> print res
    >>>
    >>> img = sc.getImage()
    >>> img.show()
    """
    _roi = None

    def __init__(self):
        if not PYSCREENSHOT_ENABLED:
            warn("Initializing pyscreenshot failed. Install pyscreenshot from https://github.com/vijaym123/pyscreenshot")
            return None

    def getResolution(self):
        """
        **DESCRIPTION**

        returns the resolution of the screenshot of the screen.

        **PARAMETERS**
        None

        **RETURNS**
        returns the resolution.

        **EXAMPLE**

        >>> img = ScreenCamera()
        >>> res = img.getResolution()
        >>> print res
        """
        return Image(pyscreenshot.grab()).size()

    def setROI(self,roi):
        """
        **DESCRIPTION**
        To set the region of interest.

        **PARAMETERS**
        * *roi* - tuple - It is a tuple of size 4. where region of interest is to the center of the screen.

        **RETURNS**
        None

        **EXAMPLE**
        >>> sc = ScreenCamera()
        >>> res = sc.getResolution()
        >>> sc.setROI(res[0]/4,res[1]/4,res[0]/2,res[1]/2)
        >>> img = sc.getImage()
        >>> s.show()
        """
        if isinstance(roi,tuple) and len(roi)==4:
            self._roi = roi
        return

    def getImage(self):
        """
        **DESCRIPTION**

        getImage function returns a Image object capturing the current screenshot of the screen.

        **PARAMETERS**
        None

        **RETURNS**
        Returns the region of interest if setROI is used.
        else returns the original capture of the screenshot.

        **EXAMPLE**
        >>> sc = ScreenCamera()
        >>> img = sc.getImage()
        >>> img.show()
        """
        img = Image(pyscreenshot.grab())
        try :
            if self._roi :
                img = img.crop(self._roi,centered=True)
        except :
            print "Error croping the image. ROI specified is not correct."
            return None
        return img


class StereoImage:
    """
    **SUMMARY**

    This class is for binaculor Stereopsis. That is exactrating 3D information from two differing views of a scene(Image). By comparing the two images, the relative depth information can be obtained.

    - Fundamental Matrix : F : a 3 x 3 numpy matrix, is a relationship between any two images of the same scene that constrains where the projection of points from the scene can occur in both images. see : http://en.wikipedia.org/wiki/Fundamental_matrix_(computer_vision)

    - Homography Matrix : H : a 3 x 3 numpy matrix,

    - ptsLeft : The matched points on the left image.

    - ptsRight : The matched points on the right image.

    -findDisparityMap and findDepthMap - provides 3D information.

    for more information on stereo vision, visit : http://en.wikipedia.org/wiki/Computer_stereo_vision

    **EXAMPLE**
    >>> img1 = Image('sampleimages/stereo_view1.png')
    >>> img2 = Image('sampleimages/stereo_view2.png')
    >>> stereoImg = StereoImage(img1,img2)
    >>> stereoImg.findDisparityMap(method="BM",nDisparity=20).show()
    """
    def __init__( self, imgLeft , imgRight ):
        self.ImageLeft = imgLeft
        self.ImageRight = imgRight
        if self.ImageLeft.size() != self.ImageRight.size():
            logger.warning('Left and Right images should have the same size.')
            return None
        else:
            self.size = self.ImageLeft.size()

    def findFundamentalMat(self, thresh=500.00, minDist=0.15 ):
        """
        **SUMMARY**

        This method returns the fundamental matrix F such that (P_2).T F P_1 = 0

        **PARAMETERS**

        * *thresh* - The feature quality metric. This can be any value between about 300 and 500. Higher
          values should return fewer, but higher quality features.
        * *minDist* - The value below which the feature correspondence is considered a match. This
          is the distance between two feature vectors. Good values are between 0.05 and 0.3

        **RETURNS**
        Return None if it fails.
        * *F* -  Fundamental matrix as ndarray.
        * *matched_pts1* - the matched points (x, y) in img1
        * *matched_pts2* - the matched points (x, y) in img2

        **EXAMPLE**
        >>> img1 = Image("sampleimages/stereo_view1.png")
        >>> img2 = Image("sampleimages/stereo_view2.png")
        >>> stereoImg = StereoImage(img1,img2)
        >>> F,pts1,pts2 = stereoImg.findFundamentalMat()

        **NOTE**
        If you deal with the fundamental matrix F directly, be aware of (P_2).T F P_1 = 0
        where P_2 and P_1 consist of (y, x, 1)
        """

        (kpts1, desc1) = self.ImageLeft._getRawKeypoints(thresh)
        (kpts2, desc2) = self.ImageRight._getRawKeypoints(thresh)

        if desc1 == None or desc2 == None:
            logger.warning("We didn't get any descriptors. Image might be too uniform or blurry.")
            return None

        num_pts1 = desc1.shape[0]
        num_pts2 = desc2.shape[0]

        magic_ratio = 1.00
        if num_pts1 > num_pts2:
            magic_ratio = float(num_pts1) / float(num_pts2)

        (idx, dist) = Image()._getFLANNMatches(desc1, desc2)
        p = dist.squeeze()
        result = p * magic_ratio < minDist

        try:
            import cv2
        except:
            logger.warning("Can't use fundamental matrix without OpenCV >= 2.3.0")
            return None

        pts1 = np.array([kpt.pt for kpt in kpts1])
        pts2 = np.array([kpt.pt for kpt in kpts2])

        matched_pts1 = pts1[idx[result]].squeeze()
        matched_pts2 = pts2[result]
        (F, mask) = cv2.findFundamentalMat(matched_pts1, matched_pts2, method=cv.CV_FM_LMEDS)

        inlier_ind = mask.nonzero()[0]
        matched_pts1 = matched_pts1[inlier_ind, :]
        matched_pts2 = matched_pts2[inlier_ind, :]

        matched_pts1 = matched_pts1[:, ::-1.00]
        matched_pts2 = matched_pts2[:, ::-1.00]
        return (F, matched_pts1, matched_pts2)

    def findHomography( self, thresh=500.00, minDist=0.15):
        """
        **SUMMARY**

        This method returns the homography H such that P2 ~ H P1

        **PARAMETERS**

        * *thresh* - The feature quality metric. This can be any value between about 300 and 500. Higher
          values should return fewer, but higher quality features.
        * *minDist* - The value below which the feature correspondence is considered a match. This
          is the distance between two feature vectors. Good values are between 0.05 and 0.3

        **RETURNS**

        Return None if it fails.
        * *H* -  homography as ndarray.
        * *matched_pts1* - the matched points (x, y) in img1
        * *matched_pts2* - the matched points (x, y) in img2

        **EXAMPLE**
        >>> img1 = Image("sampleimages/stereo_view1.png")
        >>> img2 = Image("sampleimages/stereo_view2.png")
        >>> stereoImg = StereoImage(img1,img2)
        >>> H,pts1,pts2 = stereoImg.findHomography()

        **NOTE**
        If you deal with the homography H directly, be aware of P2 ~ H P1
        where P2 and P1 consist of (y, x, 1)
        """

        (kpts1, desc1) = self.ImageLeft._getRawKeypoints(thresh)
        (kpts2, desc2) = self.ImageRight._getRawKeypoints(thresh)

        if desc1 == None or desc2 == None:
            logger.warning("We didn't get any descriptors. Image might be too uniform or blurry.")
            return None

        num_pts1 = desc1.shape[0]
        num_pts2 = desc2.shape[0]

        magic_ratio = 1.00
        if num_pts1 > num_pts2:
            magic_ratio = float(num_pts1) / float(num_pts2)

        (idx, dist) = Image()._getFLANNMatches(desc1, desc2)
        p = dist.squeeze()
        result = p * magic_ratio < minDist

        try:
            import cv2
        except:
            logger.warning("Can't use homography without OpenCV >= 2.3.0")
            return None

        pts1 = np.array([kpt.pt for kpt in kpts1])
        pts2 = np.array([kpt.pt for kpt in kpts2])

        matched_pts1 = pts1[idx[result]].squeeze()
        matched_pts2 = pts2[result]

        (H, mask) = cv2.findHomography(matched_pts1, matched_pts2,
                method=cv.CV_LMEDS)

        inlier_ind = mask.nonzero()[0]
        matched_pts1 = matched_pts1[inlier_ind, :]
        matched_pts2 = matched_pts2[inlier_ind, :]

        matched_pts1 = matched_pts1[:, ::-1.00]
        matched_pts2 = matched_pts2[:, ::-1.00]
        return (H, matched_pts1, matched_pts2)

    def findDisparityMap( self, nDisparity=16 ,method='BM'):
        """
        The method generates disparity map from set of stereo images.

        **PARAMETERS**

        * *method* :
                 *BM* - Block Matching algorithm, this is a real time algorithm.
                 *SGBM* - Semi Global Block Matching algorithm, this is not a real time algorithm.
                 *GC* - Graph Cut algorithm, This is not a real time algorithm.

        * *nDisparity* - Maximum disparity value. This should be multiple of 16
        * *scale* - Scale factor

        **RETURNS**

        Return None if it fails.
        Returns Disparity Map Image

        **EXAMPLE**
        >>> img1 = Image("sampleimages/stereo_view1.png")
        >>> img2 = Image("sampleimages/stereo_view2.png")
        >>> stereoImg = StereoImage(img1,img2)
        >>> disp = stereoImg.findDisparityMap(method="BM")
        """
        gray_left = self.ImageLeft.getGrayscaleMatrix()
        gray_right = self.ImageRight.getGrayscaleMatrix()
        (r, c) = self.size
        scale = int(self.ImageLeft.depth)
        if nDisparity % 16 !=0 :
            if nDisparity < 16 :
                nDisparity = 16
            nDisparity = (nDisparity/16)*16
        try :
            if method == 'BM':
                disparity = cv.CreateMat(c, r, cv.CV_32F)
                state = cv.CreateStereoBMState()
                state.SADWindowSize = 41
                state.preFilterType = 1
                state.preFilterSize = 41
                state.preFilterCap = 31
                state.minDisparity = -8
                state.numberOfDisparities = nDisparity
                state.textureThreshold = 10
                #state.speckleRange = 32
                #state.speckleWindowSize = 100
                state.uniquenessRatio=15
                cv.FindStereoCorrespondenceBM(gray_left, gray_right, disparity, state)
                disparity_visual = cv.CreateMat(c, r, cv.CV_8U)
                cv.Normalize( disparity, disparity_visual, 0, 256, cv.CV_MINMAX )
                disparity_visual = Image(disparity_visual)
                return Image(disparity_visual.getBitmap(),colorSpace=ColorSpace.GRAY)

            elif method == 'GC':
                disparity_left = cv.CreateMat(c, r, cv.CV_32F)
                disparity_right = cv.CreateMat(c, r, cv.CV_32F)
                state = cv.CreateStereoGCState(nDisparity, 8)
                state.minDisparity = -8
                cv.FindStereoCorrespondenceGC( gray_left, gray_right, disparity_left, disparity_right, state, 0)
                disparity_left_visual = cv.CreateMat(c, r, cv.CV_8U)
                cv.Normalize( disparity_left, disparity_left_visual, 0, 256, cv.CV_MINMAX )
                #cv.Scale(disparity_left, disparity_left_visual, -scale)
                disparity_left_visual = Image(disparity_left_visual)
                return Image(disparity_left_visual.getBitmap(),colorSpace=ColorSpace.GRAY)

            elif method == 'SGBM':
                try:
                    import cv2
                    ver = cv2.__version__
                    if ver.startswith("$Rev :"):
                        logger.warning("Can't use SGBM without OpenCV >= 2.4.0")
                        return None
                except:
                    logger.warning("Can't use SGBM without OpenCV >= 2.4.0")
                    return None
                state = cv2.StereoSGBM()
                state.SADWindowSize = 41
                state.preFilterCap = 31
                state.minDisparity = 0
                state.numberOfDisparities = nDisparity
                #state.speckleRange = 32
                #state.speckleWindowSize = 100
                state.disp12MaxDiff = 1
                state.fullDP=False
                state.P1 = 8 * 1 * 41 * 41
                state.P2 = 32 * 1 * 41 * 41
                state.uniquenessRatio=15
                disparity=state.compute(self.ImageLeft.getGrayNumpy(),self.ImageRight.getGrayNumpy())
                return Image(disparity)

            else :
                logger.warning("Unknown method. Choose one method amoung BM or SGBM or GC !")
                return None

        except :
            logger.warning("Error in computing the Disparity Map, may be due to the Images are stereo in nature.")
            return None

    def Eline (self, point, F, whichImage):
        """
        **SUMMARY**

        This method returns, line feature object.

        **PARAMETERS**

        * *point* - Input point (x, y)
        * *F* - Fundamental matrix.
        * *whichImage* - Index of the image (1 or 2) that contains the point

        **RETURNS**

        epipolar line, in the form of line feature object.

        **EXAMPLE**

        >>> img1 = Image("sampleimages/stereo_view1.png")
        >>> img2 = Image("sampleimages/stereo_view2.png")
        >>> stereoImg = StereoImage(img1,img2)
        >>> F,pts1,pts2 = stereoImg.findFundamentalMat()
        >>> point = pts2[0]
        >>> epiline = mapper.Eline(point,F, 1) #find corresponding Epipolar line in the left image.
        """

        from SimpleCV.Features.Detection import Line

        pts1 = (0,0)
        pts2 = self.size
        pt_cvmat = cv.CreateMat(1, 1, cv.CV_32FC2)
        pt_cvmat[0, 0] = (point[1], point[0])  # OpenCV seems to use (y, x) coordinate.
        line = cv.CreateMat(1, 1, cv.CV_32FC3)
        cv.ComputeCorrespondEpilines(pt_cvmat, whichImage, npArray2cvMat(F), line)
        line_npArray = np.array(line).squeeze()
        line_npArray = line_npArray[[1.00, 0, 2]]
        pts1 = (pts1[0],(-line_npArray[2]-line_npArray[0]*pts1[0])/line_npArray[1] )
        pts2 = (pts2[0],(-line_npArray[2]-line_npArray[0]*pts2[0])/line_npArray[1] )
        if whichImage == 1 :
            return Line(self.ImageLeft, [pts1,pts2])
        elif whichImage == 2 :
            return Line(self.ImageRight, [pts1,pts2])

    def projectPoint( self, point, H ,whichImage):
        """
        **SUMMARY**

        This method returns the corresponding point (x, y)

        **PARAMETERS**

        * *point* - Input point (x, y)
        * *whichImage* - Index of the image (1 or 2) that contains the point
        * *H* - Homography that can be estimated
                using StereoCamera.findHomography()

        **RETURNS**

        Corresponding point (x, y) as tuple

        **EXAMPLE**

        >>> img1 = Image("sampleimages/stereo_view1.png")
        >>> img2 = Image("sampleimages/stereo_view2.png")
        >>> stereoImg = StereoImage(img1,img2)
        >>> F,pts1,pts2 = stereoImg.findFundamentalMat()
        >>> point = pts2[0]
        >>> projectPoint = stereoImg.projectPoint(point,H ,1) #finds corresponding  point in the left image.
        """

        H = np.matrix(H)
        point = np.matrix((point[1], point[0],1.00))
        if whichImage == 1.00:
            corres_pt = H * point.T
        else:
            corres_pt = np.linalg.inv(H) * point.T
        corres_pt = corres_pt / corres_pt[2]
        return (float(corres_pt[1]), float(corres_pt[0]))

    def get3DImage(self, Q, method="BM", state=None):
        """
        **SUMMARY**

        This method returns the 3D depth image using reprojectImageTo3D method.

        **PARAMETERS**

        * *Q* - reprojection Matrix (disparity to depth matrix)
        * *method* - Stereo Correspondonce method to be used.
                   - "BM" - Stereo BM
                   - "SGBM" - Stereo SGBM
        * *state* - dictionary corresponding to parameters of
                    stereo correspondonce.
                    SADWindowSize - odd int
                    nDisparity - int
                    minDisparity  - int
                    preFilterCap - int
                    preFilterType - int (only BM)
                    speckleRange - int
                    speckleWindowSize - int
                    P1 - int (only SGBM)
                    P2 - int (only SGBM)
                    fullDP - Bool (only SGBM)
                    uniquenessRatio - int
                    textureThreshold - int (only BM)

        **RETURNS**

        SimpleCV.Image representing 3D depth Image
        also StereoImage.Image3D gives OpenCV 3D Depth Image of CV_32F type.

        **EXAMPLE**

        >>> lImage = Image("l.jpg")
        >>> rImage = Image("r.jpg")
        >>> stereo = StereoImage(lImage, rImage)
        >>> Q = cv.Load("Q.yml")
        >>> stereo.get3DImage(Q).show()

        >>> state = {"SADWindowSize":9, "nDisparity":112, "minDisparity":-39}
        >>> stereo.get3DImage(Q, "BM", state).show()
        >>> stereo.get3DImage(Q, "SGBM", state).show()
        """
        imgLeft = self.ImageLeft
        imgRight = self.ImageRight
        cv2flag = True
        try:
            import cv2
        except ImportError:
            cv2flag = False
        import cv2.cv as cv
        (r, c) = self.size
        if method == "BM":
            sbm = cv.CreateStereoBMState()
            disparity = cv.CreateMat(c, r, cv.CV_32F)
            if state:
                SADWindowSize = state.get("SADWindowSize")
                preFilterCap = state.get("preFilterCap")
                minDisparity = state.get("minDisparity")
                numberOfDisparities = state.get("nDisparity")
                uniquenessRatio = state.get("uniquenessRatio")
                speckleRange = state.get("speckleRange")
                speckleWindowSize = state.get("speckleWindowSize")
                textureThreshold = state.get("textureThreshold")
                speckleRange = state.get("speckleRange")
                speckleWindowSize = state.get("speckleWindowSize")
                preFilterType = state.get("perFilterType")

                if SADWindowSize is not None:
                    sbm.SADWindowSize = SADWindowSize
                if preFilterCap is not None:
                    sbm.preFilterCap = preFilterCap
                if minDisparity is not None:
                    sbm.minDisparity = minDisparity
                if numberOfDisparities is not None:
                    sbm.numberOfDisparities = numberOfDisparities
                if uniquenessRatio is not None:
                    sbm.uniquenessRatio = uniquenessRatio
                if speckleRange is not None:
                    sbm.speckleRange = speckleRange
                if speckleWindowSize is not None:
                    sbm.speckleWindowSize = speckleWindowSize
                if textureThreshold is not None:
                    sbm.textureThreshold = textureThreshold
                if preFilterType is not None:
                    sbm.preFilterType = preFilterType
            else:
                sbm.SADWindowSize = 9
                sbm.preFilterType = 1
                sbm.preFilterSize = 5
                sbm.preFilterCap = 61
                sbm.minDisparity = -39
                sbm.numberOfDisparities = 112
                sbm.textureThreshold = 507
                sbm.uniquenessRatio= 0
                sbm.speckleRange = 8
                sbm.speckleWindowSize = 0

            gray_left = imgLeft.getGrayscaleMatrix()
            gray_right = imgRight.getGrayscaleMatrix()
            cv.FindStereoCorrespondenceBM(gray_left, gray_right, disparity, sbm)
            disparity_visual = cv.CreateMat(c, r, cv.CV_8U)

        elif method == "SGBM":
            if not cv2flag:
                warnings.warn("Can't Use SGBM without OpenCV >= 2.4. Use SBM instead.")
            sbm = cv2.StereoSGBM()
            if state:
                SADWindowSize = state.get("SADWindowSize")
                preFilterCap = state.get("preFilterCap")
                minDisparity = state.get("minDisparity")
                numberOfDisparities = state.get("nDisparity")
                P1 = state.get("P1")
                P2 = state.get("P2")
                uniquenessRatio = state.get("uniquenessRatio")
                speckleRange = state.get("speckleRange")
                speckleWindowSize = state.get("speckleWindowSize")
                fullDP = state.get("fullDP")

                if SADWindowSize is not None:
                    sbm.SADWindowSize = SADWindowSize
                if preFilterCap is not None:
                    sbm.preFilterCap = preFilterCap
                if minDisparity is not None:
                    sbm.minDisparity = minDisparity
                if numberOfDisparities is not None:
                    sbm.numberOfDisparities = numberOfDisparities
                if P1 is not None:
                    sbm.P1 = P1
                if P2 is not None:
                    sbm.P2 = P2
                if uniquenessRatio is not None:
                    sbm.uniquenessRatio = uniquenessRatio
                if speckleRange is not None:
                    sbm.speckleRange = speckleRange
                if speckleWindowSize is not None:
                    sbm.speckleWindowSize = speckleWindowSize
                if fullDP is not None:
                    sbm.fullDP = fullDP
            else:
                sbm.SADWindowSize = 9;
                sbm.numberOfDisparities = 96;
                sbm.preFilterCap = 63;
                sbm.minDisparity = -21;
                sbm.uniquenessRatio = 7;
                sbm.speckleWindowSize = 0;
                sbm.speckleRange = 8;
                sbm.disp12MaxDiff = 1;
                sbm.fullDP = False;

            disparity = sbm.compute(imgLeft.getGrayNumpyCv2(), imgRight.getGrayNumpyCv2())
            
        else:
            warnings.warn("Unknown method. Returning None")
            return None

        if cv2flag:
            if not isinstance(Q, np.ndarray):
                Q = np.array(Q)
            if not isinstance(disparity, np.ndarray):
                disparity = np.array(disparity)
            Image3D = cv2.reprojectImageTo3D(disparity, Q, ddepth=cv2.cv.CV_32F)
            Image3D_normalize = cv2.normalize(Image3D, alpha=0, beta=255, norm_type=cv2.cv.CV_MINMAX, dtype=cv2.cv.CV_8UC3)
            retVal = Image(Image3D_normalize, cv2image=True)
        else:
            Image3D = cv.CreateMat(self.LeftImage.size()[1], self.LeftImage.size()[0], cv2.cv.CV_32FC3)
            Image3D_normalize = cv.CreateMat(self.LeftImage.size()[1], self.LeftImage.size()[0], cv2.cv.CV_8UC3)
            cv.ReprojectImageTo3D(disparity, Image3D, Q)
            cv.Normalize(Image3D, Image3D_normalize, 0, 255, cv.CV_MINMAX, CV_8UC3)
            retVal = Image(Image3D_normalize)
        self.Image3D = Image3D
        return retVal

    def get3DImageFromDisparity(self, disparity, Q):
        """
        **SUMMARY**

        This method returns the 3D depth image using reprojectImageTo3D method.

        **PARAMETERS**
        * *disparity* - Disparity Image
        * *Q* - reprojection Matrix (disparity to depth matrix)

        **RETURNS**

        SimpleCV.Image representing 3D depth Image
        also StereoCamera.Image3D gives OpenCV 3D Depth Image of CV_32F type.

        **EXAMPLE**

        >>> lImage = Image("l.jpg")
        >>> rImage = Image("r.jpg")
        >>> stereo = StereoCamera()
        >>> Q = cv.Load("Q.yml")
        >>> disp = stereo.findDisparityMap()
        >>> stereo.get3DImageFromDisparity(disp, Q)
        """
        cv2flag = True
        try:
            import cv2
        except ImportError:
            cv2flag = False
            import cv2.cv as cv

        if cv2flag:
            if not isinstance(Q, np.ndarray):
                Q = np.array(Q)
            disparity = disparity.getNumpyCv2()    
            Image3D = cv2.reprojectImageTo3D(disparity, Q, ddepth=cv2.cv.CV_32F)
            Image3D_normalize = cv2.normalize(Image3D, alpha=0, beta=255, norm_type=cv2.cv.CV_MINMAX, dtype=cv2.cv.CV_8UC3)
            retVal = Image(Image3D_normalize, cv2image=True)
        else:
            disparity = disparity.getMatrix()
            Image3D = cv.CreateMat(self.LeftImage.size()[1], self.LeftImage.size()[0], cv2.cv.CV_32FC3)
            Image3D_normalize = cv.CreateMat(self.LeftImage.size()[1], self.LeftImage.size()[0], cv2.cv.CV_8UC3)
            cv.ReprojectImageTo3D(disparity, Image3D, Q)
            cv.Normalize(Image3D, Image3D_normalize, 0, 255, cv.CV_MINMAX, CV_8UC3)
            retVal = Image(Image3D_normalize)
        self.Image3D = Image3D
        return retVal
        

class StereoCamera :
    """
    Stereo Camera is a class dedicated for calibration stereo camera. It also has functionalites for
    rectification and getting undistorted Images.

    This class can be used to calculate various parameters related to both the camera's :
      -> Camera Matrix
      -> Distortion coefficients
      -> Rotation and Translation matrix
      -> Rectification transform (rotation matrix)
      -> Projection matrix in the new (rectified) coordinate systems
      -> Disparity-to-depth mapping matrix (Q)
    """
    def __init__(self):
        return

    def stereoCalibration(self,camLeft, camRight, nboards=30, chessboard=(8, 5), gridsize=0.027, WinSize = (352,288)):
        """
        
        **SUMMARY**
        
        Stereo Calibration is a way in which you obtain the parameters that will allow you to calculate 3D information of the scene.
        Once both the camera's are initialized.
        Press [Space] once chessboard is identified in both the camera's.
        Press [esc] key to exit the calibration process.

        **PARAMETERS**
        
        * camLeft - Left camera index.
        * camRight - Right camera index.
        * nboards - Number of samples or multiple views of the chessboard in different positions and orientations with your stereo camera.
        * chessboard - A tuple of Cols, Rows in the chessboard (used for calibration).
        * gridsize - chessboard grid size in real units
        * WinSize - This is the window resolution.

        **RETURNS**
        
        A tuple of the form (CM1, CM2, D1, D2, R, T, E, F) on success
        CM1 - Camera Matrix for left camera,
        CM2 - Camera Matrix for right camera,
        D1 - Vector of distortion coefficients for left camera,
        D2 - Vector of distortion coefficients for right camera,
        R - Rotation matrix between the left and the right camera coordinate systems,
        T - Translation vector between the left and the right coordinate systems of the cameras,
        E - Essential matrix,
        F - Fundamental matrix

        **EXAMPLE**
        
        >>> StereoCam = StereoCamera()
        >>> calibration = StereoCam.StereoCalibration(1,2,nboards=40)

        **Note**
        
        Press space to capture the images.
        
        """
        count = 0
        n1="Left"
        n2="Right"
        try :
            captureLeft = cv.CaptureFromCAM(camLeft)
            cv.SetCaptureProperty(captureLeft, cv.CV_CAP_PROP_FRAME_WIDTH, WinSize[0])
            cv.SetCaptureProperty(captureLeft, cv.CV_CAP_PROP_FRAME_HEIGHT, WinSize[1])
            frameLeft = cv.QueryFrame(captureLeft)
            cv.FindChessboardCorners(frameLeft, (chessboard))

            captureRight = cv.CaptureFromCAM(camRight)
            cv.SetCaptureProperty(captureRight, cv.CV_CAP_PROP_FRAME_WIDTH, WinSize[0])
            cv.SetCaptureProperty(captureRight, cv.CV_CAP_PROP_FRAME_HEIGHT, WinSize[1])
            frameRight = cv.QueryFrame(captureRight)
            cv.FindChessboardCorners(frameRight, (chessboard))
        except :
            print "Error Initialising the Left and Right camera"
            return None

        imagePoints1 = cv.CreateMat(1, nboards * chessboard[0] * chessboard[1], cv.CV_64FC2)
        imagePoints2 = cv.CreateMat(1, nboards * chessboard[0] * chessboard[1], cv.CV_64FC2)

        objectPoints = cv.CreateMat(1, chessboard[0] * chessboard[1] * nboards, cv.CV_64FC3)
        nPoints = cv.CreateMat(1, nboards, cv.CV_32S)

        # the intrinsic camera matrices
        CM1 = cv.CreateMat(3, 3, cv.CV_64F)
        CM2 = cv.CreateMat(3, 3, cv.CV_64F)

        # the distortion coefficients of both cameras
        D1 = cv.CreateMat(1, 5, cv.CV_64F)
        D2 = cv.CreateMat(1, 5, cv.CV_64F)

        # matrices governing the rotation and translation from camera 1 to camera 2
        R = cv.CreateMat(3, 3, cv.CV_64F)
        T = cv.CreateMat(3, 1, cv.CV_64F)

        # the essential and fundamental matrices
        E = cv.CreateMat(3, 3, cv.CV_64F)
        F = cv.CreateMat(3, 3, cv.CV_64F)

        while True:
            frameLeft = cv.QueryFrame(captureLeft)
            cv.Flip(frameLeft, frameLeft, 1)
            frameRight = cv.QueryFrame(captureRight)
            cv.Flip(frameRight, frameRight, 1)
            k = cv.WaitKey(3)

            cor1 = cv.FindChessboardCorners(frameLeft, (chessboard))
            if cor1[0] :
                cv.DrawChessboardCorners(frameLeft, (chessboard), cor1[1], cor1[0])
                cv.ShowImage(n1, frameLeft)

            cor2 = cv.FindChessboardCorners(frameRight, (chessboard))
            if cor2[0]:
                cv.DrawChessboardCorners(frameRight, (chessboard), cor2[1], cor2[0])
                cv.ShowImage(n2, frameRight)

            if cor1[0] and cor2[0] and k==0x20:
                print count
                for i in range(0, len(cor1[1])):
                    cv.Set1D(imagePoints1, count * chessboard[0] * chessboard[1] + i, cv.Scalar(cor1[1][i][0], cor1[1][i][1]))
                    cv.Set1D(imagePoints2, count * chessboard[0] * chessboard[1] + i, cv.Scalar(cor2[1][i][0], cor2[1][i][1]))

                count += 1

                if count == nboards:
                    cv.DestroyAllWindows()
                    for i in range(nboards):
                        for j in range(chessboard[1]):
                            for k in range(chessboard[0]):
                                cv.Set1D(objectPoints, i * chessboard[1] * chessboard[0] + j * chessboard[0] + k, (k * gridsize, j * gridsize, 0))

                    for i in range(nboards):
                        cv.Set1D(nPoints, i, chessboard[0] * chessboard[1])


                    cv.SetIdentity(CM1)
                    cv.SetIdentity(CM2)
                    cv.Zero(D1)
                    cv.Zero(D2)

                    print "Running stereo calibration..."
                    del(camLeft)
                    del(camRight)
                    cv.StereoCalibrate(objectPoints, imagePoints1, imagePoints2, nPoints, CM1, D1, CM2, D2, WinSize, R, T, E, F,
                                      flags=cv.CV_CALIB_SAME_FOCAL_LENGTH | cv.CV_CALIB_ZERO_TANGENT_DIST)

                    print "Done."
                    return (CM1, CM2, D1, D2, R, T, E, F)

            cv.ShowImage(n1, frameLeft)
            cv.ShowImage(n2, frameRight)
            if k == 0x1b:
                print "ESC pressed. Exiting. WARNING: NOT ENOUGH CHESSBOARDS FOUND YET"
                cv.DestroyAllWindows()
                break

    def saveCalibration(self,calibration=None, fname="Stereo",cdir="."):
        """
        
        **SUMMARY**
        
        saveCalibration is a method to save the StereoCalibration parameters such as CM1, CM2, D1, D2, R, T, E, F of stereo pair.
        This method returns True on success and saves the calibration in the following format.
        StereoCM1.txt
        StereoCM2.txt
        StereoD1.txt
        StereoD2.txt
        StereoR.txt
        StereoT.txt
        StereoE.txt
        StereoF.txt
        
        **PARAMETERS**
        
        calibration - is a tuple os the form (CM1, CM2, D1, D2, R, T, E, F)
        CM1 -> Camera Matrix for left camera,
        CM2 -> Camera Matrix for right camera,
        D1 -> Vector of distortion coefficients for left camera,
        D2 -> Vector of distortion coefficients for right camera,
        R -> Rotation matrix between the left and the right camera coordinate systems,
        T -> Translation vector between the left and the right coordinate systems of the cameras,
        E -> Essential matrix,
        F -> Fundamental matrix


        **RETURNS**
        
        return True on success and saves the calibration files.

        **EXAMPLE**
        
        >>> StereoCam = StereoCamera()
        >>> calibration = StereoCam.StereoCalibration(1,2,nboards=40)
        >>> StereoCam.saveCalibration(calibration,fname="Stereo1")
        """
        filenames = (fname+"CM1.txt", fname+"CM2.txt", fname+"D1.txt", fname+"D2.txt", fname+"R.txt", fname+"T.txt", fname+"E.txt", fname+"F.txt")
        try :
            (CM1, CM2, D1, D2, R, T, E, F) = calibration
            cv.Save("{0}/{1}".format(cdir, filenames[0]), CM1)
            cv.Save("{0}/{1}".format(cdir, filenames[1]), CM2)
            cv.Save("{0}/{1}".format(cdir, filenames[2]), D1)
            cv.Save("{0}/{1}".format(cdir, filenames[3]), D2)
            cv.Save("{0}/{1}".format(cdir, filenames[4]), R)
            cv.Save("{0}/{1}".format(cdir, filenames[5]), T)
            cv.Save("{0}/{1}".format(cdir, filenames[6]), E)
            cv.Save("{0}/{1}".format(cdir, filenames[7]), F)
            print "Calibration parameters written to directory '{0}'.".format(cdir)
            return True

        except :
            return False

    def loadCalibration(self,fname="Stereo",dir="."):
        """
        
        **SUMMARY**
        
        loadCalibration is a method to load the StereoCalibration parameters such as CM1, CM2, D1, D2, R, T, E, F of stereo pair.
        This method loads from calibration files and return calibration on success else return false.
        
        **PARAMETERS**
        
        fname - is the prefix of the calibration files.
        dir - is the directory in which files are present.
        
        **RETURNS**
        
        a tuple of the form (CM1, CM2, D1, D2, R, T, E, F) on success.
        CM1 - Camera Matrix for left camera
        CM2 - Camera Matrix for right camera
        D1 - Vector of distortion coefficients for left camera
        D2 - Vector of distortion coefficients for right camera
        R - Rotation matrix between the left and the right camera coordinate systems
        T - Translation vector between the left and the right coordinate systems of the cameras
        E - Essential matrix
        F - Fundamental matrix
        else returns false
        
        **EXAMPLE**
        
        >>> StereoCam = StereoCamera()
        >>> loadedCalibration = StereoCam.loadCalibration(fname="Stereo1")
        
        """
        filenames = (fname+"CM1.txt", fname+"CM2.txt", fname+"D1.txt", fname+"D2.txt", fname+"R.txt", fname+"T.txt", fname+"E.txt", fname+"F.txt")
        try :
            CM1 = cv.Load("{0}/{1}".format(dir, filenames[0]))
            CM2 = cv.Load("{0}/{1}".format(dir, filenames[1]))
            D1 = cv.Load("{0}/{1}".format(dir, filenames[2]))
            D2 = cv.Load("{0}/{1}".format(dir, filenames[3]))
            R = cv.Load("{0}/{1}".format(dir, filenames[4]))
            T = cv.Load("{0}/{1}".format(dir, filenames[5]))
            E = cv.Load("{0}/{1}".format(dir, filenames[6]))
            F = cv.Load("{0}/{1}".format(dir, filenames[7]))
            print "Calibration files loaded from dir '{0}'.".format(dir)
            return (CM1, CM2, D1, D2, R, T, E, F)

        except :
            return False

    def stereoRectify(self,calib=None,WinSize=(352,288)):
        """
        
        **SUMMARY**
        
        Computes rectification transforms for each head of a calibrated stereo camera.
        
        **PARAMETERS**
        
        calibration - is a tuple os the form (CM1, CM2, D1, D2, R, T, E, F)
        CM1 - Camera Matrix for left camera,
        CM2 - Camera Matrix for right camera,
        D1 - Vector of distortion coefficients for left camera,
        D2 - Vector of distortion coefficients for right camera,
        R - Rotation matrix between the left and the right camera coordinate systems,
        T - Translation vector between the left and the right coordinate systems of the cameras,
        E - Essential matrix,
        F - Fundamental matrix
        
        **RETURNS**
        
        On success returns a a tuple of the format -> (R1, R2, P1, P2, Q, roi)
        R1 - Rectification transform (rotation matrix) for the left camera.
        R2 - Rectification transform (rotation matrix) for the right camera.
        P1 - Projection matrix in the new (rectified) coordinate systems for the left camera.
        P2 - Projection matrix in the new (rectified) coordinate systems for the right camera.
        Q - disparity-to-depth mapping matrix.
        
        **EXAMPLE**
        
        >>> StereoCam = StereoCamera()
        >>> calibration = StereoCam.loadCalibration(fname="Stereo1")
        >>> rectification = StereoCam.stereoRectify(calibration)
        
        """
        (CM1, CM2, D1, D2, R, T, E, F) = calib
        R1 = cv.CreateMat(3, 3, cv.CV_64F)
        R2 = cv.CreateMat(3, 3, cv.CV_64F)
        P1 = cv.CreateMat(3, 4, cv.CV_64F)
        P2 = cv.CreateMat(3, 4, cv.CV_64F)
        Q = cv.CreateMat(4, 4, cv.CV_64F)
        
        print "Running stereo rectification..."
        
        (leftroi, rightroi) = cv.StereoRectify(CM1, CM2, D1, D2, WinSize, R, T, R1, R2, P1, P2, Q)
        roi = []
        roi.append(max(leftroi[0], rightroi[0]))
        roi.append(max(leftroi[1], rightroi[1]))
        roi.append(min(leftroi[2], rightroi[2]))
        roi.append(min(leftroi[3], rightroi[3]))
        print "Done."
        return (R1, R2, P1, P2, Q, roi)

    def getImagesUndistort(self,imgLeft, imgRight, calibration, rectification, WinSize=(352,288)):
        """
        **SUMMARY**
        Rectify two images from the calibration and rectification parameters.

        **PARAMETERS**
        * *imgLeft* - Image captured from left camera and needs to be rectified.
        * *imgRight* - Image captures from right camera and need to be rectified.
        * *calibration* - A calibration tuple of the format (CM1, CM2, D1, D2, R, T, E, F)
        * *rectification* - A rectification tuple of the format (R1, R2, P1, P2, Q, roi)

        **RETURNS**
        returns rectified images in a tuple -> (imgLeft,imgRight)
        >>> StereoCam = StereoCamera()
        >>> calibration = StereoCam.loadCalibration(fname="Stereo1")
        >>> rectification = StereoCam.stereoRectify(loadedCalibration)
        >>> imgLeft = camLeft.getImage()
        >>> imgRight = camRight.getImage()
        >>> rectLeft,rectRight = StereoCam.getImagesUndistort(imgLeft,imgRight,calibration,rectification)
        """
        imgLeft = imgLeft.getMatrix()
        imgRight = imgRight.getMatrix()
        (CM1, CM2, D1, D2, R, T, E, F) = calibration
        (R1, R2, P1, P2, Q, roi) = rectification

        dst1 = cv.CloneMat(imgLeft)
        dst2 = cv.CloneMat(imgRight)
        map1x = cv.CreateMat(WinSize[1], WinSize[0], cv.CV_32FC1)
        map2x = cv.CreateMat(WinSize[1], WinSize[0], cv.CV_32FC1)
        map1y = cv.CreateMat(WinSize[1], WinSize[0], cv.CV_32FC1)
        map2y = cv.CreateMat(WinSize[1], WinSize[0], cv.CV_32FC1)

        #print "Rectifying images..."
        cv.InitUndistortRectifyMap(CM1, D1, R1, P1, map1x, map1y)
        cv.InitUndistortRectifyMap(CM2, D2, R2, P2, map2x, map2y)

        cv.Remap(imgLeft, dst1, map1x, map1y)
        cv.Remap(imgRight, dst2, map2x, map2y)
        return Image(dst1), Image(dst2)

    def get3DImage(self, leftIndex, rightIndex, Q, method="BM", state=None):
        """
        **SUMMARY**

        This method returns the 3D depth image using reprojectImageTo3D method.

        **PARAMETERS**
        
        * *leftIndex* - Index of left camera
        * *rightIndex* - Index of right camera
        * *Q* - reprojection Matrix (disparity to depth matrix)
        * *method* - Stereo Correspondonce method to be used.
                   - "BM" - Stereo BM
                   - "SGBM" - Stereo SGBM
        * *state* - dictionary corresponding to parameters of
                    stereo correspondonce.
                    SADWindowSize - odd int
                    nDisparity - int
                    minDisparity  - int
                    preFilterCap - int
                    preFilterType - int (only BM)
                    speckleRange - int
                    speckleWindowSize - int
                    P1 - int (only SGBM)
                    P2 - int (only SGBM)
                    fullDP - Bool (only SGBM)
                    uniquenessRatio - int
                    textureThreshold - int (only BM)
                    

        **RETURNS**

        SimpleCV.Image representing 3D depth Image
        also StereoCamera.Image3D gives OpenCV 3D Depth Image of CV_32F type.

        **EXAMPLE**

        >>> lImage = Image("l.jpg")
        >>> rImage = Image("r.jpg")
        >>> stereo = StereoCamera()
        >>> Q = cv.Load("Q.yml")
        >>> stereo.get3DImage(1, 2, Q).show()

        >>> state = {"SADWindowSize":9, "nDisparity":112, "minDisparity":-39}
        >>> stereo.get3DImage(1, 2, Q, "BM", state).show()
        >>> stereo.get3DImage(1, 2, Q, "SGBM", state).show()
        """
        cv2flag = True
        try:
            import cv2
        except ImportError:
            cv2flag = False
            import cv2.cv as cv
        if cv2flag:
            camLeft = cv2.VideoCapture(leftIndex)
            camRight = cv2.VideoCapture(rightIndex)
            if camLeft.isOpened():
                _, imgLeft = camLeft.read()
            else:
                warnings.warn("Unable to open left camera")
                return None
            if camRight.isOpened():
                _, imgRight = camRight.read()
            else:
                warnings.warn("Unable to open right camera")
                return None
            imgLeft = Image(imgLeft, cv2image=True)
            imgRight = Image(imgRight, cv2image=True)
        else:
            camLeft = cv.CaptureFromCAM(leftIndex)
            camRight = cv.CaptureFromCAM(rightIndex)
            imgLeft = cv.QueryFrame(camLeft)
            if imgLeft is None:
                warnings.warn("Unable to open left camera")
                return None

            imgRight = cv.QueryFrame(camRight)
            if imgRight is None:
                warnings.warn("Unable to open right camera")
                return None

            imgLeft = Image(imgLeft, cv2image=True)
            imgRight = Image(imgRight, cv2image=True)

        del camLeft
        del camRight

        stereoImages = StereoImage(imgLeft, imgRight)
        Image3D_normalize = stereoImages.get3DImage(Q, method, state)
        self.Image3D = stereoImages.Image3D
        return Image3D_normalize


class AVTCameraThread(threading.Thread):
    camera = None
    run = True
    verbose = False
    lock = None
    logger = None
    framerate = 0


    def __init__(self, camera):
        super(AVTCameraThread, self).__init__()
        self._stop = threading.Event()
        self.camera = camera
        self.lock = threading.Lock()
        self.name = 'Thread-Camera-ID-' + str(self.camera.uniqueid)

      
    def run(self):
        counter = 0
        timestamp = time.time()
        
        while self.run:
          self.lock.acquire()
          self.camera.runCommand("AcquisitionStart")
          frame = self.camera._getFrame(1000)
          
          if frame:            
            img = Image(pil.fromstring(self.camera.imgformat, 
              (self.camera.width, self.camera.height), 
              frame.ImageBuffer[:int(frame.ImageBufferSize)]))
            self.camera._buffer.appendleft(img)
            
          self.camera.runCommand("AcquisitionStop")
          self.lock.release()
          counter += 1
          time.sleep(0.01)

          if time.time() - timestamp >= 1:
            self.camera.framerate = counter
            counter = 0
            timestamp = time.time()
            


    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
  


AVTCameraErrors = [
    ("ePvErrSuccess",        "No error"),
    ("ePvErrCameraFault",        "Unexpected camera fault"),
    ("ePvErrInternalFault",        "Unexpected fault in PvApi or driver"),
    ("ePvErrBadHandle",        "Camera handle is invalid"),
    ("ePvErrBadParameter",        "Bad parameter to API call"),
    ("ePvErrBadSequence",        "Sequence of API calls is incorrect"),
    ("ePvErrNotFound",        "Camera or attribute not found"),
    ("ePvErrAccessDenied",        "Camera cannot be opened in the specified mode"),
    ("ePvErrUnplugged",        "Camera was unplugged"),
    ("ePvErrInvalidSetup",        "Setup is invalid (an attribute is invalid)"),
    ("ePvErrResources",       "System/network resources or memory not available"),
    ("ePvErrBandwidth",       "1394 bandwidth not available"),
    ("ePvErrQueueFull",       "Too many frames on queue"),
    ("ePvErrBufferTooSmall",       "Frame buffer is too small"),
    ("ePvErrCancelled",       "Frame cancelled by user"),
    ("ePvErrDataLost",       "The data for the frame was lost"),
    ("ePvErrDataMissing",       "Some data in the frame is missing"),
    ("ePvErrTimeout",       "Timeout during wait"),
    ("ePvErrOutOfRange",       "Attribute value is out of the expected range"),
    ("ePvErrWrongType",       "Attribute is not this type (wrong access function)"),
    ("ePvErrForbidden",       "Attribute write forbidden at this time"),
    ("ePvErrUnavailable",       "Attribute is not available at this time"),
    ("ePvErrFirewall",       "A firewall is blocking the traffic (Windows only)"),
  ]
def pverr(errcode):
  if errcode:
    raise Exception(": ".join(AVTCameraErrors[errcode]))


class AVTCamera(FrameSource):
    """
    **SUMMARY**
    AVTCamera is a ctypes wrapper for the Prosilica/Allied Vision cameras,
    such as the "manta" series.

    These require the PvAVT binary driver from Allied Vision:
    http://www.alliedvisiontec.com/us/products/1108.html

    Note that as of time of writing the new VIMBA driver is not available
    for Mac/Linux - so this uses the legacy PvAVT drive

    Props to Cixelyn, whos py-avt-pvapi module showed how to get much
    of this working https://bitbucket.org/Cixelyn/py-avt-pvapi

    All camera properties are directly from the PvAVT manual -- if not
    specified it will default to whatever the camera state is.  Cameras
    can either by

    **EXAMPLE**
    >>> cam = AVTCamera(0, {"width": 656, "height": 492})
    >>>
    >>> img = cam.getImage()
    >>> img.show()
    """

    
    _buffer = None # Buffer to store images
    _buffersize = 10 # Number of images to keep in the rolling image buffer for threads
    _lastimage = None # Last image loaded into memory
    _thread = None
    _framerate = 0
    threaded = False
    _pvinfo = { }    
    _properties = {
        "AcqEndTriggerEvent": ("Enum", "R/W"),
        "AcqEndTriggerMode": ("Enum", "R/W"),
        "AcqRecTriggerEvent": ("Enum", "R/W"),
        "AcqRecTriggerMode": ("Enum", "R/W"),
        "AcqStartTriggerEvent": ("Enum", "R/W"),
        "AcqStartTriggerMode": ("Enum", "R/W"),
        "FrameRate": ("Float32", "R/W"),
        "FrameStartTriggerDelay": ("Uint32", "R/W"),
        "FrameStartTriggerEvent": ("Enum", "R/W"),
        "FrameStartTriggerMode": ("Enum", "R/W"),
        "FrameStartTriggerOverlap": ("Enum", "R/W"),
        "AcquisitionFrameCount": ("Uint32", "R/W"),
        "AcquisitionMode": ("Enum", "R/W"),
        "RecorderPreEventCount": ("Uint32", "R/W"),
        "ConfigFileIndex": ("Enum", "R/W"),
        "ConfigFilePowerup": ("Enum", "R/W"),
        "DSPSubregionBottom": ("Uint32", "R/W"),
        "DSPSubregionLeft": ("Uint32", "R/W"),
        "DSPSubregionRight": ("Uint32", "R/W"),
        "DSPSubregionTop": ("Uint32", "R/W"),
        "DefectMaskColumnEnable": ("Enum", "R/W"),
        "ExposureAutoAdjustTol": ("Uint32", "R/W"),
        "ExposureAutoAlg": ("Enum", "R/W"),
        "ExposureAutoMax": ("Uint32", "R/W"),
        "ExposureAutoMin": ("Uint32", "R/W"),
        "ExposureAutoOutliers": ("Uint32", "R/W"),
        "ExposureAutoRate": ("Uint32", "R/W"),
        "ExposureAutoTarget": ("Uint32", "R/W"),
        "ExposureMode": ("Enum", "R/W"),
        "ExposureValue": ("Uint32", "R/W"),
        "GainAutoAdjustTol": ("Uint32", "R/W"),
        "GainAutoMax": ("Uint32", "R/W"),
        "GainAutoMin": ("Uint32", "R/W"),
        "GainAutoOutliers": ("Uint32", "R/W"),
        "GainAutoRate": ("Uint32", "R/W"),
        "GainAutoTarget": ("Uint32", "R/W"),
        "GainMode": ("Enum", "R/W"),
        "GainValue": ("Uint32", "R/W"),
        "LensDriveCommand": ("Enum", "R/W"),
        "LensDriveDuration": ("Uint32", "R/W"),
        "LensVoltage": ("Uint32", "R/V"),
        "LensVoltageControl": ("Uint32", "R/W"),
        "IrisAutoTarget": ("Uint32", "R/W"),
        "IrisMode": ("Enum", "R/W"),
        "IrisVideoLevel": ("Uint32", "R/W"),
        "IrisVideoLevelMax": ("Uint32", "R/W"),
        "IrisVideoLevelMin": ("Uint32", "R/W"),
        "VsubValue": ("Uint32", "R/C"),
        "WhitebalAutoAdjustTol": ("Uint32", "R/W"),
        "WhitebalAutoRate": ("Uint32", "R/W"),
        "WhitebalMode": ("Enum", "R/W"),
        "WhitebalValueRed": ("Uint32", "R/W"),
        "WhitebalValueBlue": ("Uint32", "R/W"),
        "EventAcquisitionStart": ("Uint32", "R/C 40000"),
        "EventAcquisitionEnd": ("Uint32", "R/C 40001"),
        "EventFrameTrigger": ("Uint32", "R/C 40002"),
        "EventExposureEnd": ("Uint32", "R/C 40003"),
        "EventAcquisitionRecordTrigger": ("Uint32", "R/C 40004"),
        "EventSyncIn1Rise": ("Uint32", "R/C 40010"),
        "EventSyncIn1Fall": ("Uint32", "R/C 40011"),
        "EventSyncIn2Rise": ("Uint32", "R/C 40012"),
        "EventSyncIn2Fall": ("Uint32", "R/C 40013"),
        "EventSyncIn3Rise": ("Uint32", "R/C 40014"),
        "EventSyncIn3Fall": ("Uint32", "R/C 40015"),
        "EventSyncIn4Rise": ("Uint32", "R/C 40016"),
        "EventSyncIn4Fall": ("Uint32", "R/C 40017"),
        "EventOverflow": ("Uint32", "R/C 65534"),
        "EventError": ("Uint32", "R/C"),
        "EventNotification": ("Enum", "R/W"),
        "EventSelector": ("Enum", "R/W"),
        "EventsEnable1": ("Uint32", "R/W"),
        "BandwidthCtrlMode": ("Enum", "R/W"),
        "ChunkModeActive": ("Boolean", "R/W"),
        "NonImagePayloadSize": ("Unit32", "R/V"),
        "PayloadSize": ("Unit32", "R/V"),
        "StreamBytesPerSecond": ("Uint32", "R/W"),
        "StreamFrameRateConstrain": ("Boolean", "R/W"),
        "StreamHoldCapacity": ("Uint32", "R/V"),
        "StreamHoldEnable": ("Enum", "R/W"),
        "TimeStampFrequency": ("Uint32", "R/C"),
        "TimeStampValueHi": ("Uint32", "R/V"),
        "TimeStampValueLo": ("Uint32", "R/V"),
        "Height": ("Uint32", "R/W"),
        "RegionX": ("Uint32", "R/W"),
        "RegionY": ("Uint32", "R/W"),
        "Width": ("Uint32", "R/W"),
        "PixelFormat": ("Enum", "R/W"),
        "TotalBytesPerFrame": ("Uint32", "R/V"),
        "BinningX": ("Uint32", "R/W"),
        "BinningY": ("Uint32", "R/W"),
        "CameraName": ("String", "R/W"),
        "DeviceFirmwareVersion": ("String", "R/C"),
        "DeviceModelName": ("String", "R/W"),
        "DevicePartNumber": ("String", "R/C"),
        "DeviceSerialNumber": ("String", "R/C"),
        "DeviceVendorName": ("String", "R/C"),
        "FirmwareVerBuild": ("Uint32", "R/C"),
        "FirmwareVerMajor": ("Uint32", "R/C"),
        "FirmwareVerMinor": ("Uint32", "R/C"),
        "PartClass": ("Uint32", "R/C"),
        "PartNumber": ("Uint32", "R/C"),
        "PartRevision": ("String", "R/C"),
        "PartVersion": ("String", "R/C"),
        "SerialNumber": ("String", "R/C"),
        "SensorBits": ("Uint32", "R/C"),
        "SensorHeight": ("Uint32", "R/C"),
        "SensorType": ("Enum", "R/C"),
        "SensorWidth": ("Uint32", "R/C"),
        "UniqueID": ("Uint32", "R/C"),
        "Strobe1ControlledDuration": ("Enum", "R/W"),
        "Strobe1Delay": ("Uint32", "R/W"),
        "Strobe1Duration": ("Uint32", "R/W"),
        "Strobe1Mode": ("Enum", "R/W"),
        "SyncIn1GlitchFilter": ("Uint32", "R/W"),
        "SyncInLevels": ("Uint32", "R/V"),
        "SyncOut1Invert": ("Enum", "R/W"),
        "SyncOut1Mode": ("Enum", "R/W"),
        "SyncOutGpoLevels": ("Uint32", "R/W"),
        "DeviceEthAddress": ("String", "R/C"),
        "HostEthAddress": ("String", "R/C"),
        "DeviceIPAddress": ("String", "R/C"),
        "HostIPAddress": ("String", "R/C"),
        "GvcpRetries": ("Uint32", "R/W"),
        "GvspLookbackWindow": ("Uint32", "R/W"),
        "GvspResentPercent": ("Float32", "R/W"),
        "GvspRetries": ("Uint32", "R/W"),
        "GvspSocketBufferCount": ("Enum", "R/W"),
        "GvspTimeout": ("Uint32", "R/W"),
        "HeartbeatInterval": ("Uint32", "R/W"),
        "HeartbeatTimeout": ("Uint32", "R/W"),
        "MulticastEnable": ("Enum", "R/W"),
        "MulticastIPAddress": ("String", "R/W"),
        "PacketSize": ("Uint32", "R/W"),
        "StatDriverType": ("Enum", "R/V"),
        "StatFilterVersion": ("String", "R/C"),
        "StatFrameRate": ("Float32", "R/V"),
        "StatFramesCompleted": ("Uint32", "R/V"),
        "StatFramesDropped": ("Uint32", "R/V"),
        "StatPacketsErroneous": ("Uint32", "R/V"),
        "StatPacketsMissed": ("Uint32", "R/V"),
        "StatPacketsReceived": ("Uint32", "R/V"),
        "StatPacketsRequested": ("Uint32", "R/V"),
        "StatPacketResent": ("Uint32", "R/V")
        }



    class AVTCameraInfo(ct.Structure):
        """
        AVTCameraInfo is an internal ctypes.Structure-derived class which
        contains metadata about cameras on the local network.

        Properties include:
        * UniqueId
        * CameraName
        * ModelName
        * PartNumber
        * SerialNumber
        * FirmwareVersion
        * PermittedAccess
        * InterfaceId
        * InterfaceType
        """
        _fields_ = [
            ("StructVer", ct.c_ulong),
            ("UniqueId", ct.c_ulong),
            ("CameraName", ct.c_char*32),
            ("ModelName", ct.c_char*32),
            ("PartNumber", ct.c_char*32),
            ("SerialNumber", ct.c_char*32),
            ("FirmwareVersion", ct.c_char*32),
            ("PermittedAccess", ct.c_long),
            ("InterfaceId", ct.c_ulong),
            ("InterfaceType", ct.c_int)
        ]

        def __repr__(self):
            return "<SimpleCV.Camera.AVTCameraInfo - UniqueId: %s>" % (self.UniqueId)

    class AVTFrame(ct.Structure):
        _fields_ = [
            ("ImageBuffer", ct.POINTER(ct.c_char)),
            ("ImageBufferSize", ct.c_ulong),
            ("AncillaryBuffer", ct.c_int),
            ("AncillaryBufferSize", ct.c_int),
            ("Context", ct.c_int*4),
            ("_reserved1", ct.c_ulong*8),

            ("Status", ct.c_int),
            ("ImageSize", ct.c_ulong),
            ("AncillarySize", ct.c_ulong),
            ("Width", ct.c_ulong),
            ("Height", ct.c_ulong),
            ("RegionX", ct.c_ulong),
            ("RegionY", ct.c_ulong),
            ("Format", ct.c_int),
            ("BitDepth", ct.c_ulong),
            ("BayerPattern", ct.c_int),
            ("FrameCount", ct.c_ulong),
            ("TimestampLo", ct.c_ulong),
            ("TimestampHi", ct.c_ulong),
            ("_reserved2", ct.c_ulong*32)
        ]

        def __init__(self, buffersize):
            self.ImageBuffer = ct.create_string_buffer(buffersize)
            self.ImageBufferSize = ct.c_ulong(buffersize)
            self.AncillaryBuffer = 0
            self.AncillaryBufferSize = 0
            self.img = None
            self.hasImage = False
            self.frame = None

    def __del__(self):
      #This function should disconnect from the AVT Camera
      pverr(self.dll.PvCameraClose(self.handle))
    
    def __init__(self, camera_id = -1, properties = {}, threaded = False):
        #~ super(AVTCamera, self).__init__()
        import platform

        if platform.system() == "Windows":
            self.dll = ct.windll.LoadLibrary("PvAPI.dll")
        elif platform.system() == "Darwin":
            self.dll = ct.CDLL("libPvAPI.dylib", ct.RTLD_GLOBAL)
        else:
            self.dll = ct.CDLL("libPvAPI.so")

        if not self._pvinfo.get("initialized", False):
            self.dll.PvInitialize()
            self._pvinfo['initialized'] = True
        #initialize.  Note that we rely on listAllCameras being the next
        #call, since it blocks on cameras initializing

        camlist = self.listAllCameras()

        if not len(camlist):
            raise Exception("Couldn't find any cameras with the PvAVT driver.  Use SampleViewer to confirm you have one connected.")

        if camera_id < 9000: #camera was passed as an index reference
            if camera_id == -1:  #accept -1 for "first camera"
                camera_id = 0

            camera_id = camlist[camera_id].UniqueId

        camera_id = long(camera_id)
        self.handle = ct.c_uint()
        init_count = 0
        while self.dll.PvCameraOpen(camera_id,0,ct.byref(self.handle)) != 0: #wait until camera is availble
          if init_count > 4: # Try to connect 5 times before giving up
            raise Exception('Could not connect to camera, please verify with SampleViewer you can connect')
          init_count += 1
          time.sleep(1) # sleep and retry to connect to camera in a second

        pverr(self.dll.PvCaptureStart(self.handle))
        self.uniqueid = camera_id

        self.setProperty("AcquisitionMode","SingleFrame")
        self.setProperty("FrameStartTriggerMode","Freerun")

        if properties.get("mode", "RGB") == 'gray':
            self.setProperty("PixelFormat", "Mono8")
        else:
            self.setProperty("PixelFormat", "Rgb24")

        #give some compatablity with other cameras
        if properties.get("mode", ""):
            properties.pop("mode")

        if properties.get("height", ""):
            properties["Height"] = properties["height"]
            properties.pop("height")

        if properties.get("width", ""):
            properties["Width"] = properties["width"]
            properties.pop("width")

        for p in properties:
            self.setProperty(p, properties[p])


        if threaded:
          self._thread = AVTCameraThread(self)
          self._thread.daemon = True
          self._buffer = deque(maxlen=self._buffersize)
          self._thread.start()
          self.threaded = True
        self.frame = None
        self._refreshFrameStats()

    def restart(self):
        """
        This tries to restart the camera thread
        """
        self._thread.stop()
        self._thread = AVTCameraThread(self)
        self._thread.daemon = True
        self._buffer = deque(maxlen=self._buffersize)
        self._thread.start()


    def listAllCameras(self):
        """
        **SUMMARY**
        List all cameras attached to the host

        **RETURNS**
        List of AVTCameraInfo objects, otherwise empty list

        """
        camlist = (self.AVTCameraInfo*100)()
        starttime = time.time()
        while int(camlist[0].UniqueId) == 0 and time.time() - starttime < 10:
            self.dll.PvCameraListEx(ct.byref(camlist), 100, None, ct.sizeof(self.AVTCameraInfo))
            time.sleep(0.1) #keep checking for cameras until timeout


        return [cam for cam in camlist if cam.UniqueId != 0]

    def runCommand(self,command):
        """
        **SUMMARY**
        Runs a PvAVT Command on the camera

        Valid Commands include:
        * FrameStartTriggerSoftware
        * AcquisitionAbort
        * AcquisitionStart
        * AcquisitionStop
        * ConfigFileLoad
        * ConfigFileSave
        * TimeStampReset
        * TimeStampValueLatch

        **RETURNS**

        0 on success

        **EXAMPLE**
        >>>c = AVTCamera()
        >>>c.runCommand("TimeStampReset")
        """
        return self.dll.PvCommandRun(self.handle,command)

    def getProperty(self, name):
        """
        **SUMMARY**
        This retrieves the value of the AVT Camera attribute

        There are around 140 properties for the AVT Camera, so reference the
        AVT Camera and Driver Attributes pdf that is provided with
        the driver for detailed information

        Note that the error codes are currently ignored, so empty values
        may be returned.

        **EXAMPLE**
        >>>c = AVTCamera()
        >>>print c.getProperty("ExposureValue")
        """
        valtype, perm = self._properties.get(name, (None, None))

        if not valtype:
            return None

        val = ''
        err = 0
        if valtype == "Enum":
            val = ct.create_string_buffer(100)
            vallen = ct.c_long()
            err = self.dll.PvAttrEnumGet(self.handle, name, val, 100, ct.byref(vallen))
            val = str(val[:vallen.value])
        elif valtype == "Uint32":
            val = ct.c_uint()
            err = self.dll.PvAttrUint32Get(self.handle, name, ct.byref(val))
            val = int(val.value)
        elif valtype == "Float32":
            val = ct.c_float()
            err = self.dll.PvAttrFloat32Get(self.handle, name, ct.byref(val))
            val = float(val.value)
        elif valtype == "String":
            val = ct.create_string_buffer(100)
            vallen = ct.c_long()
            err = self.dll.PvAttrStringGet(self.handle, name, val, 100, ct.byref(vallen))
            val = str(val[:vallen.value])
        elif valtype == "Boolean":
            val = ct.c_bool()
            err = self.dll.PvAttrBooleanGet(self.handle, name, ct.byref(val))
            val = bool(val.value)

        #TODO, handle error codes

        return val

    #TODO, implement the PvAttrRange* functions
    #def getPropertyRange(self, name)

    def getAllProperties(self):
        """
        **SUMMARY**
        This returns a dict with the name and current value of the
        documented PvAVT attributes

        CAVEAT: it addresses each of the properties individually, so
        this may take time to run if there's network latency

        **EXAMPLE**
        >>>c = AVTCamera(0)
        >>>props = c.getAllProperties()
        >>>print props['ExposureValue']

        """
        props = {}
        for p in self._properties.keys():
            props[p] = self.getProperty(p)

        return props

    def setProperty(self, name, value, skip_buffer_size_check=False):
        """
        **SUMMARY**
        This sets the value of the AVT Camera attribute.

        There are around 140 properties for the AVT Camera, so reference the
        AVT Camera and Driver Attributes pdf that is provided with
        the driver for detailed information

        By default, we will also refresh the height/width and bytes per
        frame we're expecting -- you can manually bypass this if you want speed

        Returns the raw PvAVT error code (0 = success)

        **Example**
        >>>c = AVTCamera()
        >>>c.setProperty("ExposureValue", 30000)
        >>>c.getImage().show()
        """
        valtype, perm = self._properties.get(name, (None, None))

        if not valtype:
            return None

        if valtype == "Uint32":
            err = self.dll.PvAttrUint32Set(self.handle, name, ct.c_uint(int(value)))
        elif valtype == "Float32":
            err = self.dll.PvAttrFloat32Set(self.handle, name, ct.c_float(float(value)))
        elif valtype == "Enum":
            err = self.dll.PvAttrEnumSet(self.handle, name, str(value))
        elif valtype == "String":
            err = self.dll.PvAttrStringSet(self.handle, name, str(value))
        elif valtype == "Boolean":
            err = self.dll.PvAttrBooleanSet(self.handle, name, ct.c_bool(bool(value)))

        #just to be safe, re-cache the camera metadata
        if not skip_buffer_size_check:
            self._refreshFrameStats()

        return err

    def getImage(self, timeout = 5000):
        """
        **SUMMARY**
        Extract an Image from the Camera, returning the value.  No matter
        what the image characteristics on the camera, the Image returned
        will be RGB 8 bit depth, if camera is in greyscale mode it will
        be 3 identical channels.

        **EXAMPLE**
        >>>c = AVTCamera()
        >>>c.getImage().show()
        """

        if self.frame != None:
            st = time.time()
            try:
                pverr( self.dll.PvCaptureWaitForFrameDone(self.handle, ct.byref(self.frame), timeout) )
            except Exception, e:
                print "Exception waiting for frame:", e
                print "Time taken:",time.time() - st
                self.frame = None
                raise(e)
            img = self.unbuffer()
            self.frame = None
            return img
        elif self.threaded:
          self._thread.lock.acquire()
          try:
              img = self._buffer.pop()
              self._lastimage = img
          except IndexError:
              img = self._lastimage
          self._thread.lock.release()

        else:
          self.runCommand("AcquisitionStart")
          frame = self._getFrame(timeout)
          img = Image(pil.fromstring(self.imgformat, 
              (self.width, self.height), 
              frame.ImageBuffer[:int(frame.ImageBufferSize)]))
          self.runCommand("AcquisitionStop")
        return img


    def setupASyncMode(self):
        self.setProperty('AcquisitionMode','SingleFrame')
        self.setProperty('FrameStartTriggerMode','Software')


    def setupSyncMode(self):
        self.setProperty('AcquisitionMode','Continuous')
        self.setProperty('FrameStartTriggerMode','FreeRun')

    def unbuffer(self):
        img = Image(pil.fromstring(self.imgformat,
                                   (self.width, self.height),
                                   self.frame.ImageBuffer[:int(self.frame.ImageBufferSize)]))

        return img

    def _refreshFrameStats(self):
        self.width = self.getProperty("Width")
        self.height = self.getProperty("Height")
        self.buffersize = self.getProperty("TotalBytesPerFrame")
        self.pixelformat = self.getProperty("PixelFormat")
        self.imgformat = 'RGB'
        if self.pixelformat == 'Mono8':
            self.imgformat = 'L'

    def _getFrame(self, timeout = 5000):
        #return the AVTFrame object from the camera, timeout in ms
        #need to multiply by bitdepth
        try:
          frame = self.AVTFrame(self.buffersize)
          pverr( self.dll.PvCaptureQueueFrame(self.handle, ct.byref(frame), None) )
          st = time.time()
          try:
            pverr( self.dll.PvCaptureWaitForFrameDone(self.handle, ct.byref(frame), timeout) )
          except Exception, e:
            print "Exception waiting for frame:", e
            print "Time taken:",time.time() - st
            raise(e)
            
        except Exception, e:
            print "Exception aquiring frame:", e
            raise(e)  
          
        return frame

    def acquire(self):
        self.frame = self.AVTFrame(self.buffersize)
        try:
            self.runCommand("AcquisitionStart")
            pverr( self.dll.PvCaptureQueueFrame(self.handle, ct.byref(self.frame), None) )
            self.runCommand("AcquisitionStop")
        except Exception, e:
            print "Exception aquiring frame:", e
            raise(e)  


class GigECamera(Camera):
    """
        GigE Camera driver via Aravis
    """
       
    def __init__(self, camera_id = None, properties = {}, threaded = False):
        try:
            from gi.repository import Aravis
        except:
            print "GigE is supported by the Aravis library, download and build from https://github.com/sightmachine/aravis"
            print "Note that you need to set GI_TYPELIB_PATH=$GI_TYPELIB_PATH:(PATH_TO_ARAVIS)/src for the GObject Introspection"
            sys.exit()
        
        self._cam = Aravis.Camera.new (None)
        
        self._pixel_mode = "RGB"
        if properties.get("mode", False):
            self._pixel_mode = properties.pop("mode")
        
        
        if self._pixel_mode == "gray":
            self._cam.set_pixel_format (Aravis.PIXEL_FORMAT_MONO_8)
        else:
            self._cam.set_pixel_format (Aravis.PIXEL_FORMAT_BAYER_BG_8) #we'll use bayer (basler cams)
            #TODO, deal with other pixel formats
        
        if properties.get("roi", False):
            roi = properties['roi']
            self._cam.set_region(*roi)
            #TODO, check sensor size
        
        if properties.get("width", False):
            #TODO, set internal function to scale results of getimage
            pass
        
        if properties.get("framerate", False):
            self._cam.set_frame_rate(properties['framerate'])
        
        self._stream = self._cam.create_stream (None, None)
        
        payload = self._cam.get_payload()
        self._stream.push_buffer(Aravis.Buffer.new_allocate (payload))
        [x,y,width,height] = self._cam.get_region ()
        self._height, self._width = height, width
    
    def getImage(self):
        
        camera = self._cam
        camera.start_acquisition()
        buff = self._stream.pop_buffer()
        self.capturetime = buff.timestamp_ns / 1000000.0
        img = np.fromstring(ct.string_at(buff.data_address(), buff.size), dtype = np.uint8).reshape(self._height, self._width)
        rgb = cv2.cvtColor(img, cv2.COLOR_BAYER_BG2BGR)
        self._stream.push_buffer(buff)
        camera.stop_acquisition()
        #TODO, we should handle software triggering (separate capture and get image events)
        
        return Image(rgb)

    def getPropertyList(self):
      l = [
           'available_pixel_formats',
           'available_pixel_formats_as_display_names',
           'available_pixel_formats_as_strings',
           'binning',
           'device_id',
           'exposure_time',
           'exposure_time_bounds',
           'frame_rate',
           'frame_rate_bounds',
           'gain',
           'gain_bounds',
           'height_bounds',
           'model_name',
           'payload',
           'pixel_format',
           'pixel_format_as_string',
           'region',
           'sensor_size',
           'trigger_source',
           'vendor_name',
           'width_bounds'
          ]
      return l
      
    
    def getProperty(self, name = None):
      '''
      This function get's the properties availble to the camera

      Usage:
        > camera.getProperty('region')
        > (0, 0, 128, 128)
      
      Available Properties:
        see function camera.getPropertyList()
      '''
      if name == None:
        print "You need to provide a property, available properties are:"
        print ""
        for p in self.getPropertyList():
          print p
        return

      stringval = "get_{}".format(name)
      try:
        return getattr(self._cam, stringval)()
      except:
        print 'Property {} does not appear to exist'.format(name)
        return None
      
    def setProperty(self, name = None, *args):
      '''
      This function sets the property available to the camera

      Usage:
        > camera.setProperty('region',(256,256))

      Available Properties:
        see function camera.getPropertyList()

      '''

      if name == None:
        print "You need to provide a property, available properties are:"
        print ""
        for p in self.getPropertyList():
          print p
        return

      if len(args) <= 0:
        print "You must provide a value to set"
        return
        
      stringval = "set_{}".format(name)
      try:
        return getattr(self._cam, stringval)(*args)
      except:
        print 'Property {} does not appear to exist or value is not in correct format'.format(name)
        return None

       
    def getAllProperties(self):
      '''
      This function just prints out all the properties available to the camera
      '''
      
      for p in self.getPropertyList():
        print "{}: {}".format(p,self.getProperty(p))

class VimbaCameraThread(threading.Thread):
    camera = None
    run = True
    verbose = False
    lock = None
    logger = None
    framerate = 0


    def __init__(self, camera):
        super(VimbaCameraThread, self).__init__()
        self._stop = threading.Event()
        self.camera = camera
        self.lock = threading.Lock()
        self.name = 'Thread-Camera-ID-' + str(self.camera.uniqueid)

      
    def run(self):
        counter = 0
        timestamp = time.time()
        
        while self.run:
            self.lock.acquire()

            img = self.camera._captureFrame(1000)
            self.camera._buffer.appendleft(img)

            self.lock.release()
            counter += 1
            time.sleep(0.01)

            if time.time() - timestamp >= 1:
                self.camera.framerate = counter
                counter = 0
                timestamp = time.time()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

class VimbaCamera(FrameSource):
    """
    **SUMMARY**
    VimbaCamera is a wrapper for the Allied Vision cameras,
    such as the "manta" series.

    This requires the 
    1) Vimba SDK provided from Allied Vision
    http://www.alliedvisiontec.com/us/products/software/vimba-sdk.html

    2) Pyvimba Python library
    TODO: <INSERT URL>

    Note that as of time of writing, the VIMBA driver is not available
    for Mac.

    All camera properties are directly from the Vimba SDK manual -- if not
    specified it will default to whatever the camera state is.  Cameras
    can either by

    **EXAMPLE**
    >>> cam = VimbaCamera(0, {"width": 656, "height": 492})
    >>>
    >>> img = cam.getImage()
    >>> img.show()
    """

    def _setupVimba(self):
        from pymba import Vimba

        self._vimba = Vimba()
        self._vimba.startup()
        system = self._vimba.getSystem()
        if system.GeVTLIsPresent:
            system.runFeatureCommand("GeVDiscoveryAllOnce")
            time.sleep(0.2)

    def __del__(self):
        #This function should disconnect from the Vimba Camera
        if self._camera is not None:
            if self.threaded:
                self._thread.stop()
                time.sleep(0.2)

            if self._frame is not None:
                self._frame.revokeFrame()
                self._frame = None

            self._camera.closeCamera()

        self._vimba.shutdown()

    def shutdown(self):
        """You must call this function if you are using threaded=true when you are finished
            to prevent segmentation fault"""
        # REQUIRED TO PREVENT SEGMENTATION FAULT FOR THREADED=True
        if (self._camera):
            self._camera.closeCamera()

        self._vimba.shutdown()


    def __init__(self, camera_id = -1, properties = {}, threaded = False):
        if not VIMBA_ENABLED:
            raise Exception("You don't seem to have the pymba library installed.  This will make it hard to use a AVT Vimba Camera.")

        self._vimba = None
        self._setupVimba()
        
        camlist = self.listAllCameras()
        self._camTable = {}
        self._frame = None
        self._buffer = None # Buffer to store images
        self._buffersize = 10 # Number of images to keep in the rolling image buffer for threads
        self._lastimage = None # Last image loaded into memory
        self._thread = None
        self._framerate = 0
        self.threaded = False
        self._properties = {}
        self._camera = None

        i = 0
        for cam in camlist:
            self._camTable[i] = {'id': cam.cameraIdString}
            i += 1

        if not len(camlist):
            raise Exception("Couldn't find any cameras with the Vimba driver.  Use VimbaViewer to confirm you have one connected.")

        if camera_id < 9000: #camera was passed as an index reference
            if camera_id == -1:  #accept -1 for "first camera"
                camera_id = 0

            if (camera_id > len(camlist)):
                raise Exception("Couldn't find camera at index %d." % camera_id)

            cam_guid = camlist[camera_id].cameraIdString
        else:
            raise Exception("Index %d is too large" % camera_id)

        self._camera = self._vimba.getCamera(cam_guid)
        self._camera.openCamera()

        self.uniqueid = cam_guid

        self.setProperty("AcquisitionMode","SingleFrame")
        self.setProperty("TriggerSource","Freerun")

        # TODO: FIX
        if properties.get("mode", "RGB") == 'gray':
            self.setProperty("PixelFormat", "Mono8")
        else:
            fmt = "RGB8Packed" # alternatively use BayerRG8
            self.setProperty("PixelFormat", "BayerRG8")

        #give some compatablity with other cameras
        if properties.get("mode", ""):
            properties.pop("mode")

        if properties.get("height", ""):
            properties["Height"] = properties["height"]
            properties.pop("height")

        if properties.get("width", ""):
            properties["Width"] = properties["width"]
            properties.pop("width")

        for p in properties:
            self.setProperty(p, properties[p])

        if threaded:
          self._thread = VimbaCameraThread(self)
          self._thread.daemon = True
          self._buffer = deque(maxlen=self._buffersize)
          self._thread.start()
          self.threaded = True
          
        self._refreshFrameStats()

    def restart(self):
        """
        This tries to restart the camera thread
        """
        self._thread.stop()
        self._thread = VimbaCameraThread(self)
        self._thread.daemon = True
        self._buffer = deque(maxlen=self._buffersize)
        self._thread.start()

    def listAllCameras(self):
        """
        **SUMMARY**
        List all cameras attached to the host

        **RETURNS**
        List of VimbaCamera objects, otherwise empty list
        VimbaCamera objects are defined in the pymba module
        """
        cameraIds = self._vimba.getCameraIds()
        ar = []
        for cameraId in cameraIds:
            ar.append(self._vimba.getCamera(cameraId))
        return ar

    def runCommand(self,command):
        """
        **SUMMARY**
        Runs a Vimba Command on the camera

        Valid Commands include:
        * AcquisitionAbort
        * AcquisitionStart
        * AcquisitionStop

        **RETURNS**

        0 on success

        **EXAMPLE**
        >>>c = VimbaCamera()
        >>>c.runCommand("TimeStampReset")
        """
        return self._camera.runFeatureCommand(command)

    def getProperty(self, name):
        """
        **SUMMARY**
        This retrieves the value of the Vimba Camera attribute

        There are around 140 properties for the Vimba Camera, so reference the
        Vimba Camera pdf that is provided with
        the SDK for detailed information

        Throws VimbaException if property is not found or not implemented yet.

        **EXAMPLE**
        >>>c = VimbaCamera()
        >>>print c.getProperty("ExposureMode")
        """        
        return self._camera.__getattr__(name)

    #TODO, implement the PvAttrRange* functions
    #def getPropertyRange(self, name)

    def getAllProperties(self):
        """
        **SUMMARY**
        This returns a dict with the name and current value of the
        documented Vimba attributes

        CAVEAT: it addresses each of the properties individually, so
        this may take time to run if there's network latency

        **EXAMPLE**
        >>>c = VimbaCamera(0)
        >>>props = c.getAllProperties()
        >>>print props['ExposureMode']

        """
        from pymba import VimbaException

        # TODO
        ar = {}
        c = self._camera
        cameraFeatureNames = c.getFeatureNames()
        for name in cameraFeatureNames:
            try:
                ar[name] =  c.__getattr__(name)
            except VimbaException:
                # Ignore features not yet implemented
                pass
        return ar
        

    def setProperty(self, name, value, skip_buffer_size_check=False):
        """
        **SUMMARY**
        This sets the value of the Vimba Camera attribute.

        There are around 140 properties for the Vimba Camera, so reference the
        Vimba Camera pdf that is provided with
        the SDK for detailed information

        Throws VimbaException if property not found or not yet implemented

        **Example**
        >>>c = VimbaCamera()
        >>>c.setProperty("ExposureAutoRate", 200)
        >>>c.getImage().show()
        """
        ret = self._camera.__setattr__(name, value)

        #just to be safe, re-cache the camera metadata
        if not skip_buffer_size_check:
            self._refreshFrameStats()

        return ret

    def getImage(self):
        """
        **SUMMARY**
        Extract an Image from the Camera, returning the value.  No matter
        what the image characteristics on the camera, the Image returned
        will be RGB 8 bit depth, if camera is in greyscale mode it will
        be 3 identical channels.

        **EXAMPLE**
        >>>c = VimbaCamera()
        >>>c.getImage().show()
        """

        if self.threaded:
            self._thread.lock.acquire()
            try:
                img = self._buffer.pop()
                self._lastimage = img
            except IndexError:
                img = self._lastimage
            self._thread.lock.release()

        else:
            img = self._captureFrame()

        return img


    def setupASyncMode(self):
        self.setProperty('AcquisitionMode','SingleFrame')
        self.setProperty('TriggerSource','Software')

    def setupSyncMode(self):
        self.setProperty('AcquisitionMode','SingleFrame')
        self.setProperty('TriggerSource','Freerun')

    def _refreshFrameStats(self):
        self.width = self.getProperty("Width")
        self.height = self.getProperty("Height")
        self.pixelformat = self.getProperty("PixelFormat")
        self.imgformat = 'RGB'
        if self.pixelformat == 'Mono8':
            self.imgformat = 'L'

    def _getFrame(self):
        if not self._frame:
            self._frame = self._camera.getFrame()    # creates a frame
            self._frame.announceFrame()

        return self._frame

    def _captureFrame(self, timeout = 5000):
        try:
            c = self._camera
            f = self._getFrame()

            colorSpace = ColorSpace.BGR
            if self.pixelformat == 'Mono8':
                colorSpace = ColorSpace.GRAY

            c.startCapture()
            f.queueFrameCapture()
            c.runFeatureCommand('AcquisitionStart')
            c.runFeatureCommand('AcquisitionStop')
            try:
                f.waitFrameCapture(timeout)
            except Exception, e:
                print "Exception waiting for frame: %s: %s" % (e, traceback.format_exc())
                raise(e)

            imgData = f.getBufferByteData()
            moreUsefulImgData = np.ndarray(buffer = imgData,
                                           dtype = np.uint8,
                                           shape = (f.height, f.width, 1))

            rgb = cv2.cvtColor(moreUsefulImgData, cv2.COLOR_BAYER_RG2RGB)
            c.endCapture()

            return Image(rgb, colorSpace=colorSpace, cv2image=imgData)

        except Exception, e:
            print "Exception acquiring frame: %s: %s" % (e, traceback.format_exc())
            raise(e)

