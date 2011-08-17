#!/usr/bin/python 
import os
import glob
from SimpleCV import *
from numpy import *

def BuildWidthHistogram( img, bins ):
    raw_vals = []
    #for each line going down the image
    for i in range(0,img.height):
        #we get the scanline, i.e. the pixels
        scanline = img.getHorzScanlineGray(i)
        #we find the location of all the white pixels
        
        points = np.where(scanline>0)
        #and if there are two of them
        if( points[0].shape[0] > 2 ):
            #we save the distance between the two
            w = points[0][-1]-points[0][0]
            # and add that to our array
            raw_vals.append(w)
    # and return a normalized histgram of the results
    print(raw_vals)
    return np.histogram(raw_vals,bins, normed = True)
    
def BuildHeightHistogram( img, bins ):
    raw_vals = []
    #for each line going down the image
    for i in range(0,img.width):
        #we get the scanline, i.e. the pixels
        scanline = img.getVertScanlineGray(i)
        #we find the location of all the white pixels
        points = np.where(scanline>0)
        #and if there are two of them
        if( points[0].shape[0] > 2 ):
            #we save the distance between the two
            w = points[0][-1]-points[0][0]
            # and add that to our array
            raw_vals.append(w)
    # and return a normalized histgram of the results
    return np.histogram(raw_vals,bins, normed = True)    
        
def ExtractFeatures( fname, outbase, colormodel ):
    img = Image(fname)
    #try to smooth everything to get rid of noise
    #img = img.medianFilter()
    #do an adaptive binary operation
    blurr = img.smooth(aperature=9)
    #blobs = img.binarize(thresh = -1, blocksize=21,p=3)
    blobs = colormodel.threshold(img)
 
    #blobs = blobs.dilate(0)
    #default behavior is black on white, invert that 
    #blobs = blobs.invert()
    blobs = blobs.dilate(2);
    blobs.save('derp1.png')
    #grow the blob images a little bit
    #t = outbase + "blob.png"
    #blobs.save(t)
    #also perform a canny edge detection
    edges = img.edges()
    #also grow that a little bit to fill in gaps
    #edges = edges.dilate(2)
    edges.save('edge.png')
    #t = outbase + "edge.png"
    #edges.save(t)
    #now reinforce the image, we only want edges that are in both, so we multiply
    mult = blobs
    #mult = mult.erode(4)
    #mult.save(t)
    #now we grow the result 
    mult.save('derp.png')
    blobmaker = BlobMaker()
    chunks = blobmaker.extract(mult)
    mult.clear()
    chunks[0].drawHull(color=(255,255,255))
    #mult.applyLayers()
    #t = outbase + "mult.png"
    #mult.save(t)
    mult.save("mult0.png")
    if( len(chunks) == 0 ):
        mult.save("BadImage.png")
        warnings.warn("BAD IMAGE: "+fname)
        return None 
    # we take the center blob
    (x,y) = chunks[0].center()
    # and the blobs rotation, the 90- is to get the battery so it is vertical
    angle = chunks[0].angle()
    # now we rotate the blob so that the major axis is parallel to the sides of our image
    print(angle)
    print((x,y))
    print(chunks[0].width())
    print(chunks[0].height())
    
    mult = mult.applyLayers()
    mult = mult.rotate(angle,point=(x,y),mode='full')
    mult.save("rotated.png")
    # now we reapply the blobbing on the straightened image
    # chunks = mult.findBlobs(threshval=-1)   
    if( len(chunks) == 0 ):
        mult.save("BadImage.png")
        warnings.warn("BAD IMAGE: "+fname)
        return None 
    # now we crop the image to emlinate a lot of the noise and other junk
    # we crow the blob by 1/5th its original width and 1/10th its height
    #chunks = blobmaker.extract(mult)
    #mult.clear()
    #chunks[0].drawHull(color=(255,255,255))   
   
    #w = chunks[0].width()
    #h = chunks[0].height()
    #(cx,cy) = chunks[0].center()
    #cx = chunks[0].cvblob.minx+(w/2)
    #cy = chunks[0].cvblob.miny+(h/2)
    #mult = mult.crop(cx,cy,w,h,centered=True)
    #now we do an erode since we did so much dilation
    #mult = mult.erode()
    #finally we save the image
    #t = outbase + ".png"
    mult.save('final.png')
    #and build the edge histogram
    hhist = BuildWidthHistogram( mult, 10 )
    data = hhist[0]
    vhist = BuildHeightHistogram(mult,10)
    data = np.append(data,vhist[0])
    chunks = mult.findBlobs(threshval=-1)
    data = np.append(data,chunks[0].m00)
    data = np.append(data,chunks[0].m10)
    data = np.append(data,chunks[0].m01)
    data = np.append(data,chunks[0].m11)
    data = np.append(data,chunks[0].m02)
    data = np.append(data,chunks[0].m20)
    data = np.append(data,chunks[0].m21)
    data = np.append(data,chunks[0].m12)
    return data

dataset = np.array([])
tempFile = 'goodtemp.csv'
path = './batteries/good/'
i = 0
colorModel = ColorModel()
colorModel.add(Image('./batteries/background/bg0.png'))
print(len(colorModel.mData))
#colorModel.add(Image('./batteries/background/bg1.png'))
print(len(colorModel.mData))
#colorModel.add(Image('./batteries/background/bg2.png'))
print(len(colorModel.mData))
#colorModel.add(Image('./batteries/background/bg3.png'))
print(len(colorModel.mData))


#for every file on our good directory
for infile in glob.glob( os.path.join(path, '*.png') ):
    print "Opening File: " + infile
    #output string
    outfile = 'GoodResult' + str(i) #+ ".png"
    #we built the histogram / feature vector
    data = ExtractFeatures(infile, outfile,colorModel)
    if( data != None ):
        #We append the class label zero for good, one for bad
        data = np.append(data,0)
        #now we append the data onto our final dataset
        if( i == 0 ):
            dataset = data
        else:
            dataset = np.row_stack((dataset,data))
    i = i+1
    #use save text to write our file out
    savetxt(tempFile,dataset,delimiter=',')

#now do the same for the bad data




path = './batteries/bad/'
for infile in glob.glob( os.path.join(path, '*.png') ):
    print "Opening File: " + infile
    #output string
    outfile = 'BulgedResult' + str(i) #+ ".png"
    #we built the histogram
    data = ExtractFeatures(infile, outfile,colorModel)
    if( data != None ):
        data = np.append(data,1) #bad data is given label one
        if( i == 0 ):
            dataset = data
        else:
            dataset = np.row_stack((dataset,data))
    i = i+1
    savetxt(tempFile,dataset,delimiter=',')
