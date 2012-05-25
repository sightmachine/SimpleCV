#!/usr/bin/python

from SimpleCV import * 
import scipy.spatial as ss
import pickle 
import copy
dispSz = (640+480,480)
disp = Display(dispSz)
pg.display.toggle_fullscreen()
print "LOADING CAM 2"
cam = Camera(2)
time.sleep(1)
tempimg = cam.getImage()
print "LOADING CAM 1"
faceCam = Camera(1)
time.sleep(1)

pg.mixer.init()
acheer = pg.mixer.Sound("cheer2.wav")
aBeep = pg.mixer.Sound("beep.wav")
aBeep2 = pg.mixer.Sound("beep2.wav")
shutter = pg.mixer.Sound("shutter.wav")


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

def play_slideshow( disp, imgset, timestep,sound=None):
    if( sound is not None):
        sound.play()
    for img in imgset:
        img.save(disp)
        time.sleep(timestep)
        if( sound is not None):
            sound.play()
    if( sound is not None):
        sound.play()
    return

def doLeaderBoard( leaders, faceCam, disp, haarface,  thresh=2):
    # loop the leader board until we see a face
    pg.mixer.music.load("final.mid")
    pg.mixer.music.play(-1)
    facecount = 0
    l = len(leaders)
    i = 0
    start = time.time()
    while facecount < thresh or time.time()-start < 10.0 : #Runs for 30s 
        facecount = 0
        tmp = leaders[i]
        img = tmp[1]
        i = i + 1
        if( i >= l  ):
            i = 0
        img.save(disp)
        t0 = time.time()
        while( time.time()-t0 < 1.0):
            img = faceCam.getImage().resize(320,240)
            f = img.findHaarFeatures(face)
            if( f is not None ):
                facecount = facecount + 1 
        
    pg.mixer.music.stop()

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
        entry = leaderboard[i] 
        if mytime < entry[0]:
            return i
    return -1

def updateLeaderboard( leaderboard, mytime, myimage, place ):
    leaderboard.insert(place,(mytime,myimage))
    if( len(leaderboard) > 10 ):
        leaderboard  = leaderboard[0:10]
    return leaderboard

def doConfirmation( faceCam, disp ):
    dialog = Image("confirm.png")
    mask = Image("confirmMask.png")
    gotResult = False
    last = faceCam.getImage().resize(640,480)
    rhs = 0
    lhs = 0 
    framecount = 7
    lhs_threshold = 300000
    rhs_threshold = 300000
    retVal = False
    start = time.time()
    while( not gotResult ):
        img = faceCam.getImage().resize(640,480).flipVertical().flipHorizontal()
        output = img.blit(dialog,mask=mask)
        diff = last-img
        diff = diff.threshold(20)
        last = img
        output.save(disp)
        lhs_activity = np.sum(diff[0:200,0:120].getNumpy())
        rhs_activity = np.sum(diff[440:639,0:120].getNumpy())
        #print "activity: " + str((lhs_activity,rhs_activity))  
        if( (rhs_activity > rhs_threshold or lhs_activity > lhs_threshold)):
            aBeep2.play()
            if( rhs_activity > lhs_activity ):
                rhs = rhs + 1
            else:
                lhs = lhs + 1
        if( lhs > framecount ):
            gotResult = True
            retVal = True
        elif( rhs > framecount ):
            gotResult = True
            retVal = True

        if(time.time()-start > 60.00):
            gotResult = True
            retVal = False
        time.sleep(.01)
    return retVal 
    
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
fail = ImageSet("./fail/")


#haar resources

face = HaarCascade("../../Features/HaarCascades/face.xml") 

mode = "leaderboard"
gamestart = time.time()
gameOver = False
leaderboard = loadLeaderBoard()

while disp.isNotDone():
    if( mode == "leaderboard"):
        doLeaderBoard(leaderboard,faceCam, disp, face)
        mode = "confirm"
        
    if( mode == "directions" ):
        play_slideshow(disp, directions, 5,aBeep)
        mode = "rsg"

    if( mode == "confirm"):
        if( doConfirmation( cam, disp ) ):
            mode = "directions" 
        else:
            mode = "leaderboard"
        

    if( mode == "rsg" ):
        play_slideshow(disp, rsg, 1, sound=aBeep)
        mode = "playgame"

        gameOver = False
        pg.mixer.music.load("tick.wav")
        pg.mixer.music.play(-1)
        gameIndex = random.randrange(0,len(gametemplates))
        model = createOutputImage(gametemplates[gameIndex],template)
        gamestart = time.time()
        good = False
        
    if( mode == "playgame"):
        t = cam.getImage().resize(640,480).flipVertical().flipHorizontal()
        mask = t.colorDistance(Color.WHITE).binarize().invert().dilate(4)
        blobs = t.findBlobsFromMask(mask,minsize=t.width*t.height*0.2)
        output = t
        if( blobs is not None and blobs[-1].area() > (t.width*t.height*.5)):
            cm = getColorMatrix(t,blobs)
            if( cm is not None ):
                result = estimateColorMatrix(cm)
                bigcm = result.scale(10)
                output = output.blit(bigcm)
                good = userImageIsCorrect(result,gametemplates[gameIndex])
                if( good ):
                    gameOver = True
                    gameTime = time.time()-gamestart
                    mode = "postgame"
                output = renderResult( t, good, greencheck,greencheckm,redx,redxm) 
                output = model.sideBySide(output)
        else:        
            output = model.sideBySide(output)
        tt = time.time()-gamestart
        ttstr = "Elapsed Time %2.0f" % (tt,)
        output.drawText(ttstr,30,30,color=Color.WHITE,fontsize=50)
        output.save(disp)
        if( good ): #display the results for a few extra second for feedback
            acheer.play()
            for i in range(0,20):
                t = cam.getImage().resize(640,480).flipVertical().flipHorizontal()
                mask = t.colorDistance(Color.WHITE).binarize().invert().dilate(4)
                blobs = t.findBlobsFromMask(mask,minsize=t.width*t.height*0.2)
                output = t
                if( blobs is not None and blobs[-1].area() > (t.width*t.height*.3)):
                    cm = getColorMatrix(t,blobs)
                    if( cm is not None ):
                        result = estimateColorMatrix(cm)
                output = renderResult( t, good, greencheck,greencheckm,redx,redxm) 
                output = model.sideBySide(output)
                output.save(disp)
        if( not good and time.time()-gamestart > 120.00 ):
            pg.mixer.music.stop()
            play_slideshow(disp, fail, 5, sound=aBeep)
            mode = "confirm"
        time.sleep(0.01)
        
    if( mode == "postgame" ):
        pg.mixer.music.stop()
        ts =  "%2.2f seconds" % (tt,)
        timeScore = postgame[0].copy()
        timeScore.drawText(ts,200,240,color=Color.GREEN,fontsize=150)
        endshow = [timeScore, postgame[1],postgame[2],postgame[3]]
        play_slideshow(disp, endshow ,2,aBeep)
        rank = placesOnLeaderBoard(leaderboard,gameTime) 
        for i in range(0,30):
            frame = Image("winner.png")
            frameMask = Image("winnerMask.png")
            lbimg = faceCam.getImage().resize(640,480)
            lbimg = lbimg.blit(frame,mask=frameMask)
            lbimg.drawText(ts,200,420,color=Color.BLACK,fontsize=50)
            lbimg.save(disp)

        shutter.play()
        time.sleep(5)
        if( rank > -1 ):
            leaderboard = updateLeaderboard( leaderboard, gameTime, lbimg, rank )
            saveLeaderBoard( leaderboard )
            
        mode = "leaderboard"
    
