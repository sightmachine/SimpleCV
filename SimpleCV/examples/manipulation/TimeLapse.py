from SimpleCV import *
import glob

path= "./burrito_challenge/"
stem = "burrito"
ext = "*.jpg"
files = glob.glob( os.path.join(path, ext) )
print files 
c = len(files)
rate = 5
cam = Camera(1)

while True:
    img = cam.getImage().resize(640,480)
    fname = path + stem + str(c) + ".jpg"
    img.save(fname)
    img.show()
    print "frame: " + str(c)
    time.sleep(rate) 
    c = c + 1
    
