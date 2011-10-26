# This demo is used to find missing pills in a blister type of package
# it would be used in quality control in manufacturing type of application
# were you are verifying that the correct number of pills are present



from SimpleCV import *

pillcolor = (153, 198, 252)
i = Image("pills.png")
expected_pillcount = 12
saturation_threshold = 40
pill_size = 100
packblobs = i.findBlobs(minsize=10) #find the bright silver on back blackground, easy

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
  for p in pills:
     p.image = pack
     p.drawHull( color = Color.RED, width = 5 )
  i.dl().blit(pack.applyLayers(), packblobs[idx].points[0])
  packblobs[idx].drawHull(color = Color.BLUE, width = 5)
#
d = i.show()
i.save("pillsresult.png")
