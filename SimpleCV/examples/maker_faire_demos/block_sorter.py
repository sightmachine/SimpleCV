#!/usr/bin/python

from SimpleCV import * 
import scipy.spatial as ss

disp = Display((1200,600))
cam = Camera(1)
tempimg = cam.getImage()
scale_f = 0.4

def getColorMatrix(t,blobs):
    h = blobs[-1].hullImage()
    h = h.rotate(blobs[-1].angle())
    mask = h.threshold(1).dilate(5)
    b2 = h.findBlobsFromMask(mask, threshold=1)
    if( b2 is not None):
        h2 = b2[-1].hullImage()
        h3 = h2.crop( 20,20, h2.width-40,h2.height-40)
        h4 = h3.pixelize((h3.width/4,h3.height/4),mode=True)
        h5 = h3.pixelize((h3.width/4,h3.height/4),mode=False)
        return(h4,h5)
    else:
        return None
    
def estimateColorMatrix(t, shape=(4,4), palette = [Color.RED, Color.LEGO_ORANGE, Color.GREEN, Color.LEGO_BLUE] ):
    retVal = Image(shape)
    wstep = t.width/shape[0]
    hstep = t.height/shape[1]
    w0 = wstep/2
    h0 = hstep/2
    tree = ss.KDTree(np.array(palette))
    for i in range(0,shape[0]):
        for j in range(0,shape[1]):
            x=w0+(i*wstep)
            y=h0+(j*hstep)
            test = t[x,y] 
            best = tree.query(test)
            retVal[i,j] = palette[best[1]]
    return retVal.rotate90().flipHorizontal() 


def createOutputImage(colors,template,shape=(4,4)):
    w = template.width
    h = template.height
    wstep = w/shape[0]
    hstep = h/shape[1]
    retVal = Image((w,h))
    for i in range(0,shape[0]):
        for j in range(0,shape[1]):
            myColor = colors[i,j]
            retVal[(i*wstep):((i+1)*wstep),(j*hstep):((j+1)*hstep)] = myColor
             
    retVal = retVal.blit(template,alphaMask = template.invert() )
    return retVal
    
def userImageIsCorrect( userImage, truthImage ):
    img00 = userImage - truthImage
    img90 = userImage.rotate90().flipVertical() - truthImage
    img180 = userImage.flipVertical().flipHorizontal() - truthImage
    img270 = userImage.rotate90().flipHorizontal() - truthImage
    r00 = np.sum(img00.getNumpy())
    r90 = np.sum(img90.getNumpy())
    r180 = np.sum(img180.getNumpy())
    r270 = np.sum(img270.getNumpy())
    threshold = 0.50
    print [r00,r90,r180,r270]
    retVal = False
    if( r00 < threshold or r90 < threshold or r180 < threshold or r270 < threshold):
        retVal = True
    return retVal

def renderResult( userImg, isCorrect, correct, correctMask, incorrect, incorrectMask):
    if(isCorrect):
        result = userImg.blit(correct,pos=(150,150),mask=correctMask)
    else:
        result = userImg.blit(incorrect,pos=(150,150),mask=incorrectMask)
    return result

maskh = 600
tempimg = tempimg.resize(maskh,maskh)
template = Image("template.png")


redx = Image("redx.png")
redxm = redx.binarize().invert()
greencheck = Image("greencheck.png")
greencheckm = greencheck.binarize()

gametemplates = ImageSet("./truthdata/")

while disp.isNotDone():
    t = cam.getImage().scale(scale_f)
    mask = t.colorDistance(Color.WHITE).binarize().invert().dilate(4)
    blobs = t.findBlobsFromMask(mask,minsize=t.width*t.height*0.2)
    output = t
    if( blobs is not None ):
        t = t.applyLayers()
        (result2,cm) = getColorMatrix(t,blobs)
        if( cm is not None ):
            result = estimateColorMatrix(cm)
            model = createOutputImage(result,template)
            #model = model.rotate(-90)
            #output = t
            good = userImageIsCorrect(result,gametemplates[0])
            output = renderResult( t, good, greencheck,greencheckm,redx,redxm) 
            #result = result.resize(50,50)
            #output = t.blit(result)
            #output = output.blit(cm.resize(50,50),(0,51))
            #outut = output.blit(result2.resize(50,50),(0,102))
            
            output = model.sideBySide(output)
            blobs[-1].draw(width=3)
        
    output.save(disp)
    time.sleep(0.1)
    
