from SimpleCV.base import *
from SimpleCV.ImageClass import *

class PCA:
    """
    **SUMMARY**

    This is the Principal Component Analysis class. PCA is a widely used 
    dimensionality reduction technique.

    This class provides you with projecting data to one of the
    principal components and also reconstructing from the reducded data.
    This is a lossy dimensionality reduction technique.

    **EXAMPLE**

    >>> p = PCA("path/to/dataset",retention = 50)
    >>> p.setSize((250,250))
    >>> p.setRetention(20)
    >>> p.project()
    >>> p.backProject.show()

    **NOTES**

    Further reading: https://en.wikipedia.org/wiki/Principal_component_analysis

    """

    _dataset = None #To store the original dataset
    _vectorImgs = None # To store the image set in row vector form. All images stacked up
    _stdDataset = None # To store standard dataset. Images with standard width and height in original color space
    meanDataset = None # To store the mean of the dataset
    _width = 150 #Standard width of the Dataset
    _height = 150 #Standard height of the Dataset
    meanValue = None # To store the mean of the images
    _covMat = None # To store the covariance matrix
    eigenValues = None # To store the eigen values
    eigenVectors = None # To store the eigen Vectors
    _featureMat = None # To store the important eigen vectors
    _retention = None # To store the percentage of eigen vectors to retain
    _projectionMat = None # To store the data projected on the principal components 
    _backProjectionMat = None # To store the back projected data
    _backProjectionData = None # Imageset for the rexonstructed data

    def __init__(self,data=None,size=(150,150),retention=70):

        if isinstance(data,ImageSet):
            self._dataset = data[:]
        elif isinstance(data,str) or isinstance(data,list):
            self._dataset = ImageSet(data)
        if self._dataset is not None:
            self._stdDataset = self._dataset.standardize(size[0],size[1]) #Standardize the dataset before processing
            self._width = size[0]
            self._height = size[1]
            self._retention = retention
        
    def loadData(self,data=None):
        """
        **SUMMARY**

        A funtion to quickly load datasets.        

        **PARAMETERS**

        * *data* - path to image datatset. Default value is set None.

        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> p = PCA()
        >>> p.loadData("path/to/datset")

        """

        if data is None:
            warnings.warn("No dataset passed")
            return None
        if isinstance(data,ImageSet):
            self._dataset = data[:]
        elif isinstance(data,str) or isinstance(data,list):
            self._dataset = ImageSet(data) # Load the set of Images to compute PCA 
        self._stdDataset = self._dataset.standardize(self._width,self._height)

    def setSize(self,size = (150,150)):
        """
        **SUMMARY**

        This allows you to set a standard size for the dataset

        **PARAMETERS**

        * *size* - (width,height) for the dataset.

        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> p = PCA()
        >>> p.setSize((250,250))

        """

        if self._dataset is None:
            warnings.warn('Load dataset first using loadData()')
            return None

        self._width = size[0]
        self._height = size[1]
        self._stdDataset = self._dataset.standardize(self._width,self._height)
        self.makeVectorImages()

    def setRetention(self,retention = 70):
        """
        **SUMMARY**

        This allows you to set the retention value.
        Retention value means the percentage of eigenvectors used for projection.

        **PARAMETERS**

        * *retention* - retention value. Give a value between 0 to 100(percentage).

        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> p = PCA()
        >>> p.setRetention(50)

        """

        self._retention  = retention

    def makeVectorImages(self):
        """
        **SUMMARY**

        Converts the given Images into 1-D arrays and stacks them together into one matrix.

        **PARAMETERS**

        Nothing.

        **RETURNS**

        Nothing.

        """

        if self._stdDataset is None:
            warnings.warn('No Data loaded. Load Data first.')
            return None
        self._vectorImgs = np.empty((len(self._stdDataset),self._width*self._height),dtype=np.int)
        for index in range(len(self._dataset)):
            self._vectorImgs[index] = self._stdDataset[index].getGrayNumpy().flatten()

    def mean(self):
        """
        **SUMMARY**

        Function to calculate the mean of the dataset. Mean is calcuated center the data
        about the mean.

        **PARAMETERS**

        Nothing.

        **RETURNS**

        Nothing.

        """

        self.meanValue = self._vectorImgs.mean(axis=1) #Calculate mean of each row
        self.meanDataset = np.empty((len(self._vectorImgs),self._width*self._height),dtype=np.float)
        for index in range(len(self._vectorImgs)):
            self.meanDataset[index] = self._vectorImgs[index] - self.meanValue[index]

    def covariance(self):
        """
        **SUMMARY**

        Calculates the covariance matrix of the 1-D vector images matrix

        **PARAMETERS**

        Nothing.

        **RETURNS**

        Nothing.

        """

        self._covMat = np.empty((len(self._stdDataset),self._width*self._height))
        self._covMat = np.cov(self.meanDataset) # Calculate the covariance matrix

    def project(self):
        """
        **SUMMARY**

        This function computes the Principal Component of the set of images.
        And projects the Images onto the Proncipal Component.

        **PARAMETERS**

        Nothing.

        **RETURNS**

        Nothing.

        **EXAMPLE**

        >>> p = PCA()
        >>> p.project()

        """

        if self._stdDataset is None:
            warnings.warn('No Data loaded. Load Data first.')
            return None

        self.makeVectorImages()
        self.mean()
        self.covariance()
        self.eigenValues , self.eigenVectors = np.linalg.eig(self._covMat) #Calculate the eigen values and the eigen vectors
        self.eigenVectors = self.eigenVectors[self.eigenValues.argsort()[::-1]] # Sort eigen vectors in descending order according to their corresponding eigen values
        self.eigenValues.sort()
        self.eigenValues = self.eigenValues[::-1] #Sort the eigen values in descending order
        l = (int)((self._retention / 100.0) * len(self.eigenValues))
        self._featureMat = np.empty((self.eigenVectors.shape[1],l),dtype=np.float)
        self._featureMat = np.copy(self.eigenVectors[:l])
        self._projectionMat = np.dot(self._featureMat,self.meanDataset)

    def backProject(self):
        """
        **SUMMARY**

        This function reconstructs the reduced dimension data back to the original data.

        **PARAMETERS**

        Nothing.

        **RETURNS**

        Reconstructed average image of the dataset.

        **EXAMPLE**

        >>> p = PCA()
        >>> p.backProject().show()

        """

        if self._featureMat is None:
            warnings.warn('Compute PCA first, using project()')
            return None

        self._backProjectionMat = np.dot(self._featureMat.transpose(),self._projectionMat)
        for index in range(len(self.meanValue)):
            self._backProjectionMat[index] = np.array((self._backProjectionMat[index] + self.meanValue[index]))
        self._backProjectionMat = np.uint8(self._backProjectionMat)
        self._backProjectionData = np.mean(self._backProjectionMat,axis=0)
        self._backProjectionData = np.uint8(self._backProjectionData)

        return Image(self._backProjectionData.reshape(self._width,self._height))
