from multiprocessing import Process,Pipe
import os
from ..Base import DisplayBase



class GtkWorker(Process):
    """
    A Process for handling a single Display window. Each GtkDisplay window has
    one instance of this class. For each task the GtkDisplay sends a message
    to it's GtkWorker.
    
    Each GUI function (*) in GtkDisplay has a corresponding handle_* method in
    GtkWorker . 
    
    eg. GtkDisplay.showImage() correspons to GtkWorker.handle_showImage()
    
    
    """
    _gladeFile = "main.glade"
    def __init__(self,connection,size,type_,title,fit):
        self.connection = connection
        self.size = size
        self.fit = fit
        self.title = title
        self.type_ = type_
        Process.__init__(self)
   
    def run(self):
        #Gtk imports have to be done in run, Otherwise Gtk thknks there are
        #multiple copies of itself
        import gtk
        import gobject
        self.gtk = gtk
        
        
        #Loads the GUI from file and connects signals
        builder = gtk.Builder()
        path = os.path.dirname(__file__) + os.sep + GtkWorker._gladeFile
        builder.add_from_file(path)
        builder.connect_signals(self)
        
        
        self.window = builder.get_object("window")
        self.image = builder.get_object("image")
        
        if(self.type_ == DisplayBase.FULLSCREEN):
            self.window.fullscreen()
        else:
            self.image.set_size_request(*self.size)
            self.window.set_resizable(False)

        self.window.set_title(self.title)
        self.window.show_all()
        
        #calls pollMsg when gtk is idle
        gobject.idle_add(self.pollMsg,None)
        gtk.main()
        
    def pollMsg(self,data=None):
        
        #check if there is any data to be read, wait for 100ms
        #Is used because select.select/poll and gobject.idle_add dont work on windows
        dataThere = self.connection.poll(.10)
        
        #handle data if it's there
        if(dataThere):
            self.checkMsg()
            
        #required so that event handler stays enabled
        return True
        
    def checkMsg(self):
        
        #examine the message and figure out what to do with it
        msg = self.connection.recv()
        
        funcName = "handle_" + msg['function']
        funcToCall = self.__getattribute__(funcName)
        funcToCall(msg) 
            
    def handle_showImage(self,data):
        #show image from string
        pix =  self.gtk.gdk.pixbuf_new_from_data(data['data'], self.gtk.gdk.COLORSPACE_RGB, False, data['depth'], data['width'], data['height'], data['width']*3)
        self.image.set_from_pixbuf(pix)
        
        #
        #if(self.type_ == DisplayBase.DEFAULT):
        self.image.set_size_request(data['width'],data['height'])
        #elif(self.type_ == DisplayBase.FIXED):
            #pass
        
        #print self.image.size_request()
        
    def handle_close(self,widget,data=None):
        self.connection.send('Kill Me')
        self.window.hide()
        
        #Calling gtk.main_quit() stalls the parent application. This is because
        #The child quits and parent blocks till the child ca receive
        #
        #Instead we send the parent a message so that it terminates the child.
        #This we the child can continue to receive a message that the parent 
        #might be sending and the parent knows exactly when the display is 
        #closed
        
        
        
