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
        points = np.where(scanline==255)
        #and if there are two of them
        if( points[0].shape[0] > 2 ):
            #we save the distance between the two
            w = points[0][-1]-points[0][0]
            # and add that to our array
            raw_vals.append(w)
    # and return a normalized histgram of the results        
    return np.histogram(raw_vals,bins, normed = True)
        
def ExtractFeatures( fname, outbase ):
    img = Image(fname)
    #try to smooth everything to get rid of noise
    img = img.medianFilter()
    #do an adaptive binary operation
    #blurr = img.smooth(aperature=3)
    #blurr = blurr.binarizeAdaptive()
    #t = outbase + "blur.png"
    #blurr.save(t) 
    blobs = img.binarizeAdaptive()
    blobs = blobs.erode()
    #default behavior is black on white, invert that 
    blobs = blobs.invert()
    #grow the blob images a little bit
    #blobs = blobs.dilate(1)
    #t = outbase + "blob.png"
    #blobs.save(t)
    #also perform a canny edge detection
    edges = img.edges()
    #also grow that a little bit to fill in gaps
    edges = edges.dilate()
    #t = outbase + "edge.png"
    #edges.save(t)
    #now reinforce the image, we only want edges that are in both, so we multiply
    mult = edges*blobs
    #now we grow the result 
    #mult = mult.dilate()
    #now we get the "blobs"
    chunks = mult.findBlobs()
    # we take the center blob
    x = (chunks[0].cvblob.maxx - chunks[0].cvblob.minx)/2
    y = (chunks[0].cvblob.maxy - chunks[0].cvblob.miny)/2
    # and the blobs rotation, the 90- is to get the battery so it is vertical
    angle = 90-chunks[0].angle()
    # now we rotate the blob so that the major axis is parallel to the sides of our image
    mult = mult.rotate(-1*angle,point=(x,y))
    # now we reapply the blobbing on the straightened image
    chunks = mult.findBlobs()
    if( len(chunks) == 0 ):
        mult.save("SuckyImage.png")
        warnings.warn("BAD IMAGE: "+fname)
        return None 
    # now we crop the image to emlinate a lot of the noise and other junk
    # we crow the blob by 1/5th its original width and 1/10th its height
    w = (chunks[0].cvblob.maxx - chunks[0].cvblob.minx)
    h = (chunks[0].cvblob.maxy - chunks[0].cvblob.miny)
    cx = chunks[0].cvblob.minx+(w/2)
    cy = chunks[0].cvblob.miny+(h/2)
    mult = mult.crop(cx,cy,int(w+(w/5)),int(h+(h/10)),centered=True)
    #now we do an erode since we did so much dilation
    #mult = mult.erode()
    #finally we save the image
    t = outbase + ".png"
    mult.save(t)
    #and build the edge histogram
    hist = BuildWidthHistogram( mult, 10 )
    data = hist[0]
    chunks = mult.findBlobs()
    data = np.append(data,chunks[0].cvblob.m00)
    data = np.append(data,chunks[0].cvblob.m10)
    data = np.append(data,chunks[0].cvblob.m01)
    data = np.append(data,chunks[0].cvblob.m11)
    data = np.append(data,chunks[0].cvblob.m02)
    data = np.append(data,chunks[0].cvblob.m20)
    return data

dataset = np.array([])
path = '../sampleimages/battery/good/'
i = 0
#for every file on our good directory
for infile in glob.glob( os.path.join(path, '*.jpg') ):
    print "Opening File: " + infile
    #output string
    outfile = 'GoodResult' + str(i) #+ ".png"
    #we built the histogram / feature vector
    data = ExtractFeatures(infile, outfile)
    print(data)
    if( data != None ):
        #We append the class label zero for good, one for bad
        data = np.append(data,0)
        #now we append the data onto our final dataset
        if( i == 0 ):
            dataset = data
        else:
            dataset = np.row_stack((dataset,data))
    i = i+1

print(dataset)
#now do the same for the bad data   
path = '../sampleimages/battery/bad/'
for infile in glob.glob( os.path.join(path, '*.jpg') ):
    print "Opening File: " + infile
    #output string
    outfile = 'BadResult' + str(i) #+ ".png"
    #we built the histogram
    data = ExtractFeatures(infile, outfile)
    if( data != None ):
        data = np.append(data,1) #bad data is given label one
        if( i == 0 ):
            dataset = data
        else:
            dataset = np.row_stack((dataset,data))
    i = i+1

myFile = 'data.csv'
tempFile = 'temp.csv'
#use save text to write our file out
savetxt(tempFile,dataset,delimiter=',')
#now open a new file, add the header, pipe in the data file, and then delete it. 
f = open(myFile,'w')
d = open('temp.csv')
f.writelines("hb0, hb1, hb2, hb3, hb4, hb5, hb6, hb7, hb8, hb9, area, m10, m01, m11, m02, m20, label\n")
f.writelines(d.readlines())
f.close()
d.close()
os.remove(tempFile)
