#!/usr/bin/python 
from SimpleCV import *
import flickrapi

"""
This is a simple demo which uses the up/down and left/right keyboard arrows
to show the thresholds of the edges() function.

It will also snap a picture and upload it to flickr if the API
credentials are correct
"""

import sys, curses
#start values for the edges function
api_key = '3db81c1c0bba17b6f9b36c7edbd8cabd'
api_secret = '48b028b3a5c07791'
flickr = flickrapi.FlickrAPI(api_key, api_secret)
_flickr_setup = False

def init_flickr():

  (token, frob) = flickr.get_token_part_one(perms='write')
  if not token: raw_input("Press ENTER after you authorized this program")
  flickr.get_token_part_two((token, frob))
  _flickr_setup = True


def uploader(progress, done):
    if done:
        print "Done uploading"
    else:
        print "At %s%%" % progress


def main(stdscr):
  stdscr.nodelay(1)
  t1 = 50 
  t2 = 100 
  cam = Camera()
  js = JpegStreamer()

  while (1):
    c = stdscr.getch() 
    if (c != -1):
        if (c == 259):
          t1 += 5
        elif (c == 258):
          t1 -= 5
        elif (c == 260):
          t2 -= 5
        elif (c == 261):
          t2 += 5
        elif (c == 115):
          fname = "/tmp/tmp_flickr_upload.jpg"
          cam.getImage().flipHorizontal().edges(t1, t2).invert().smooth().save(fname)
          flickr.upload(filename=fname, tags='ingenuitas', callback=uploader)
	if (t1 < 0):
          t1 = 0
        if (t2 < 0):
          t2 = 0

        stdscr.addstr(str(int(c)))
	stdscr.addstr("t1: " + str(t1) + ", t2 "+ str(t2) + "\n")
        stdscr.refresh()
	stdscr.move(0, 0)

    cam.getImage().flipHorizontal().edges(t1, t2).invert().smooth().save(js.framebuffer)
		 

if __name__ == '__main__':
  curses.wrapper(main)




