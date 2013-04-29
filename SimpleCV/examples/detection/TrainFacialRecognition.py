from SimpleCV import *
import time

# This file shows you how to train Fisher Face Recognition
# Enter the names of the faces and the output file.
cam = Camera(0) # camera
names = ['Alice','Bob'] # names of people to recognize
outfile = "test.csv" #output file 
waitTime = 10 # how long to wait between each training session

def getFaceSet(cam,myStr=""):
    # Grab a series of faces and return them.
    # quit when we press escape. 
    iset = ImageSet()
    count = 0
    disp = Display((640,480))
    while disp.isNotDone():
        img = cam.getImage()
        fs = img.findHaarFeatures('face')
        if( fs is not None ):
            fs = fs.sortArea()
            face = fs[-1].crop().resize(100,100)
            fs[-1].draw()
            iset.append(face)
            count = count + 1
        img.drawText(myStr,20,20,color=Color.RED,fontsize=32)
        img.save(disp)
    disp.quit()
    return iset

# First make sure our camera is all set up.
getFaceSet(cam,"Get Camera Ready! - ESC to Exit")
time.sleep(5)
labels = []
imgs = []
# for each person grab a training set of images
# and generate a list of labels.
for name in names:
    myStr = "Training for : " + name
    iset = getFaceSet(cam,myStr)
    imgs += iset
    labels += [name for i in range(0,len(iset))]
    time.sleep(waitTime)

# Create, train, and save the recognizer. 
f = FaceRecognizer()
print f.train(imgs, labels)
f.save(outfile)
# Now show us the results
disp = Display((640,480))
while disp.isNotDone():
    img = cam.getImage()
    fs = img.findHaarFeatures('face')
    if( fs is not None ):
        fs = fs.sortArea()
        face = fs[-1].crop().resize(100,100)
        fs[-1].draw()
        name, confidence = f.predict(face)
        img.drawText(name,30,30,fontsize=64)
    img.save(disp)
