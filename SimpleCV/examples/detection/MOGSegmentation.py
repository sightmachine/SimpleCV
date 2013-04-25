from SimpleCV import Camera, Display
from SimpleCV.Color import Color
from SimpleCV.Segmentation.MOGSegmentation import MOGSegmentation

mog = MOGSegmentation(history = 200, nMixtures = 5, backgroundRatio = 0.3, noiseSigma = 16, learningRate = 0.3)
  
cam = Camera()  
  
disp = Display()
  
while (disp.isNotDone()):  
    frame = cam.getImage()
    
    mog.addImage(frame)
    
    segmentedImage = mog.getSegmentedImage()
    blobs = mog.getSegmentedBlobs()
    for blob in blobs:
        segmentedImage.dl().circle((blob.x, blob.y), 10, Color.RED)
    
    segmentedImage.save(disp)
