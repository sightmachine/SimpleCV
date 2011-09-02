
img = img.scale(img.width/2,img.height/2)
f0.save('f0.png')
f1.save('f1.png')

img = Image()
img = Image('../sampleimages/twofaces3.jpg')
img.show()


cam = Camera()
img = cam.getImage()
faces = img.findHaarFeatures("facetrack-training.xml")
len(faces)
f0 = img.crop(faces[0].x,faces[0].y,faces[0].width(),faces[0].height(),centered=True)
f1 = img.crop(faces[1].x,faces[1].y,faces[1].width(),faces[1].height(),centered=True)
f0 = f0.scale(faces[1].width(),faces[1].height())
f1= f1.scale(faces[0].width(),faces[0].height())
img = img.blit(f1,(faces[0].x,faces[0].y),centered=True)
img = img.blit(f0,(faces[1].x,faces[1].y),centered=True)
img.show()

