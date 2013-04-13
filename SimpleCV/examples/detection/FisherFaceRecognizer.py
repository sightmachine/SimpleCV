from SimpleCV import *
import time
"""
This is an example of HOW-TO use FaceRecognizer to recognize gender
of the person in the ImageSet
"""

def identifyGender():
    f = FaceRecognizer()

    imgset1 = ImageSet("../../sampleimages/facerecognizer/female")
    label1 = [0]*len(imgset1)

    imgset2 = ImageSet("../../sampleimages/facerecognizer/male")
    label2 = [1]*len(imgset2)

    imgset = imgset1 + imgset2
    labels = label1 + label2
    f.train(imgset, labels)

    imgset3 = ImageSet("../../sampleimages/facerecognizer/identify")

    for img in imgset3:
        label = f.predict(img)
        if label == 0:
            img.drawText("Female")
        else:
            img.drawText("Male")
        img.show()
        time.sleep(4)

identifyGender()
