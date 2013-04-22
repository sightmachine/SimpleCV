'''
This example illustrates the edgeSnap function in the Image class

Left-click to define points for snapping ( Blue )
Right-click to start the process, Detected Edge points will be shown in Red

'''
print __doc__

from SimpleCV import *



image = Image("shapes.png",sample = True)
edgeMap = image.edges()

display = Display((image.width,image.height))

edgeMap.drawText("Left Click to choose points, Right click to find Edge Points", 10,10,color=Color.BLACK,fontsize=20)


points = []
image.save(display)

while not display.isDone():

    time.sleep(0.01)
    left = display.leftButtonDownPosition()
    right = display.rightButtonDownPosition()


    if(left != None ):
        image.drawCircle((left[0],left[1]),5,Color.BLUE,-1)
        image.save(display)
        points += [left]

    if(right != None ):
        
        featureSet = edgeMap.edgeSnap(points)
        featureSet.image = image
        if(featureSet):
            featureSet.draw(width = 4,color = Color.RED)
            image.save(display)
        
        points = []






