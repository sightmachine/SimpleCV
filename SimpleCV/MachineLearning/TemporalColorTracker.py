from SimpleCV import Image, ImageSet, Camera, VirtualCamera, Features, ROI, Color
import numpy as np
import scipy.signal as sps
class TemporalColorTracker:
    def __init__(self):
        self._roi = None # the roi
        self._steadyState = None # mu/signal for the ss behavior
        self._window = None # the window for local min
        self._mode = "passfail"
        self._searchMode = "minima" # either minima or maxima
        self._channel = "I" # "R"/"G"/"B"/"I"/"H"
        self._decisionBoundry = None # the threshold for picking values
        
    def train(self,src,roi,mode="passfail",maxFrames=1000):
        """
        Use data = video/imageset/camera
        ROI should be ROI feature.
        two modes:
            passfail: ternary returns 'pass'/'fail'/None e.g. genetech
            counter: returns 'count'/None - e.g. zing
        """
        self._extract(src,roi,maxFrames)
        self._findSteadyState()
        self._findPeaks()
        
    def _getDataFromImg(self,img,roi):
        temp = roi.reassign(img)
        mc = temp.meanColor()
        self.data['r'].append(mc[0])
        self.data['g'].append(mc[1])
        self.data['b'].append(mc[2])
        # NEED TO CHECK THAT THIS REALLY RGB
        self.data['i'].append(Color.getLightness(mc))
        self.data['h'].append(Color.getHueFromRGB(mc))
        #return [mc[0],mc[1],mc[2],gray,Color.rgbToHue(mc)]

    def _extract(self,src,roi,maxFrames):
        self.data = {'r':[],'g':[],'b':[],'i':[],'h':[]}
        if( isinstance(src,ImageSet) ):
            src = VirtualCamera(src,st='imageset') # this could cause a bug
        if( isinstance(src,(VirtualCamera,Camera))):
            for i in range(0,maxFrames):
                img = src.getImage()
                print "Doing Frame {0}".format(i)
                if( img is None ):
                    break
                else:
                    img.show()
                    self._getDataFromImg(img,roi)
                
        else:
            warnings.warn('Not a valid train source')
            return None
    
    def _findSteadyState(self,windowSzPrct=0.05):
        # slide a window across each of the signals
        # find where the std dev of the window is minimal
        # this is the steady state (e.g. where the
        # assembly line has nothing moving)
        # save the mean and sd of this value
        # as a tuple in the steadyStateDict
        self.steadyState = {}
        for key in self.data.keys():
            wndwSz = int(np.floor(windowSzPrct*len(self.data[key])))
            signal = self.data[key]
            # slide the window and get the std
            data = [np.std(signal[i:i+wndwSz]) for i in range(0,len(signal)-wndwSz)]
            # find the first spot where sd is minimal
            index = np.where(data==np.min(data))[0][0]
            # find the mean for the window
            mean = np.mean(signal[index:index+wndwSz])
            self.steadyState[key]=(mean,data[index])


    def _findPeaks(self):
        self.peaks = {}
        for key in self.data.keys():
            wndwSz = int(np.floor(0.05*len(self.data[key])))
            idxs = sps.find_peaks_cwt(self.data[key],np.arange(1,wndwSz))
            self.peaks[key] = [(i,self.data[key][i]) for i in idxs]
