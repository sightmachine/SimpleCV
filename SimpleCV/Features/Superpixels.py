from SimpleCV.base import cv2, np, LazyProperty, copy
from SimpleCV.ImageClass import Image
from SimpleCV.Features import Blob, FeatureSet
from SimpleCV.Color import Color

class SLIC:
    """
    **SUMMARY**

    This class contains an implementation of the SLIC Superpixel
    algorithm by Achanta et al. (PAMI'12, vol. 34, num. 11, pp. 2274-2282).
    The C++ implementation from which this Python implementation is derived
    can be found here https://github.com/PSMM/SLIC-Superpixels

    **EXAMPLE**

     >>> img = Image("lenna")
     >>> nr_superpixels = 400
     >>> step = int((img.width*img.height/nr_superpixels)**0.5)
     >>> nc = 40
     >>> slic = SLIC(img, step, nc)
     >>> superpixels = slic.generateSuperPixels()
     >>> superpixels.show()
    """
    def __init__(self, img, step, nc):
        self.image = img
        self.img = img.getNumpy()
        self.labimg = cv2.cvtColor(self.img, cv2.COLOR_BGR2LAB).astype(np.float64)
        self.contourImage = img.copy()
        self.contourImg = self.contourImage._numpy
        self.width, self.height = img.size()
        self.step = step
        self.nc = nc
        self.ns = step
        self.FLT_MAX = 1000000
        self.ITERATIONS = 10

    def generateSuperPixels(self):
        """
        Compute the over-segmentation based on the step-size and relative 
        weighting of the pixel and colour values.
        """
        self._initData()
        indnp = np.mgrid[0:self.height,0:self.width].swapaxes(0,2).swapaxes(0,1)
        for i in range(self.ITERATIONS):
            self.distances = self.FLT_MAX * np.ones(self.img.shape[:2])
            for j in xrange(self.centers.shape[0]):
                xlow, xhigh = int(self.centers[j][3] - self.step), int(self.centers[j][3] + self.step)
                ylow, yhigh = int(self.centers[j][4] - self.step), int(self.centers[j][4] + self.step)

                if xlow <= 0:
                    xlow = 0
                if xhigh > self.width:
                    xhigh = self.width
                if ylow <=0:
                    ylow = 0
                if yhigh > self.height:
                    yhigh = self.height

                cropimg = self.labimg[ylow : yhigh , xlow : xhigh].astype(np.int64)
                colordiff = cropimg - self.labimg[self.centers[j][4], self.centers[j][3]]
                colorDist = np.sqrt(np.sum(np.square(colordiff.astype(np.int64)), axis=2))

                yy, xx = np.ogrid[ylow : yhigh, xlow : xhigh]
                pixdist = ((yy-self.centers[j][4])**2 + (xx-self.centers[j][3])**2)**0.5
                dist = ((colorDist/self.nc)**2 + (pixdist/self.ns)**2)**0.5

                distanceCrop = self.distances[ylow : yhigh, xlow : xhigh]
                idx = dist < distanceCrop
                distanceCrop[idx] = dist[idx]
                self.distances[ylow : yhigh, xlow : xhigh] = distanceCrop
                self.clusters[ylow : yhigh, xlow : xhigh][idx] = j

            for k in xrange(len(self.centers)):
                idx = (self.clusters == k)
                colornp = self.labimg[idx]
                distnp = indnp[idx]
                self.centers[k][0:3] = np.sum(colornp, axis=0)
                sumy, sumx = np.sum(distnp, axis=0)
                self.centers[k][3:] = sumx, sumy
                self.centers[k] /= np.sum(idx)

        self._createConnectivity()
        superpixels = self._segmentSuperpixels()
        return superpixels

    def _initData(self):
        """
        Initialize the cluster centers and initial values of the pixel-wise
        cluster assignment and distance values.
        """
        self.clusters = -1 * np.ones(self.img.shape[:2])
        self.distances = self.FLT_MAX * np.ones(self.img.shape[:2])

        centers = []
        for i in xrange(self.step, self.width - self.step/2, self.step):
            for j in xrange(self.step, self.height - self.step/2, self.step):
                nc = self._findLocalMinimum(center=(i, j))
                color = self.labimg[nc[1], nc[0]]
                center = [color[0], color[1], color[2], nc[0], nc[1]]
                centers.append(center)
        self.center_counts = np.zeros(len(centers))
        self.centers = np.array(centers)

    def _findLocalMinimum(self, center):
        """
        Find a local gradient minimum of a pixel in a 3x3 neighbourhood.
        This method is called upon initialization of the cluster centers.
        """
        min_grad = self.FLT_MAX
        loc_min = center
        for i in xrange(center[0] - 1, center[0] + 2):
            for j in xrange(center[1] - 1, center[1] + 2):
                c1 = self.labimg[j+1, i]
                c2 = self.labimg[j, i+1]
                c3 = self.labimg[j, i]
                if ((c1[0] - c3[0])**2)**0.5 + ((c2[0] - c3[0])**2)**0.5 < min_grad:
                    min_grad = abs(c1[0] - c3[0]) + abs(c2[0] - c3[0])
                    loc_min = [i, j]
        return loc_min
    
    def _createConnectivity(self):
        """
        Enforce connectivity of the superpixels. Needs to be optimized.
        """
        label = 0
        adjlabel = 0
        lims = self.width * self.height / self.centers.shape[0]
        dx4 = [-1, 0, 1, 0]
        dy4 = [0, -1, 0, 1]
        new_clusters = -1 * np.ones(self.img.shape[:2]).astype(np.int64)

        elements = []
        for i in xrange(self.width):
            for j in xrange(self.height):
                if new_clusters[j, i] == -1:
                    elements = []
                    elements.append((j, i))
                    for dx, dy in zip(dx4, dy4):
                        x = elements[0][1] + dx
                        y = elements[0][0] + dy
                        if (x>=0 and x < self.width and 
                            y>=0 and y < self.height and 
                            new_clusters[y, x] >=0):
                            adjlabel = new_clusters[y, x]

                count = 1
                c = 0
                while c < count:
                    for dx, dy in zip(dx4, dy4):
                        x = elements[c][1] + dx
                        y = elements[c][0] + dy

                        if (x>=0 and x<self.width and y>=0 and y<self.height):
                            if new_clusters[y, x] == -1 and self.clusters[j, i] == self.clusters[y, x]:
                                elements.append((y, x))
                                new_clusters[y, x] = label
                                count+=1
                    c+=1
                #print count
                if (count <= lims >> 2):
                    for c in range(count):
                        new_clusters[elements[c]] = adjlabel
                    label-=1
                label+=1
        self.new_clusters = new_clusters

    def _segmentSuperpixels(self):
        img = self.new_clusters
        limit = np.max(img)
        superpixels = Superpixels()
        for label in range(limit+1):
            clusterimg = Image(255*(img == label).astype(np.uint8))
            blobs = clusterimg.findBlobs()
            if blobs is None:
                continue
            blob = blobs[-1]
            blob.image = self.image & clusterimg
            superpixels.append(blob)
        return superpixels

class Superpixels(FeatureSet):
    """
    ** SUMMARY **
    Superpixels is a class extended from FeatureSet which is a class
    extended from Python's list. So, it has all the properties of a list
    as well as all the properties of FeatureSet.

    Each object of this list is a Blob corresponding to the superpixel.

    ** EXAMPLE **
    >>> image = Image("lenna")
    >>> sp = image.segmentSuperpixels(300, 20)
    >>> sp.show()
    >>> sp.centers()
    """
    def __init__(self):
        self._drawingImage = None
        self.clusterMeanImage = None
        pass

    def append(self, blob):
        list.append(self, blob)
        #if len(self) != 1:
            #self.image += blob.image.copy()

    @LazyProperty
    def image(self):
        img = None
        for sp in self:
            if img is None:
                img = sp.image
            else:
                img += sp.image
        return img

    def draw(self, color=Color.BLUE, width=2, alpha=255):
        """
        **SUMMARY**

        Draw all the superpixels, in the given color, to the appropriate layer

        By default, this draws the superpixels boundary. If you
        provide a width, an outline of the exterior and interior contours is drawn.

        **PARAMETERS**

        * *color* -The color to render the blob as a color tuple.
        * *width* - The width of the drawn blob in pixels, if -1 then filled then the polygon is filled.
        * *alpha* - The alpha value of the rendered blob 0=transparent 255=opaque.
        
        **RETURNS**

        Image with superpixels drawn on it.

        **EXAMPLE**

        >>> image = Image("lenna")
        >>> sp = image.segmentSuperpixels(300, 20)
        >>> sp.draw(color=(255, 0, 255), width=5, alpha=128).show()
        """
        img = self.image.copy()
        self._drawingImage = Image(self.image.getEmpty(3))
        _mLayers = []
        for sp in self:
            sp.draw(color=color, width=width, alpha=alpha)
            self._drawingImage += sp.image.copy()
            for layer in sp.image._mLayers:
                _mLayers.append(layer)
        self._drawingImage._mLayers = copy(_mLayers)
        return self._drawingImage.copy()

    def show(self, color=Color.BLUE, width=2, alpha=255):
        """
        **SUMMARY**

        This function automatically draws the superpixels on the drawing image
        and shows it.

        ** RETURNS **

        None

        ** EXAMPLE **
        >>> image = Image("lenna")
        >>> sp = image.segmentSuperpixels(300, 20)
        >>> sp.show(color=(255, 0, 255), width=5, alpha=128)
        """
        if type(self._drawingImage) == type(None):
            self.draw(color=color, width=width, alpha=alpha)
        self._drawingImage.show()

    def colorWithClusterMeans(self):
        """
        **SUMMARY**

        This function colors each superpixel with its mean color and
        return an image.

        **RETURNS**
        Image with superpixles drawn in its mean color.

        **EXAMPLE**
        >>> image = Image("lenna")
        >>> sp = image.segmentSuperpixels(300, 20)
        >>> sp.colorWithClusterMeans().show()
        """
        if type(self.clusterMeanImage) != type(None):
            return self.clusterMeanImage
        self.clusterMeanImage = Image(self.image.getEmpty(3))
        _mLayers = []
        for sp in self:
            color = tuple(reversed(sp.meanColor()))
            sp.draw(color=color, width=-1)
            self.clusterMeanImage += sp.image.copy()
            for layer in sp.image._mLayers:
                _mLayers.append(layer)
        self.clusterMeanImage._mLayers = copy(_mLayers)
        return self.clusterMeanImage
