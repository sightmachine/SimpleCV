from SimpleCV import Image, ImageSet, Camera, VirtualCamera, ROI, Color, LineScan
import numpy as np
import scipy.signal as sps
import warnings
import time as time
class TemporalColorTracker:
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

    def train(self,src,roi=None, extractor=None, doCorr=False, maxFrames=1000,
              ssWndw=0.05, pkWndw=30, pkDelta=3, forceChannel=None, verbose=True):
        """
        Use data = video/imageset/camera
        ROI should be ROI feature.
        forceChannel => use specific channel
        two modes:
            passfail: ternary returns 'pass'/'fail'/None e.g. genetech
            counter: returns 'count'/None - e.g. zing
        """
        if( roi is None and extractor is None ):
            raise Exception('Need to provide an ROI or an extractor')
        self.doCorr = doCorr
        self._extractor = extractor #function that returns a RGB values
        self._roi = roi
        self._extract(src,maxFrames)
        self._findSteadyState(windowSzPrct=ssWndw)
        self._findPeaks(pkWndw,pkDelta)
        self._extractSignalInfo()
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

    def _extract(self,src,maxFrames):
        self.data = {'r':[],'g':[],'b':[],'i':[],'h':[]}
        if( isinstance(src,ImageSet) ):
            src = VirtualCamera(src,st='imageset') # this could cause a bug
        elif( isinstance(src,(VirtualCamera,Camera))):
            for i in range(0,maxFrames):
                img = src.getImage()
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
        corrVals = [np.correlate(peak,self._template) for peak in self.corrTemplates] 
        self.corrThresh = np.mean(corrVals)-(3.0*np.std(corrVals))
        
    def _getBestValue(self,img):

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
        retVal = None
        self._rtData.append(v)
        wndwCenter = int(np.floor(self._window/2.0))
        # pop the end of the buffer
        if( len(self._rtData) > self._window):
            self._rtData = self._rtData[1:]
            if( self._isPeak ):
                lm = self._rtData.localMaxima()
                for l in lm:
                    if( l[0] == wndwCenter and l[1] > self._cutoff ):
                        if( self.doCorr ):
                            corrVal = np.correlate(self._rtData,self._template)
                            if( corrVal[0] > self.corrThresh ):
                                retVal = "count"
                        else:
                            retVal = "count"
            else:
                lm = self._rtData.localMinima()
                for l in lm:
                    if( l[0] == wndwCenter and l[1] < self._cutoff ):
                        if( self.doCorr ):
                            corrVal = np.correlate(self._rtData,self._template)
                            if( corrVal[0] > self.corrThresh ):
                                retVal = "count"
                        else:
                            retVal = "count"
        return retVal
        
    def recognize(self,img):
        if( self._bestKey is None ):
            raise Exception('The TemporalColorTracker has not been trained.')
        v = self._getBestValue(img)
        return self._updateBuffer(v)
