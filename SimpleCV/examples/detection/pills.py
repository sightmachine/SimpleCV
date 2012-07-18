'''
This demo is used to find missing pills in a blister type of package
it would be used in quality control in manufacturing type of application
were you are verifying that the correct number of pills are present
'''


from SimpleCV import *

pillcolor = (153, 198, 252)  #This is set manually, you could either open the image you want and pick the color, or use blob detection to find the blob and do .meanColor() to get the RGB value
i = Image("pills.png", sample=True)
expected_pillcount = 12
saturation_threshold = 40  #This is how much saturation to allow in the image
pill_size = 100 #The size of the expected pills in pixels
packblobs = i.findBlobs(minsize=10) #find the bright silver on back blackground, easy


#run through the list of pills (blobs) found and check their color and markup the image when they are found
for idx in range(len(packblobs)):
  pack = packblobs[idx].crop()

  pills = pack.hueDistance(pillcolor, minsaturation = saturation_threshold)
  pills = pills.binarize(127)

  bm = BlobMaker()
  pills = bm.extractFromBinary(pills,pills,minsize=pill_size)
  if not pills:
     continue

  pillcount = len(pills)
  if pillcount != expected_pillcount:
    print "pack at %d, %d had %d pills" % (packblobs[idx].x, packblobs[idx].y, pillcount)
    i.drawText("Pills Found: " + str(pillcount), 10, 10, fontsize = 20)
    i.drawText("Pills Expected: " + str(expected_pillcount), 10, 30, fontsize = 20)
  for p in pills:
     p.image = pack
     p.drawHull( color = Color.RED, width = 5 )
  i.dl().blit(pack.applyLayers(), packblobs[idx].points[0])
  packblobs[idx].drawHull(color = Color.BLUE, width = 5)

#Continue to show the image
while True:
    i.show()

