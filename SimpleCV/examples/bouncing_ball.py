#!/usr/bin/python 

import time, sys
from SimpleCV import Camera, Image
import numpy as np
import pygame

pygame.init()

size = width, height = 800, 600
speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

c = Camera()
i = c.getImage()
arr = i.scale(int(width/8),int(height/8)).getNumpy()

ball = pygame.surfarray.make_surface(arr)
ballrect = ball.get_rect()

while 1:
  for event in pygame.event.get():
    if event.type == pygame.QUIT: sys.exit()

  ballrect = ballrect.move(speed)
  if ballrect.left < 0 or ballrect.right > width:
    speed[0] = -speed[0]
  if ballrect.top < 0 or ballrect.bottom > height:
    speed[1] = -speed[1]
  
  arr = c.getImage().flipHorizontal().scale(int(width/8),int(height/8)).getNumpy()
  ball = pygame.surfarray.make_surface(arr)
  
  screen.fill(black)
  screen.blit(ball, ballrect)
  pygame.display.flip()
