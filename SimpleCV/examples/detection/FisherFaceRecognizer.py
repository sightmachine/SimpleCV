from SimpleCV import *
import time
"""
This is an example of HOW-TO use FaceRecognizer to recognize gender
of the person.
"""


def identifyGender():
    f = FaceRecognizer()
    cam = Camera()
    img = cam.getImage()
    cascade = LAUNCH_PATH + "/" + "Features/HaarCascades/face.xml"
    feat = img.findHaarFeatures(cascade)
    if feat:
        crop_image = feat.sortArea()[-1].crop()
        feat.sortArea()[-1].draw()

    f.load(LAUNCH_PATH + "/" + "Features/FaceRecognizerData/GenderData.xml")
    w, h = f.imageSize
    crop_image = crop_image.resize(w, h)
    label, confidence = f.predict(crop_image)
    print label
    if label == 0:
        img.drawText("Female", fontsize=48)

    else:
        img.drawText("Male", fontsize=48)
    img.show()
    time.sleep(4)

identifyGender()
