from SimpleCV import Camera, VideoStream, Color, Display
from subprocess import call # to run command line programs
"""
This script requires ffmpeg and googlecl

googlecl / google command line can be found at:
https://code.google.com/p/googlecl/

To install googlecl download the source and run:
sudo python setup.py install

You will then need to get a youtube API key
You can get your key here:
https://developers.google.com/youtube/2.0/developers_guide_protocol

Install your api key by copying it to:
~/.local/share/googlecl/yt_devkey
All you do create a file called yt_devkey and
paste the key into the file.
The first time you run the script you will need to authorize
googlecl to use your account. 

ffmpeg can be found here http://www.ffmpeg.org/
see the ffmpeg website for installation instructions


"""
fname = 'test.avi'
outname = 'output.mp4'
tags = 'SimpleCV, Computer Vision, Python'
title = "SimpleCV Output"
summary = "See http://simplecv.org for more info."
access = "public" # Options are "public" "private" "protected"
# create the video stream for saving the video file
vs = VideoStream(fps=20,filename=fname,framefill=False)
# grab the camera
cam = Camera()
# create a display
disp = Display((800,600))
# while the user does not press 'esc'
while disp.isNotDone():
    # YOUR CODE GOES HERE!
    img = cam.getImage()
    img = img.edges()
    # write the frame
    vs.writeFrame(img)
    # save the image to the display
    img.save(disp)
# construct the encoding arguments
params = " -i {0} {1}".format(fname,outname)
# run ffmpeg to compress your video.
call('ffmpeg'+params,shell=True)
# construct the command line arguments for google command line
params = "{0} --title \"{1}\" --tags \"{2}\" --category \"Education\" --summary \"{3}\" --access \"{4}\" ".format(outname,title,tags,summary,access)
print params
# call the command line
call('google youtube post '+params,shell=True)
