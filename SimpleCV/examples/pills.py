from SimpleCV import *

pillcolor = (153, 198, 252)
i = Image("pills.png")
expected_pillcount = 12
saturation_threshold = 40
pill_size = 100

packblobs = i.findBlobs() #find the bright silver on back blackground, easy

for pb in packblobs:
  pack = pb.crop()
  pills = pack.hueDistance(pillcolor, minsaturation = saturation_threshold)
  pills = pills.binarize(50)
  pills = pills.findBlobs(minsize = pill_size)
  if not pills:
     continue

  pillcount = len(pills)
  if pillcount != expected_pillcount:
     print "pack at %d, %d had %d pills" % (pb.x, pb.y, pillcount)
  for p in pills:
     p.image = pack
     p.drawHull( color = Color.RED, width = 5 )
  i.dl().blit(pack.applyLayers(), pb.points[0])
  pb.drawHull(color = Color.BLUE, width = 5)
#
d = i.show()
i.save("pillsresult.png")
