from SimpleCV import Camera, Image, Display

tv_original = Image("../../sampleimages/family_watching_television_1958.jpg")

tv_coordinates = [(353, 379), (433,380),(432, 448), (354,446)]
tv_mask = Image(tv_original.size()).invert().warp(tv_coordinates)
tv = tv_original - tv_mask

c = Camera()
d = Display(tv.size())

while d.isNotDone():
   bwimage = c.getImage().grayscale().resize(tv.width, tv.height)
   on_tv = tv + bwimage.warp(tv_coordinates)
   on_tv.save(d)
