from SimpleCV import Image, ImageSet, Camera, VirtualCamera, ROI, Color, LineScan
import numpy as np
import scipy.signal as sps
import time as time
class TemporalColorTracker:
    def __init__(self):
        self._rtData = LineScan([]) # the deployed data
        self._steadyState = None # mu/signal for the ss behavior
        self._extractor = None
        self._roi = None
    def train(self,src,roi=None,extractor=None,maxFrames=1000,ssWndw=0.05,
              pkWndw=30, pkDelta=3, verbose=True):
        """
        Use data = video/imageset/camera
        ROI should be ROI feature.
        two modes:
            passfail: ternary returns 'pass'/'fail'/None e.g. genetech
            counter: returns 'count'/None - e.g. zing
        """
        if( roi is None and extractor is None ):
            warnings.warn('Need to provide an ROI or an extractor')
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
                print "Steady State: {0}+/-{1}".format(self.steadyState[key][0],self.steadyState[key][1])
                print "Peaks: {0}".format(self.peaks[key])
                print "Valleys: {0}".format(self.valleys[key])
                print "Use Peaks: {0}".format(self.doPeaks[key])
            print 30*'-'
            print "BEST SIGNAL: {0}".format(self.bestKey)
            print "BEST WINDOW: {0}".format(self.window)
            print "BEST CUTOFF: {0}".format(self.cutoff)
                
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
        if( isinstance(src,(VirtualCamera,Camera))):
            for i in range(0,maxFrames):
                img = src.getImage()
                if( isinstance(src,Camera) ):
                    time.sleep(0.05) # let the camera sleep
                if( img is None ):
                    break
                else:
                    self._getDataFromImg(img)
                
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
            self.window = p2pMean
        
        #NEED TO ERROR OUT ON NOT ENOUGH POINTS

    def _getBestValue(self,img):

        if( self._extractor ):
            mc = self._extractor(img)
        else:
            temp = self._roi.reassign(img)    
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
                lm = self._rtData.localMaxima()
                for l in lm:
                    if( l[0] == wndwCenter and l[1] > self.cutoff ):
                        retVal = "count"
            else:
                lm = self._rtData.localMinima()
                for l in lm:
                    if( l[0] == wndwCenter and l[1] < self.cutoff ):
                        retVal = "count"
        return retVal
        
    def recognize(self,img):
        v = self._getBestValue(img)
        return self._updateBuffer(v)
