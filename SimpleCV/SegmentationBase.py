from SimpleCV.base import *
from SimpleCV.Features import Feature, FeatureSet
from SimpleCV.Color import Color
from SimpleCV.ImageClass import Image
import abc



class SegmentationBase(object):
    """
    Right now I am going to keep this class as brain dead and single threaded as
    possible just so I can get the hang of abc in python. The idea behind a segmentation
    object is that you pass it frames, it does some sort of operations and you
    get a foreground / background segemnted image. Eventually I would like
    these processes to by asynchronous and multithreaded so that they can raise
    specific image processing events. 
    """
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def loadSettings(self, file):
        """
        Load all of the segmentation settings from file
        """
        return
    
    @abc.abstractmethod
    def saveSettings(self, file):
        """
        save all of the segmentation settings from file
        """
        return
    
    @abc.abstractmethod
    def addImage(self, img):
        """
        Add a single image to the segmentation algorithm
        """
        return
    
    @abc.abstractmethod
    def isReady(self):
        """
        Returns true if the camera has a segmented image ready. 
        """
        return False
    
    @abc.abstractmethod
    def isError(self):
        """
        Returns true if the segmentation system has detected an error.
        Eventually we'll consruct a syntax of errors so this becomes
        more expressive 
        """
        return False
    
    @abc.abstractmethod
    def resetError(self):
        """
        Clear the previous error. 
        """
        return False
    
    @abc.abstractmethod
    def reset(self):
        """
        Perform a reset of the segmentation systems underlying data.
        """

    @abc.abstractmethod
    def getRawImage(self):
        """
        Return the segmented image with white representing the foreground
        and black the background. 
        """
        
    @abc.abstractmethod
    def getSegmentedImage(self, whiteFG=True):
        """
        Return the segmented image with white representing the foreground
        and black the background. 
        """
        
    @abc.abstractmethod
    def getSegmentedBlobs(self):
        """
        return the segmented blobs from the fg/bg image
        """
        
 #   @abc.abstractmethod    
 #   def setInternalResolution(width,height):
 #       """
 #       If this is set the segmentation algorithm automatically scales the input image
 #       prior to performing an operation so as to reduce computional time. The width and
 #       height values should be actual pixel values. 
 #       """