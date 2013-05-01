from SimpleCV import Image, ImageSet, Camera, VirtualCamera, Features, ROI, Color

class TemporalColorTracker:
    def __init__(self):
        self._roi = None # the roi
        self._steadyState = None # mu/signal for the ss behavior
        self._window = None # the window for local min
        self._mode = "passfail"
        self._searchMode = "minima" # either minima or maxima
        self._channel = "I" # "R"/"G"/"B"/"I"/"H"
        self._decisionBoundry = None # the threshold for picking values
        
    def train(self,src,roi,mode="passfail",maxFrames=5000):
        """
        Use data = video/imageset/camera
        ROI should be ROI feature.
        two modes:
            passfail: ternary returns 'pass'/'fail'/None e.g. genetech
            counter: returns 'count'/None - e.g. zing
        """
        self._extract(src,roi,maxFrames)

    def _getDataFromImg(self,img,roi):
        
        temp = roi.reassign(img)
        mc = temp.meanColor()
        # lightness
        gray = (np.max(mc)+np.min(mc)/2.0)
        self.data['r'].append(mc[0])
        self.data['g'].append(mc[1])
        self.data['b'].append(mc[2])
        self.data['i'].append(gray)
        self.data['h'].append(Color.rgbToHue(mc))
        #return [mc[0],mc[1],mc[2],gray,Color.rgbToHue(mc)]
        
    def _extract(self,src,roi,maxFrames):
        self.data = {'r':[],'g':[],'b':[],'i':[],'h':[]}
        if( isinstance(src,ImageSet) ):
            src = VirtualCamera(src,st='imageset') # this could cause a bug
        if( isinstance(src,(VirtualCamera,Camera))):
            for i in range(0,maxFrames):
                img = src.getImage()
                img.show()
                self._getDataFromImg(img,roi)
        else:
            warnings.warn('Not a valid train source')
            return None
    
