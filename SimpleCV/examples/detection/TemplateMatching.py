from SimpleCV import *
import sys, time, socket

source = Image("../sampleimages/templatetest.png")

template = Image("../sampleimages/template.png")
t = 5

methods = ["SQR_DIFF","SQR_DIFF_NORM","CCOEFF","CCOEFF_NORM","CCORR","CCORR_NORM"]
for m in methods:
    print m 
    result = Image("../sampleimages/templatetest.png")
    dl = DrawingLayer((source.width,source.height))
    fs = source.findTemplate(template,threshold=t,method=m)
    #fs.draw()
    for match in fs:
        dl.rectangle((match.x,match.y),(match.width(),match.height()),color=Color.RED)
    result.addDrawingLayer(dl)
    result.applyLayers()
    result.show()
    time.sleep(3)

source.save("templateout.png")
