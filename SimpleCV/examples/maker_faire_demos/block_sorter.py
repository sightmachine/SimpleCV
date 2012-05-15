#!/usr/bin/python

from SimpleCV import * 
import scipy.spatial as ss
import pickle 
dispSz = (640+480,480)
disp = Display(dispSz)
cam = Camera(2)
faceCam = Camera(1)
tempimg = cam.getImage()
#scale_f = 0.4

def getColorMatrix(t,blobs):
    h = blobs[-1].hullImage()
    h = h.rotate(blobs[-1].angle())
    mask = h.threshold(1).dilate(5)
    b2 = h.findBlobsFromMask(mask, threshold=1)
    if( b2 is not None):
        h2 = b2[-1].hullImage()
        h3 = h2.crop( 20,20, h2.width-40,h2.height-40)
        #h4 = h3.pixelize((h3.width/4,h3.height/4),mode=True)
        h5 = h3.pixelize((h3.width/4,h3.height/4),mode=False)
        return h5
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
    #write the color matrix to the template for rendering
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

def play_slideshow( disp, imgset, timestep):
    for img in imgset:
        img.save(disp)
        time.sleep(timestep)
    return

def doLeaderBoard( leaders, faceCam, disp, haarface,  thresh=10):
    # loop the leader board until we see a face
    facecount = 0
    l = len(leaders)
    i = 0
    while facecount < thresh:
        facecount = 0
        tmp = leaders[i]
        img = tmp[1]
        i = i + 1
        if( i >= l  ):
            i = 0
        img.save(disp)
        t0 = time.time()
        while( time.time()-t0 < 5.0):
            img = faceCam.getImage().resize(320,240)
            f = img.findHaarFeatures(face)
            if( f is not None ):
                facecount = facecount + 1 

def saveLeaderBoard( leaderboard, path="./leaders/"):
    sz = len(leaderboard)
    times = []
    for i in range(0,sz):
        lead = leaderboard[i]
        times.append(lead[0])
        fname = path + str(i) + ".png"
        lead[1].save(fname)
    fname = path+"leaders.pkl"
    pickle.dump( times, open(fname,"wb"))
    
def loadLeaderBoard(path="./leaders/"):
    fname = path + "leaders.pkl"
    times = pickle.load(open(fname,"rb"))
    leaderboard = []
    for i in range(0,len(times)):
        fname = path + str(i) + ".png"
        img = Image(fname)
        leaderboard.append((times[i],img))
    return leaderboard

def placesOnLeaderBoard( leaderboard, mytime):
    boardlen = len(leaderboard)
    for i in range(0,boardlen):
        if mytime < leaderboard[i]:
            return i
    return -1

def updateLeaderboard( leaderboard, mytime, myimage, place ):
    leaderboard.insert(place,(mytime,myimage))
    if( len(leaderboard) > 10 ):
        leaderboard  = leaderboard[0:10]
    return leaderboard
#def madeLeaderBoard( mytime, leaderboard ):

#def replaceLeader( time, img, place, leaderboard):
    
# Load resources
maskh = 600
tempimg = tempimg.resize(maskh,maskh)
template = Image("template.png")

redx = Image("redx.png")
redxm = redx.binarize().invert()
greencheck = Image("greencheck.png")
greencheckm = greencheck.binarize()

gametemplates = ImageSet("./truthdata/")

#screeens 
directions = ImageSet("./directions/")
#leaders = ImageSet("./leaders/")
rsg = ImageSet("./rsg/")
postgame = ImageSet("./postgame/")



#haar resources

face = HaarCascade("../../Features/HaarCascades/face.xml") 

mode = "leaderboard"
gamestart = time.time()
gameOver = False
leaderboard = loadLeaderBoard()

while disp.isNotDone():
    if( mode == "leaderboard"):
        doLeaderBoard(leaderboard,faceCam, disp, face)
        mode = "directions"
        
    if( mode == "directions" ):
        play_slideshow(disp, directions, 5)
        mode = "rsg"

    if( mode == "rsg" ):
        play_slideshow(disp, rsg, 1)
        mode = "playgame"
        model = createOutputImage(gametemplates[0],template)
        gameOver = False
        gamestart = time.time()
        

    if( mode == "playgame"):
        t = cam.getImage().resize(640,480)
        mask = t.colorDistance(Color.WHITE).binarize().invert().dilate(4)
        blobs = t.findBlobsFromMask(mask,minsize=t.width*t.height*0.2)
        output = t
        if( blobs is not None and blobs[-1].area() > (t.width*t.height*.3)):
            cm = getColorMatrix(t,blobs)
            if( cm is not None ):
                result = estimateColorMatrix(cm)
                
                good = userImageIsCorrect(result,gametemplates[0])
                if( good ):
                    gameOver = True
                    gameTime = time.time()-gamestart
                    mode = "postgame"
                output = renderResult( t, good, greencheck,greencheckm,redx,redxm) 
                output = model.sideBySide(output)
        else:        
            output = model.sideBySide(output)
        tt = time.time()-gamestart
        ttstr = "Elapsed Time %2.2f" % (tt,)
        output.drawText(ttstr,30,30,color=Color.WHITE,fontsize=50)
        output.save(disp)
        time.sleep(0.01)
        
    if( mode == "postgame" ):
        play_slideshow(disp, postgame, 5)
        rank = placesOnLeaderBoard(leaderboard,gameTime) 
        if( rank > -1 ):
            lbimg = faceCam.getImage().resize(640,480)
            leaderboard = updateLeaderboard( leaderboard, gameTime, lbimg, rank )
            saveLeaderBoard( leaderboard )
        mode = "leaderboard"
    
