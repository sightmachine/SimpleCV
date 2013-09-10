from ..Base import Display
from ..Base.Display import DisplayBase
from tornado.web import Application
import tornado
from IPython.core.display import Javascript as JS
from IPython.core.display import display
import os
import threading
import tempfile

#string used to initialize a display in javascript
__initString__ = """
console.log('hi')
var win = window.open('/none','window','width = 500,height=500')
win.document.open()
win.document.write('<img src ="http://www.w3schools.com/images/w3schoolslogoNEW310113.gif" />')
alert("hi")
"""
class NBDisplay(Display.DisplayBase):

    _templateFile = "template.html"
    """

    
    """
    init = False
    app = None
    staticDir = None
    def name(self): 
        __doc__ = DisplayBase.name.__doc__
        return "NotebookDisplay"
        
    def __init__(self,size = (640,480),type_ = Display.DEFAULT,title = "SimpleCV",fit = Display.SCROLL):
        if( not NBDisplay.init):
            NBDisplay.init = True
            NBDisplay.staticDir = tempfile.mkdtemp()
            NBDisplay.app = Application(static_path = NBDisplay.staticDir,
            static_url_prefix = "/display/")
            NBDisplay.app.listen(18109)
            threading.Thread(target=tornado.ioloop.IOLoop.instance().start).start()
            
        w,h = size
        fn = os.path.dirname(__file__) + os.sep + NBDisplay._templateFile
        tmp = open(fn)
        raw_lines = tmp.readlines()
        tmp.close()
        lines = [line.replace('\n','') for line in raw_lines]
        template = ''.join(lines)
        
        self.startStr = """
        window.disp = window.open('','','width=%d,height=%d')
        window.disp.document.write("%s")
        """ % (w,h,template)
        
        display(JS(self.startStr))
        
        
    def close(self):
        pass

    def showImage(self,img):
    
        uid = img.getUID()
        img.save(NBDisplay.staticDir + os.sep + str(uid%10) + '.png' )
        print uid%10
        w = img.width
        h = img.height
        command = "window.disp.show(%d,%d,%d)" % (uid,w,h)
        display(JS(command))

    def mousePosition(self):
        """
        **SUMMARY**
        
        Reutrns the mouse pointer potion as a tuple of (x,y), with respect to
        the image coordinates

        **RETURNS**
        
        An (x,y) mouse postion tuple .
        
        """
        pass
        
    def mousePositionRaw(self):
        """
        **SUMMARY**
        
        Reutrns the mouse pointer potion as a tuple of (x,y), with respect to
        the display coordinates
        
        **RETURNS**
        
        An (x,y) mouse postion tuple .
        
        """
        pass
    
    def leftDown(self):
        """
        **SUMMARY**
        
        Reutrns the position where the left mouse button last went down,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the left mouse button went down.
        
        """

    def leftUp(self):
        """
        **SUMMARY**
        
        Reutrns the position where the left mouse button last went up,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the left mouse button went up.
        
        """

    def rightDown(self):
        """
        **SUMMARY**
        
        Reutrns the position where the right mouse button last went down,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the right mouse button went down.
        
        """
        
    def rightUp(self):
        """
        **SUMMARY**
        
        Reutrns the position where the right mouse button last went up,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the right mouse button went up.
        
        """
        
    def middleDown(self):
        """
        **SUMMARY**
        
        Reutrns the position where the middle mouse button last went down,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the middle mouse button went down.
        
        """
        
    def middleUp(self):
        """
        **SUMMARY**
        
        Reutrns the position where the middle mouse button last went up,None 
        if it didn't since the last time this fucntion was called
        
        **RETURNS**
        
        An (x,y) mouse postion tuple where the middle mouse button went up.
        
        """


