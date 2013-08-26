from SimpleCV.base import cv2, np
from SimpleCV.ImageClass import Image

class SLIC:
    def __init__(self, img, step, nc):
        self.image = img
        #self.labimage = img.toLAB()
        self.img = img.getNumpy()
        self.labimg = cv2.cvtColor(self.img, cv2.COLOR_BGR2LAB).astype(np.float64)
        #self.labimg = self.labimage.getNumpy()
        self.contourImage = img.copy()
        self.contourImg = self.contourImage._numpy
        self.width, self.height = img.size()
        self.step = step
        self.nc = nc
        self.ns = step
        self.FLT_MAX = 1000000
        self.ITERATIONS = 10

    def generateSuperPixels(self):
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

    def _initData(self):
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
    
    def createConnectivity(self):
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

    def drawContours(self, color=(255, 0, 0)):
        dx8 = [-1, -1, 0, 1, 1, 1, 0, -1]
        dy8 = [0, -1, -1, -1, 0, 1, 1, 1]

        isTaken = np.zeros(self.img.shape[:2], np.bool)
        contours = []

        for i in xrange(self.width):
            for j in xrange(self.height):
                nr_p = 0
                for dx, dy in zip(dx8, dy8):
                    x = i + dx
                    y = j + dy
                    if x>=0 and x < self.width and y>=0 and y < self.height:
                        if isTaken[y, x] == False and self.clusters[j, i] != self.clusters[y, x]:
                            nr_p += 1
                if nr_p >= 2:
                    isTaken[j, i] = True
                    contours.append([j, i])

        for i in xrange(len(contours)):
            self.contourImg[contours[i][0], contours[i][1]] = color

    def showContours(self):
        self.createConnectivity()
        self.drawContours()
        self.contourImage.show()

