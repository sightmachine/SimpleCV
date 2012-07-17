from SimpleCV import *

img = Image("goodfile.jpg")
img.crop(-1, -1, 1, 1)
#WARNING: Crop will try to help you, but you have a negative crop position,
#your width and height may not be what you want them to be.

set_logging(4)
#Sets logging threshold to 4 (only CRITICAL and ERROR messages are shown)

img.crop(-1, -1, 1, 1)
#Warning message is not displayed.

bad_img = Image("BADFILE.jpg")

#Big error message displayed, as the file doesn't exist. Most important part:
#IOError: [Errno 2] No such file or directory: 'BADFILE.jpg'

set_logging(3, "logfile.out")
#Now logging to logfile.out with level 3 (includes CRITICAL, ERROR and WARNING)

bad_img = Image("BADFILE.jpg")
#Error message dumped to logfile.out (and isn't displayed anymore)
