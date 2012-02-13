from SimpleCV import *


d = Display()
cam = Camera()
scale_amount = 0.5
prev = cam.getImage().scale(scale_amount)

time.sleep(0.5)


def movement_check(x = 0,y = 0):
	direction = ""
	directionX = ""
	directionY = ""
	
	if x > 1:
		directionX = "moving right"
	if x < 0:
		directionX = "moving left"
	if y < 0:
		directionY = "moving up"
	if y > 1:
		directionY = "moving down"

	direction = directionX + "," + directionY
	

	if direction is not "":
		print "direction:",direction

while d.isNotDone():
	current = cam.getImage().scale(scale_amount)
	
	fs = current.findMotion(prev, window=7)

	if fs:
		dx = 0
		dy = 0
		for f in fs:
			dx = dx + f.dx
			dy = dy + f.dy

		dx = (dx / len(fs))
		dy = (dy / len(fs))

		movement_check(dx,dy)

	time.sleep(0.1)
	current.save(d)
