#!/usr/bin/python

import time
from SimpleCV import *

def check_eyes(eyes):
    return (eyes and len(eyes) >= 2)

def process_eyes(image, eyes):
    dx, dy = eyes[-1].coordinates() - eyes[-2].coordinates()

    if dx > 0:
        right_eye = eyes[-2]
    else:
        dx = -1*dx
        right_eye = eyes[-1]

    if dx > image.width/15: #Reduces amount of wrong matches
        return (dx, dy, right_eye)
    else:
        return (None, None, None)


def draw_glasses(image, (dx, dy, right_eye), glasses):
    rotation = 0.5*dy
    try:
        new_glasses = glasses.scale(int(2.75*dx), right_eye.height())
        mask = new_glasses.invert()
        
        new_glasses = new_glasses.rotate(rotation, fixed = False)
        mask = mask.rotate(rotation, fixed=False)

        image = image.blit(new_glasses, right_eye.topLeftCorner(),alphaMask=mask)
    except:
        pass

    return image.flipHorizontal()

def main():

    glasses = Image('deal_with_it.png', sample=True).flipHorizontal()
    c = Camera()
    found = False


    while True:

        image = c.getImage().scale(0.5).flipHorizontal()
        eyes = image.findHaarFeatures("eye")

        if check_eyes(eyes):
            new_position = process_eyes(image, eyes) 
            if new_position[0]:
                found = True
                position = new_position

        if found:
            image = draw_glasses(image, position, glasses)
        else:
            image = image.flipHorizontal()

        image.show()

if __name__ == "__main__":
    main()
