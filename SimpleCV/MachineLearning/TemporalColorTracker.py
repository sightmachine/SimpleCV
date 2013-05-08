from SimpleCV import Image, ImageSet, Camera, VirtualCamera, ROI, Color, LineScan
import numpy as np
import scipy.signal as sps
import warnings
import time as time
class TemporalColorTracker:
    """
    **SUMMARY**

    The temporal color tracker attempts to find and periodic color
    signal in an roi or arbitrary function. Once the temporal tracker is
    trained it will return a count object every time the signal is detected.
    This class is usefull for counting periodically occuring events, for example,
    waves on a beach or the second hand on a clock.
    
    """
    def __init__(self):
        self._rtData = LineScan([]) # the deployed data
        self._steadyState = None # mu/signal for the ss behavior
        self._extractor = None
        self._roi = None
        self._window = None
        self._template = None
        self._cutoff = None
        self._bestKey = None
        self._isPeak = False
        self.corrTemplates = None
        self.peaks = {}
        self.valleys = {}
        self.doPeaks = {}
        self.corrStdMult = 3.0
        self.count = 0

    def train(self,src,roi=None, extractor=None, doCorr=False, maxFrames=1000,
              ssWndw=0.05, pkWndw=30, pkDelta=3, corrStdMult=2.0, forceChannel=None, verbose=True):
        """
        **SUMMARY**

        To train the TemporalColorTracker you provide it with a video, camera, or ImageSet and either
        an region of interest (ROI) or a function of the form:

        (R,G,B) = MyFunction(Image)

        This function takes in an image and returns a tuple of RGB balues for the frame.
        The TemoralColroTracker will then attempt to find the maximum peaks in the data
        and create a model for the peaks.

        **PARAMETERS**

        * *src* - An image source, either a camera, a virtual camera (like a video) or
          an ImageSet.
        * *roi* - An ROI object that tells the tracker where to look in the frame.
        * *extractor* - A function with the following signature:
          (R,G,B) = Extract(Image)
        * *doCorr* - Do correlation use correlation to confirm that the signal is present.
        * *maxFrames* - The maximum number of frames to use for training.
        * *ssWndw* - SteadyState window, this is the size of the window to look for a steady
          state, i.e a region where the signal is not changing.
        * *pkWndw* - The window size to look for peaks/valleys in the signal. This is roughly
          the period of the signal.
        * *pkDelta* - The minimum difference between the steady state to look for peaks.
        * *corrStdMult* - The maximum correlation standard deviation of the training set
          to use when looking for a signal. This is the knob to dial in when using correlation
          to confirm the event happened.
        * *forceChannel* - A string that is the channel to use. Options are:
           * 'r' - Red Channel
           * 'g' - Green Channel
           * 'b' - Blue Channel 
           * 'h' - Hue Channel
           * 'i' - Intensity Channel
          By default this module will look at the signal with the highest peak/valley swings.
          You can manually overide this behavior.
        * *verbose* - Print debug info after training. 
        
        **RETURNS**

        Nothing, will raise an exception if no signal is found.

        **EXAMPLE**

        A really simple example

        >>>> cam = Camera(1)
        >>>> tct = TemporalColorTracker()
        >>>> img = cam.getImage()
        >>>> roi = ROI(img.width*0.45,img.height*0.45,img.width*0.1,img.height*0.1,img)
        >>>> tct.train(cam,roi=roi,maxFrames=250)
        >>>> disp = Display((800,600))
        >>>> while disp.isNotDone():
        >>>>     img = cam.getImage()
        >>>>     result = tct.recognize(img)
        >>>>     roi = ROI(img.width*0.45,img.height*0.45,img.width*0.1,img.height*0.1,img)
        >>>>     roi.draw(width=3)
        >>>>     img.drawText(str(result),20,20,color=Color.RED,fontsize=32)
        >>>>     img = img.applyLayers()
        >>>>     img.save(disp)

        """
        if( roi is None and extractor is None ):
            raise Exception('Need to provide an ROI or an extractor')
        self.doCorr = doCorr
        self.corrStdMult = corrStdMult
        self._extractor = extractor #function that returns a RGB values
        self._roi = roi
        self._extract(src,maxFrames,verbose)
        self._findSteadyState(windowSzPrct=ssWndw)
        self._findPeaks(pkWndw,pkDelta)
        self._extractSignalInfo(forceChannel)
        self._buildSignalProfile()
        if verbose:
            for key in self.data.keys():
                print 30*'-'
                print "Channel: {0}".format(key)
                print "Data Points: {0}".format(len(self.data[key]))
                print "Steady State: {0}+/-{1}".format(self._steadyState[key][0],self._steadyState[key][1])
                print "Peaks: {0}".format(self.peaks[key])
                print "Valleys: {0}".format(self.valleys[key])
                print "Use Peaks: {0}".format(self.doPeaks[key])
            print 30*'-'
            print "BEST SIGNAL: {0}".format(self._bestKey)
            print "BEST WINDOW: {0}".format(self._window)
            print "BEST CUTOFF: {0}".format(self._cutoff)
                
    def _getDataFromImg(self,img):
        """
        Get the data from the image 
        """
        mc = None
        if( self._extractor ):
            mc = self._extractor(img)
        else:
            temp = self._roi.reassign(img)    
            mc = temp.meanColor()
        self.data['r'].append(mc[0])
        self.data['g'].append(mc[1])
        self.data['b'].append(mc[2])
        # NEED TO CHECK THAT THIS REALLY RGB
        self.data['i'].append(Color.getLightness(mc))
        self.data['h'].append(Color.getHueFromRGB(mc))
        #return [mc[0],mc[1],mc[2],gray,Color.rgbToHue(mc)]

    def _extract(self,src,maxFrames,verbose):
        # get the full dataset and append it to the data vector dictionary.
        self.data = {'r':[],'g':[],'b':[],'i':[],'h':[]}
        if( isinstance(src,ImageSet) ):
            src = VirtualCamera(src,st='imageset') # this could cause a bug
        elif( isinstance(src,(VirtualCamera,Camera))):
            count = 0
            for i in range(0,maxFrames):
                img = src.getImage()
                count = count + 1
                if( verbose ):
                    print "Got Frame {0}".format(count)
                if( isinstance(src,Camera) ):
                    time.sleep(0.05) # let the camera sleep
                if( img is None ):
                    break
                else:
                    self._getDataFromImg(img)
                
        else:
            raise Exception('Not a valid training source')
            return None
    
    def _findSteadyState(self,windowSzPrct=0.05):
        # slide a window across each of the signals
        # find where the std dev of the window is minimal
        # this is the steady state (e.g. where the
        # assembly line has nothing moving)
        # save the mean and sd of this value
        # as a tuple in the steadyStateDict
        self._steadyState = {}
        for key in self.data.keys():
            wndwSz = int(np.floor(windowSzPrct*len(self.data[key])))
            signal = self.data[key]
            # slide the window and get the std
            data = [np.std(signal[i:i+wndwSz]) for i in range(0,len(signal)-wndwSz)]
            # find the first spot where sd is minimal
            index = np.where(data==np.min(data))[0][0]
            # find the mean for the window
            mean = np.mean(signal[index:index+wndwSz])
            self._steadyState[key]=(mean,data[index])


    def _findPeaks(self,pkWndw,pkDelta):
        """
        Find the peaks and valleys in the data
        """
        self.peaks = {}
        self.valleys = {}
        for key in self.data.keys():
            ls = LineScan(self.data[key])
            # need to automagically adjust the window
            # to make sure we get a minimum number of
            # of peaks, maybe let the user guess a min?
            self.peaks[key]=ls.findPeaks(pkWndw,pkDelta)
            self.valleys[key]=ls.findValleys(pkWndw,pkDelta)

    def _extractSignalInfo(self,forceChannel):
        """
        Find the difference between the peaks and valleys
        """
        self.pD = {}
        self.vD = {}
        self.doPeaks = {}
        bestSpread = 0.00
        bestDoPeaks = None
        bestKey = None
        for key in self.data.keys():
            #Look at which signal has a bigger distance from
            #the steady state behavior
            if( len(self.peaks[key]) > 0 ):
                peakMean = np.mean(np.array(self.peaks[key])[:,1])
                self.pD[key] =  np.abs(self._steadyState[key][0]-peakMean)
            else:
                self.pD[key] = 0.00

            if( len(self.valleys[key]) > 0 ):
                valleyMean = np.mean(np.array(self.valleys[key])[:,1])
                self.vD[key] =  np.abs(self._steadyState[key][0]-valleyMean)
            else:
                self.vD[key] = 0.00
                
            self.doPeaks[key]=False
            best = self.vD[key]
            if( self.pD[key] > self.vD[key] ):
                best = self.pD[key]
                self.doPeaks[key] = True
            if( best > bestSpread ):
                bestSpread = best
                bestDoPeaks = self.doPeaks[key]
                bestKey = key
        # Now we know which signal has the most spread
        # and what direction we are looking for.
        if( forceChannel is not None ):
            if(self.data.has_key(forceChannel)):
                self._bestKey = forceChannel
            else:
                raise Exception('That is not a valid data channel')
        else:
            self._bestKey = bestKey

        
    def _buildSignalProfile(self):
        key = self._bestKey
        self._window = None
        peaks = None
        if( self.doPeaks[key] ):
            self._isPeak = True
            peaks = self.peaks[key]
            # We're just going to do halfway
            self._cutoff = self._steadyState[key][0]+(self.pD[key]/2.0)            
        else:
            self._isPeak = False
            peaks = self.valleys[key]
            self._cutoff = self._steadyState[key][0]-(self.vD[key]/2.0)
        if( len(peaks) > 1 ):
            p2p = np.array(peaks[1:])-np.array(peaks[:-1])
            p2pMean = int(np.mean(p2p))
            p2pS = int(np.std(p2p))
            p2pMean = p2pMean + 2*p2pS
            # constrain it to be an od window
            if int(p2pMean) % 2 == 1:
                p2pMean = p2pMean+1 
            self._window = p2pMean
        else:
            raise Exception("Can't find enough peaks")
        if( self.doCorr and self._window is not None ):
            self._doCorr()

        #NEED TO ERROR OUT ON NOT ENOUGH POINTS

    def _doCorr(self):
        key = self._bestKey
        # build an average signal for the peaks and valleys
        # centered at the peak. The go and find the correlation
        # value of each peak/valley with the average signal
        self.corrTemplates = []
        halfWndw = self._window/2
        pList = None 
        if( self._isPeak ):
            pList = self.peaks[key]
        else:
            pList = self.valleys[key]

        for peak in pList:
            center = peak[0]
            lb = center-halfWndw
            ub = center+halfWndw
            # ignore signals that fall of the end of the data
            if( lb > 0 and ub < len(self.data[key]) ):
                self.corrTemplates.append(np.array(self.data[key][lb:ub]))
        if( len(self.corrTemplates) < 1 ):
            raise Exception('Could not find a coherrent signal for correlation.')
        
        sig = np.copy(self.corrTemplates[0]) # little np gotcha
        for peak in self.corrTemplates[1:]:
            sig += peak
        self._template = sig / len(self.corrTemplates)
        self._template /= np.max(self._template)
        corrVals = [np.correlate(peak/np.max(peak),self._template) for peak in self.corrTemplates] 
        print corrVals
        self.corrThresh = (np.mean(corrVals),np.std(corrVals))
        
    def _getBestValue(self,img):
        """
        Extract the data from the live signal
        """
        if( self._extractor ):
            mc = self._extractor(img)
        else:
            temp = self._roi.reassign(img)    
            mc = temp.meanColor()
        if( self._bestKey == 'r' ):
            return mc[0]
        elif( self._bestKey == 'g' ):
            return mc[1]
        elif( self._bestKey == 'b' ):
            return mc[2]
        elif( self._bestKey == 'i' ):
            return Color.getLightness(mc)
        elif( self._bestKey == 'h' ):
            return Color.getHueFromRGB(mc)
        
    def _updateBuffer(self,v):
        """
        Keep a buffer of the running data and process it to determine if there is
        a peak. 
        """
        self._rtData.append(v)
        wndwCenter = int(np.floor(self._window/2.0))
        # pop the end of the buffer
        if( len(self._rtData) > self._window):
            self._rtData = self._rtData[1:]
            if( self._isPeak ):
                lm = self._rtData.findPeaks()
                for l in lm:
                    if( l[0] == wndwCenter and l[1] > self._cutoff ):
                        if( self.doCorr ):
                            corrVal = np.correlate(self._rtData.normalize(),self._template)
                            thresh = self.corrThresh[0]-self.corrStdMult*self.corrThresh[1]
                            if( corrVal[0] > thresh ):
                                self.count += 1
                        else:
                            self.count += 1
            else:
                lm = self._rtData.findValleys()
                for l in lm:
                    if( l[0] == wndwCenter and l[1] < self._cutoff ):
                        if( self.doCorr ):
                            corrVal = np.correlate(self._rtData.normalize(),self._template)
                            thresh = self.corrThresh[0]-self.corrStdMult*self.corrThresh[1]
                            if( corrVal[0] > thresh ):
                                self.count += 1
                        else:
                            self.count += 1
        return self.count
        
    def recognize(self,img):
        """

        **SUMMARY***

        This method is used to do the real time signal analysis. Pass the method
        an image from the stream and it will return the event count. Note that
        due to buffering the signal may lag the actual video by up to a few seconds.

        **PARAMETERS**

        * *img* - The image in the stream to test. 

        **RETURNS**

        Returns an int that is the count of the number of times the event has occurred.

        **EXAMPLE**

        >>>> cam = Camera(1)
        >>>> tct = TemporalColorTracker()
        >>>> img = cam.getImage()
        >>>> roi = ROI(img.width*0.45,img.height*0.45,img.width*0.1,img.height*0.1,img)
        >>>> tct.train(cam,roi=roi,maxFrames=250)
        >>>> disp = Display((800,600))
        >>>> while disp.isNotDone():
        >>>>     img = cam.getImage()
        >>>>     result = tct.recognize(img)
        >>>>     roi = ROI(img.width*0.45,img.height*0.45,img.width*0.1,img.height*0.1,img)
        >>>>     roi.draw(width=3)
        >>>>     img.drawText(str(result),20,20,color=Color.RED,fontsize=32)
        >>>>     img = img.applyLayers()
        >>>>     img.save(disp)

        **TODO**

        Return True/False if the event occurs.
        """
        if( self._bestKey is None ):
            raise Exception('The TemporalColorTracker has not been trained.')
        v = self._getBestValue(img)
        return self._updateBuffer(v)
