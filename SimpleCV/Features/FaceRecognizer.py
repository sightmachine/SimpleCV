from SimpleCV.base import *
from SimpleCV.ImageClass import Image


class FaceRecognizer():

    def __init__(self):
        """
        Create a Face Recognizer Class using Fisher Face Recognizer. Uses
        OpenCV's FaceRecognizer class. Currently supports Fisher Faces.
        """
        self.supported = True
        self.model = None
        self.train_imgs = None
        self.train_labels = None
        self.csvfiles = []
        self.imageSize = None
        self.labels_dict = {}
        self.labels_set = []
        self.int_labels = []
        self.labels_dict_rev = {}
        # Not yet supported
        # self.eigenValues = None
        # self.eigenVectors = None
        # self.mean = None

        try:
            import cv2
            self.model = cv2.createFisherFaceRecognizer()
        except ImportError, AttributeError:
            self.supported = False
            warnings.warn("Fisher Recognizer is supported by OpenCV >= 2.4.4")

    def train(self, images=None, labels=None, csvfile=None, delimiter=";"):
        """
        **SUMMARY**

        Train the face recognizer with images and labels.

        **PARAMETERS**

        * *images*    - A list of Images or ImageSet. All the images must be of
                        same size.
        * *labels*    - A list of labels(int) corresponding to the image in
                        images.
                        There must be at least two different labels.
        * *csvfile*   - You can also provide a csv file with image filenames
                        and labels instead of providing labels and images
                        separately.
        * *delimiter* - The delimiter used in csv files.

        **RETURNS**

        Nothing. None.

        **EXAMPLES**

        >>> f = FaceRecognizer()
        >>> imgs1 = ImageSet(path/to/images_of_type1)
        >>> labels1 = [0]*len(imgs1)
        >>> imgs2 = ImageSet(path/to/images_of_type2)
        >>> labels2 = [1]*len(imgs2)
        >>> imgs3 = ImageSet(path/to/images_of_type3)
        >>> labels3 = [2]*len(imgs3)
        >>> imgs = imgs1 + imgs2 + imgs3
        >>> labels = labels1 + labels2 + labels3
        >>> f.train(imgs, labels)
        >>> img = Image("some_image_of_any_of_the_above_type")
        >>> print f.predict(img)

        Save Fisher Training Data
        >>> f.save("trainingdata.xml")

        Load Fisher Training Data and directly use without trainging
        >>> f1 = FaceRecognizer()
        >>> f1.load("trainingdata.xml")
        >>> img = Image("some_image_of_any_of_the_above_type")
        >>> print f1.predict(img)

        Use CSV files for training
        >>> f = FaceRecognizer()
        >>> f.train(csvfile="CSV_file_name", delimiter=";")
        >>> img = Image("some_image_of_any_of_the_type_in_csv_file")
        >>> print f.predict(img)
        """
        if not self.supported:
            warnings.warn("Fisher Recognizer is supported by OpenCV >= 2.4.4")
            return None

        if csvfile:
            images = []
            labels = []
            import csv
            try:
                f = open(csvfile, "rb")
            except IOError:
                warnings.warn("No such file found. Training not initiated")
                return None

            self.csvfiles.append(csvfile)
            filereader = csv.reader(f, delimiter=delimiter)
            for row in filereader:
                images.append(Image(row[0]))
                labels.append(row[1])

        if isinstance(labels, type(None)):
            warnings.warn("Labels not provided. Training not inititated.")
            return None

        self.labels_set = list(set(labels))
        i = 0
        for label in self.labels_set:
            self.labels_dict.update({label: i})
            self.labels_dict_rev.update({i: label})
            i += 1

        if len(self.labels_set) < 2:
            warnings.warn("At least two classes/labels are required"
                          "for training. Training not inititated.")
            return None

        if len(images) != len(labels):
            warnings.warn("Mismatch in number of labels and number of"
                          "training images. Training not initiated.")
            return None

        self.imageSize = images[0].size()
        w, h = self.imageSize
        images = [img if img.size() == self.imageSize else img.resize(w, h)
                  for img in images]

        self.int_labels = [self.labels_dict[key] for key in labels]
        self.train_labels = labels
        labels = np.array(self.int_labels)
        self.train_imgs = images
        cv2imgs = [img.getGrayNumpyCv2() for img in images]

        self.model.train(cv2imgs, labels)
        # Not yet supported
        # self.eigenValues = self.model.getMat("eigenValues")
        # self.eigenVectors = self.model.getMat("eigenVectors")
        # self.mean = self.model.getMat("mean")

    def predict(self, image):
        """
        **SUMMARY**

        Predict the class of the image using trained face recognizer.

        **PARAMETERS**

        * *image*    -  Image.The images must be of the same size as provided
                        in training.

        **RETURNS**

        * *label* - Class of the image which it belongs to.

        **EXAMPLES**

        >>> f = FaceRecognizer()
        >>> imgs1 = ImageSet(path/to/images_of_type1)
        >>> labels1 = ["type1"]*len(imgs1)
        >>> imgs2 = ImageSet(path/to/images_of_type2)
        >>> labels2 = ["type2"]*len(imgs2)
        >>> imgs3 = ImageSet(path/to/images_of_type3)
        >>> labels3 = ["type3"]*len(imgs3)
        >>> imgs = imgs1 + imgs2 + imgs3
        >>> labels = labels1 + labels2 + labels3
        >>> f.train(imgs, labels)
        >>> img = Image("some_image_of_any_of_the_above_type")
        >>> print f.predict(img)

        Save Fisher Training Data
        >>> f.save("trainingdata.xml")

        Load Fisher Training Data and directly use without trainging
        >>> f1 = FaceRecognizer()
        >>> f1.load("trainingdata.xml")
        >>> img = Image("some_image_of_any_of_the_above_type")
        >>> print f1.predict(img)

        Use CSV files for training
        >>> f = FaceRecognizer()
        >>> f.train(csvfile="CSV_file_name", delimiter=";")
        >>> img = Image("some_image_of_any_of_the_type_in_csv_file")
        >>> print f.predict(img)
        """
        if not self.supported:
            warnings.warn("Fisher Recognizer is supported by OpenCV >= 2.4.4")
            return None

        if image.size() != self.imageSize:
            w, h = self.imageSize
            image = image.resize(w, h)

        cv2img = image.getGrayNumpyCv2()
        label, confidence = self.model.predict(cv2img)
        retLabel = self.labels_dict_rev.get(label)
        if not retLabel:
            retLabel = label
        return retLabel,confidence

    # def update():
    #     OpenCV 2.4.4 doens't support update yet. It asks to train.
    #     But it's not updating it.
    #     Once OpenCV starts supporting update, this function should be added
    #     it can be found at https://gist.github.com/jayrambhia/5400347

    def save(self, filename):
        """
        **SUMMARY**

        Save the trainging data.

        **PARAMETERS**

        * *filename* - File where you want to save the data.

        **RETURNS**

        Nothing. None.

        **EXAMPLES**

        >>> f = FaceRecognizer()
        >>> imgs1 = ImageSet(path/to/images_of_type1)
        >>> labels1 = [0]*len(imgs1)
        >>> imgs2 = ImageSet(path/to/images_of_type2)
        >>> labels2 = [1]*len(imgs2)
        >>> imgs3 = ImageSet(path/to/images_of_type3)
        >>> labels3 = [2]*len(imgs3)
        >>> imgs = imgs1 + imgs2 + imgs3
        >>> labels = labels1 + labels2 + labels3
        >>> f.train(imgs, labels)
        >>> img = Image("some_image_of_any_of_the_above_type")
        >>> print f.predict(img)

        #Save New Fisher Training Data
        >>> f.save("new_trainingdata.xml")
        """
        if not self.supported:
            warnings.warn("Fisher Recognizer is supported by OpenCV >= 2.4.4")
            return None

        self.model.save(filename)

    def load(self, filename):
        """
        **SUMMARY**

        Load the trainging data.

        **PARAMETERS**

        * *filename* - File where you want to load the data from.

        **RETURNS**

        Nothing. None.

        **EXAMPLES**

        >>> f = FaceRecognizer()
        >>> f.load("trainingdata.xml")
        >>> img = Image("some_image_of_any_of_the_type_present_in_data")
        >>> print f.predict(img)
        """
        if not self.supported:
            warnings.warn("Fisher Recognizer is supported by OpenCV >= 2.4.4")
            return None

        self.model.load(filename)
        loadfile = open(filename, "r")
        for line in loadfile.readlines():
            if "cols" in line:
                match = re.search("(?<=\>)\w+", line)
                tsize = int(match.group(0))
                break
        loadfile.close()
        w = int(tsize ** 0.5)
        h = tsize / w
        while(w * h != tsize):
            w += 1
            h = tsize / w
        self.imageSize = (w, h)
