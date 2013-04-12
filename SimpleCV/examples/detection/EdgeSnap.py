'''
This example illustrated the edgeSnap function in the Image class

Left-click to define points for snapping ( Blue )
Right-click to start the process, Detected Edge points will be shown in Red

'''
from SimpleCV import *



img = Image("shapes.png",sample = True)


disp = Display((img.width,img.height))

img.drawText("Left Click to choose points, right click to find Edge POints", 10,10,color=Color.BLACK,fontsize=20)


points = []

img.save(disp)
while not disp.isDone():

	time.sleep(0.01)
	left = disp.leftButtonDownPosition()
	right = disp.rightButtonDownPosition()


	if(left != None ):
		img.drawCircle((left[0],left[1]),3,Color.BLUE,-1)
		img.save(disp)
		points += [left]

	if(right != None ):		
		draw = img.edgeSnap(points,2)
		l = range(len(draw) - 1)
		for i in l:
			img.drawLine(draw[i],draw[i+1],Color.RED,2)
		img.save(disp)
		points = []
