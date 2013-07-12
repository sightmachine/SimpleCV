#!/usr/bin/python
'''
This example shows how to perform various rotations and warps on images
and put back into a display.
'''
print __doc__

from SimpleCV import *

font_size = 30
sleep_for = 3 #seconds to sleep for
draw_color = Color.RED


while True:
    image = Image("orson_welles.jpg", sample=True)
    image.drawText("Original Size", 10,10, color=draw_color, fontsize=font_size)
    image.show()
    time.sleep(sleep_for)

    rot = image.rotate(45)
    rot.drawText("Rotated 45 degrees", 10,10, color=draw_color, fontsize=font_size)
    rot.show()
    time.sleep(sleep_for)

    rot = image.rotate(45, scale=0.5)
    rot.drawText("Rotated 45 degrees and scaled", 10,10, color=draw_color, fontsize=font_size)
    rot.show()
    time.sleep(sleep_for)

    rot = image.rotate(45,scale=0.5, point = (0,0) )
    rot.drawText("Rotated 45 degrees and scaled around a point", 10,10, color=draw_color, fontsize=font_size)
    rot.show()
    time.sleep(sleep_for)

    rot = image.rotate(45,"full")
    rot.drawText("Rotated 45 degrees and full", 10,10, color=draw_color, fontsize=font_size)
    rot.show()
    time.sleep(sleep_for)

    atrans = image.shear([(image.width/2,0),(image.width-1,image.height/2),(image.width/2,image.height-1)])
    atrans.drawText("Affine Transformation", 10,10, color=draw_color, fontsize=font_size)
    atrans.show()
    time.sleep(sleep_for)

    ptrans = image.warp([(image.width*0.05,image.height*0.03),(image.width*0.9,image.height*0.1),(image.width*0.8,image.height*0.7),(image.width*0.2,image.height*0.9)])
    ptrans.drawText("Perspective Transformation", 10,10, color=draw_color, fontsize=font_size)
    ptrans.show()
    time.sleep(sleep_for)
