from SimpleCV import *
scale_amount = (200,150)
d = Display(scale_amount)
cam = Camera(1)
prev = cam.getImage().scale(scale_amount[0],scale_amount[1])
time.sleep(0.5)
def movement_check(x = 0,y = 0,t=1):
	direction = ""
	directionX = ""
	directionY = ""	
	if x > t:
		directionX = "Right"
	if x < -1*t:
		directionX = "Left"
	if y < -1*t:
		directionY = "Up"
	if y > t:
		directionY = "Down"

	direction = directionX + " " + directionY
	if direction is not "":
		return direction
	else:
		return "No Motion"

t = 0.5
buffer = 20
count = 0
while d.isNotDone():
	current = cam.getImage().scale(scale_amount[0],scale_amount[1])
	if( count < buffer ):
		count = count + 1
	else:
		fs = current.findMotion(prev, window=15, method="BM")
		if fs:
			fs.draw(color=Color.RED)
			dx = 0
			dy = 0
			for f in fs:
				dx = dx + f.dx
				dy = dy + f.dy
				
			dx = (dx / len(fs))
			dy = (dy / len(fs))
			motionStr = movement_check(dx,dy,t)
			current.drawText(motionStr,10,10)

	prev = current
	time.sleep(0.01)
	current.save(d)
