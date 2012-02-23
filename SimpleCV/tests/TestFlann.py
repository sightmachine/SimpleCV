from SimpleCV import *
w = 800
h = 600
data_path = "./../sampleimages/"
display = Display(resolution = (w,h))
spath = data_path + "/data/structured/"
ball_path = spath+"ball/"
basket_path = spath+"basket/"
boat_path = spath+"boat/"
cactus_path = spath +"cactus/"
cup_path = spath+"cup/"
duck_path = spath+"duck/"
gb_path = spath+"greenblock/"
match_path = spath+"matches/"
rb_path = spath+"redblock/"
s1_path = spath+"stuffed/"
s2_path = spath+"stuffed2/"
s3_path = spath+"stuffed3/"
logo_path = spath+"logo/"

#  [0.3360040567951319, 0.37035158891142661, 0.24431626098715353, 0.10554006085192696, 0.23206135902636918, 0.14729124408384045]

tpath = spath+"KeypointTemplate.jpg"
template = Image(tpath)
template.save(display)
time.sleep(1)
paths = [logo_path,boat_path,basket_path,cactus_path,cup_path,duck_path]
results = []
for p in paths:
    print "Doing Data Set: " + p
    local = []
    files = glob.glob( os.path.join(p, '*.jpg'))
    for f in files:
        img = Image(f)
        r = img.keypointMatch(template)
        print r
        local.append(r)
        img.drawText(str(r),10,10,color=Color.RED)
        img.save(display)

    overall = np.average(local)
    print "Overall Result"
    print overall 
    results.append(overall)
print results 
