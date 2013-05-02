from SimpleCV import Image, ImageSet, Camera, VirtualCamera, ROI, Color, LineScan
import numpy as np
import scipy.signal as sps
class TemporalColorTracker:
    def __init__(self):
        self._rtData = LineScan([]) # the deployed data
        self._roi = None # the roi
        self._steadyState = None # mu/signal for the ss behavior
        self._window = None # the window for local min
        self._mode = "passfail"
        self._searchMode = "minima" # either minima or maxima
        self._channel = "I" # "R"/"G"/"B"/"I"/"H"
        self._decisionBoundry = None # the threshold for picking values
        
    def train(self,src,roi,mode="passfail",maxFrames=1000,ssWndw=0.05,
              pkWndw=30, pkDelta=3):
        """
        Use data = video/imageset/camera
        ROI should be ROI feature.
        two modes:
            passfail: ternary returns 'pass'/'fail'/None e.g. genetech
            counter: returns 'count'/None - e.g. zing
        """
        self._extract(src,roi,maxFrames)
        self._findSteadyState(windowSzPrct=ssWndw)
        self._findPeaks(pkWndw,pkDelta)
        self._extractSignalInfo()
        self._buildSignalProfile()
        self.roi = roi
        
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


    def _findPeaks(self,pkWndw,pkDelta):
        self.peaks = {}
        self.valleys = {}
        for key in self.data.keys():
            ls = LineScan(self.data[key])
            # need to automagically adjust the window
            # to make sure we get a minimum number of
            # of peaks, maybe let the user guess a min?
            self.peaks[key]=ls.findPeaks(pkWndw,pkDelta)
            self.valleys[key]=ls.findValleys(pkWndw,pkDelta)

    def _extractSignalInfo(self):
        self.pD = {}
        self.vD = {}
        self.doPeaks = {}
        bestSpread = 0.00
        bestDoPeaks = None
        bestKey = None
        for key in self.data.keys():
            #Look at which signal has a bigger distance from
            #the steady state behavior
            peakMean = np.mean(np.array(self.peaks[key])[:,1])
            self.pD[key] =  np.abs(self.steadyState[key][0]-peakMean)
            valleyMean = np.mean(np.array(self.valleys[key])[:,1])
            self.vD[key] =  np.abs(self.steadyState[key][0]-valleyMean)
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
        self.bestKey = key
        print "Using key " + key
        
    def _buildSignalProfile(self):
        key = self.bestKey
        peaks = None
        if( self.doPeaks[key] ):
            self.isPeak = True
            peaks = self.peaks[key]
            # We're just going to do halfway
            self.cutoff = self.steadyState[key][0]+(self.pD[key]/2.0)            
        else:
            self.isPeak = False
            peaks = self.valleys[key]
            self.cutoff = self.steadyState[key][0]-(self.vD[key]/2.0)
        if( len(peaks) > 1 ):
            p2p = np.array(peaks[1:])-np.array(peaks[:-1])
            p2pMean = np.mean(p2p)
            p2pS = np.std(p2p)
            self.window = p2pMean/2
        
        #NEED TO ERROR OUT ON NOT ENOUGH POINTS

    def _getBestValue(self,img):
        temp = self.roi.reassign(img)
        mc = temp.meanColor()
        if( self.bestKey == 'r' ):
            return mc[0]
        elif( self.bestKey == 'g' ):
            return mc[1]
        elif( self.bestKey == 'b' ):
            return mc[2]
        elif( self.bestKey == 'i' ):
            return Color.getLightness(mc)
        elif( self.bestKey == 'h' ):
            return Color.getHueFromRGB(mc)
        
    def _updateBuffer(self,v):
        retVal = None
        self._rtData.append(v)
        wndwCenter = int(np.floor(self.window/2.0))
        # pop the end of the buffer
        if( len(self._rtData) > self.window):
            self._rtData = self._rtData[1:]
            if( self.isPeak ):
                lm = self._rtData.maxima()[0]
                if( lm[0] == wndwCenter and lm[1] > self.cutoff ):
                    retVal = "count"
            else:
                lm = self._rtData.minima()[0]
                if( lm[0] == wndwCenter and lm[1] < self.cutoff ):
                    retVal = "count"
        return retVal
        
    def recognize(self,img):
        v = self._getBestValue(img)
        return self._updateBuffer(v)
