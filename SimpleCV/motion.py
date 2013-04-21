import cv2.cv as cv
import numpy,threading,time
'''
This python code draws contour for all the objects that are in motion in the video. Helps in Motion detection
'''
imageArray=[]
 
def diff(img1,img2):
        '''
        this method returns the absolute difference b/w two images
        '''
        import cv2
        b1=cv.CreateImage((img1.width,img1.height),img1.depth,1)
        cv.AbsDiff(img1,img2,b1)
        #cv.ShowImage("abs", b1)
        img=b1
        
        return b1
                
def detection():
        global imageArray
        cam = cv.CaptureFromCAM( 0 )
        cv.SetCaptureProperty(cam,cv.CV_CAP_PROP_FRAME_WIDTH, 1300)
        cv.SetCaptureProperty(cam,cv.CV_CAP_PROP_FRAME_HEIGHT, 768)
        while 1:
                x=cv.QueryFrame(cam)
                '''
                captures first image
                '''
                t1=cv.CreateImage((x.width,x.height),x.depth,1)
                cv.CvtColor(x,t1,cv.CV_RGB2GRAY)
                x=cv.QueryFrame(cam)
                '''
                captures next image
                '''
                t2=cv.CreateImage((x.width,x.height),x.depth,1)
                cv.CvtColor(x,t2,cv.CV_RGB2GRAY)
                '''
                two images passed to method diff to get absolute difference
                '''
                ret=diff(t1,t2)
                cv.Smooth(ret,ret,cv.CV_GAUSSIAN,25,0)
                cv.Threshold(ret,ret,15,255,cv.CV_THRESH_BINARY)
                cv.Dilate(ret,ret, None, 15)
                cv.Erode(ret, ret, None, 10)
                storage = cv.CreateMemStorage(0)
                '''
                finding contours
                '''
                
                contour = cv.FindContours(ret, storage, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_SIMPLE)
                '''
                drawing contour
                '''
                
                cv.DrawContours (x,contour, (0, 0, 255), (0, 255, 0), 1, 2, cv.CV_FILLED)      
                while contour:
                        bound_rect = cv.BoundingRect(list(contour))
                        contour = contour.h_next()
                        pt1 = (bound_rect[0], bound_rect[1])
                        pt2 = (bound_rect[0] + bound_rect[2], bound_rect[1] + bound_rect[3])
                        if abs(pt1[0]-pt2[0]) > 100 and abs(pt1[1]-pt2[1]) > 100:
                                cv.Rectangle(x, pt1, pt2, cv.CV_RGB(255,0,0), 1)
                                print abs(pt1[0]-pt2[0]),abs(pt1[1]-pt2[1])
                cv.ShowImage("Threshold", x)
                key=cv.WaitKey(30)
                if key == 27:
                        exit(0)
               
if __name__=='__main__':
        detection()
