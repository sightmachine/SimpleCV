from SimpleCV import Image, Display,Camera,Color
import glob,os
import pygame as pg
from CardUtil import SUITS, RANKS, MISC
#SUITS = ('c', 'd', 'h', 's')
#RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A')
#MISC = ( 'none','bad','joker')

disp = Display((640,480))
cam = Camera()

path = "./data/"
ext = ".png"
suit_ptr = 0
rank_ptr = 0
current_dir = ""
allDone = False
for s in SUITS:
    for r in RANKS:
        directory = path+s+"/"+r+"/"
        if not os.path.exists(directory):
            os.makedirs(directory)
print "Current Data: " + str(RANKS[rank_ptr])+str(SUITS[suit_ptr])
while not allDone :
    keys = disp.checkEvents()
    img = cam.getImage()
    for k in keys:
        if( k == pg.K_SPACE ):
            directory = path+SUITS[suit_ptr]+"/"+RANKS[rank_ptr]+"/"
            files = glob.glob(directory+"*.*")
            count = len(files)
            fname = directory+RANKS[rank_ptr]+SUITS[suit_ptr]+"-"+str(count)+ext
            img.save(fname)
            print "Saved: " + fname
        if( k == pg.K_n ):
            if rank_ptr == len(RANKS)-1 and suit_ptr == len(SUITS)-1:
                allDone = True
            elif rank_ptr == len(RANKS)-1:
                rank_ptr = 0
                suit_ptr = suit_ptr + 1
            else:
                print rank_ptr
                rank_ptr = rank_ptr + 1
        print "Current Data" + str(RANKS[rank_ptr])+str(SUITS[suit_ptr])

    img.drawLine((0,img.height/4),(img.width,img.height/4),color=Color.RED,thickness=3)
    img.drawLine((0,3*img.height/4),(img.width,3*img.height/4),color=Color.RED,thickness=3)
    img.drawLine((img.width/3,0),(img.width/3,img.height),color=Color.RED,thickness=3)
    img.drawLine((2*img.width/3,0),(2*img.width/3,img.height   ),color=Color.RED,thickness=3)
    img.save(disp)
