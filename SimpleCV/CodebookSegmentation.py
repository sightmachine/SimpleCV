# THIS IS SCRATCH CODE
# STAY AWAY


img = Image("./SimpleCV/sampleimages/aerospace.jpg")
numpyImg = img.getNumpy()
shape = img.getNumpy().shape
linear_img = img.getNumpy().reshape(shape[0]*shape[1],3)
linear_list = linear_img.tolist()

from collections import namedtuple
CodebookCode = namedtuple('CodebookCode',['yMax','yMin','yLearnHigh','yLearnLow','uMax','uMin','uLearnHigh','uLearnLow','vMax','vMin','vLearnHigh','vLearnLow','lastUpdate','stale'] )

def Codecheck( code, pixel ):
    return( pixel[0] >= code.yLearnHigh and
            pixel[0] <= code.yLearnLow and
            pixel[1] >= code.uLearnHigh and
            pixel[1] <= code.uLearnLow and
            pixel[2] >= code.vLearnHigh and
            pixel[2] <= code.vLearnLow )
    
def IntCodecheck(codebook,pixel):
    #go through the codebook and return 255 if the pixel
    derp = 0 
    
def UpdateCodebook( codebook, pixel, count, bounds ):
    # count = c.t
    for i in range(3):
        low[i] = max(pixel[i]-bounds[i],0)
        high[i] = min(pixel[i]+bounds[i],255)
    
    #filter() such that the resulting codebook code is updateCode
    updatecode = filter(lambda x: Codecheck(x,pixel), codebook)

    #update the results
    if( updateCode is not None ):
        if(updateCode.maxY < pixel[0] ):
            updateCode.maxY = pixel[0]
        elif( updateCode.minY > pixel[0] ):
            updateCode.minY = pixel[0] 
    
        if(updateCode.maxU < pixel[1] ):
            updateCode.maxU = pixel[1]
        elif( updateCode.minU > pixel[1] ):
            updateCode.minU = pixel[1]
        
        if(updateCode.maxV < pixel[2] ):        
            updateCode.maxV = pixel[2]
        elif( updateCode.minV > pixel[2] ):
            updateCode.minV = pixel[2] 
        # update the negative entries
        
        #this is the last step... is this right?
        if(updateCode.yLearnHigh < high[0] ):
            updateCode.yLearnHigh+=1
        if(updateCode.yLearnLow > low[0] ):
            updateCode.yLearnLow-=1
        if(updateCode.uLearnHigh < high[1] ):
            updateCode.uLearnHigh+=1
        if(updateCode.uLearnLow > low[1] ):
            updateCode.uLearnLow-=1
        if(updateCode.vLearnHigh < high[2] ):
            updateCode.vLearnHigh+=1
        if(updateCode.vLearnLow > low[2] ):
            updateCode.vLearnLow-=1
            
        for cbc in codebook:
            negrun = count - cbc.lastUpdate
            if(cbc.stale < negrun ):
                cbc.stale = negrun
        
    else:#finally add a new value to the codebook
        newCode = CodebookCode( pixel[0],pixel[0],high[0],low[0],
                                pixel[1],pixel[1],high[1],low[1],
                                pixel[2],pixel[2],high[2],low[2],
                                count,0)
        codebook.append(newCode)
    return codebook

def purge_codebook(codebook, thresh):
    #thresh is c.t>>1
    retVal = [] 
    for codes in codebook:
        if codes.stale < thresh:
            codes.lastUpdate = 0 
            retVal.append(codes)


#NEED TO GET ACTUAL THRESHOLD OPERATION

#make the list of codebooks that is image widthxheight
#convert the image to yuv, linearize
#need the count array 
#map the lambda function of update codebook to the input pixel array and the codebook
#map(lambda x,y: Codecheck(x,y), image, codebook)
