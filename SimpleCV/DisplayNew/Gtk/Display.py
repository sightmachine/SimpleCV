
from ..Base import DisplayBase
from ..Base import DisplayNotFoundException
from Worker import GtkWorker
from multiprocessing import Pipe


class GtkDisplay(DisplayBase):
    
    def name(self):
        return "GtkDisplay"
        self.worker
        
        
    def __init__(self,size = (640,480),type_ = DisplayBase.DEFAULT,title = "SimpleCV",fit = DisplayBase.RESIZE):
        DisplayBase.__init__(self,size,type_,title,fit)
        parentConnection,childConnnection = Pipe()
        
        
        self.type_ = type_
        self.fit = fit
        
        #Initializing a Worker, A process to handle one display
        self.worker = GtkWorker(childConnnection,size,type_,title,fit)
        self.connection = parentConnection
        self.worker.start()
        self.workerAlive= True
        
        
    def close(self):
        pass
        
    def _checkIfWorkerDead(self):
        if(self.connection.poll()):
            if(self.connection.recv() == 'Kill Me' ):
                print "rec"
                # " Hasta La Vista , Baby "
                # http://www.youtube.com/watch?v=DMGh82QHVcQ
                self.worker.terminate()
                self.workerAlive = False
                

    def showImage(self,img):
        self._checkIfWorkerDead()
        
        if(self.type_ == DisplayBase.FIXED ):
            if(self.fit == DisplayBase.RESIZE):
                img = img.adaptiveScale(self.size,True)
            elif(self.fit == DisplayBase.CROP):
                img = img.adaptiveScale(self.size,False)
            else:
                #TODO raise an exception here maybe, cause many other functions
                #may get a value they are not expecting
                pass
        
        if(self.workerAlive):
            dic = {}
            dic['function'] = 'showImage'
            dic['data'] = img.toString()
            dic['depth'] = img.depth
            dic['width'] = img.width
            dic['height'] = img.height
            self.connection.send(dic)
        else:
            raise DisplayNotFoundException(self)
        

