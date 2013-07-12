"""
This examples demonstrates the motionBlur method.
Use Up/Down Arrow keys to change power
Use Left/Right Arrow keys to change angle
"""
print __doc__

from SimpleCV import *
import pygame
import time

img = Image((500,500))
layer = DrawingLayer((500, 500))
layer.setFontSize(25)


layer.rectangle((0,0),(500,500),Color.WHITE,1,True)

#write the text
layer.text("Just some innocent looking dots",(50,25),Color.BLACK)
layer.text("Use Up/Down arrows ro change intensity",(50,50),Color.BLACK)
layer.text("Left/Right arrows to change angle",(50,75),Color.BLACK)

#draw 6 innocent looking dots
layer.circle((125,200),25,Color.RED,1,True)
layer.circle((250,200),25,Color.BLUE,1,True)
layer.circle((375,200),25,Color.GREEN,1,True)
layer.circle((125,300),25,Color.YELLOW,1,True)
layer.circle((250,300),25,Color.ORANGE,1,True)
layer.circle((375,300),25,Color.CYAN,1,True)


#apply layer
img.addDrawingLayer(layer)
img = img.applyLayers()
display = Display()
img.save(display)
power = 1
angle = 0
while not display.isDone():
    time.sleep(0.01)
    
    #detect up,down,left,right keypresses and modify power,angle
    if( pygame.key.get_pressed()[pygame.K_UP] != 0 ):
        power +=10 
        blur = img.motionBlur(power,angle)
        blur.save(display)
    if( pygame.key.get_pressed()[pygame.K_DOWN] != 0 ):
        power = max(power-10,1)
        blur = img.motionBlur(power,angle)
        blur.save(display)
    if( pygame.key.get_pressed()[pygame.K_LEFT] != 0 ):
        angle -= 5
        blur = img.motionBlur(power,angle)
        blur.save(display)
    if( pygame.key.get_pressed()[pygame.K_RIGHT] != 0 ):
        angle += 5
        blur = img.motionBlur(power,angle)
        blur.save(display)
    pass


