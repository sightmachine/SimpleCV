from multiprocessing import Process,Pipe
import os



class GtkWorker(Process):
    
    _gladeFile = "main.glade"
    def __init__(self,connection):
        pass
   
    def run(self):
        import gtk
        self.gtk = gtk
        
        builder = gtk.Builder()

        path = os.path.dirname(__file__) + os.sep + GtkWorker._gladeFile
        
        builder.add_from_file(path)
        builder.connect_signals(self)
        self.window = builder.get_object("window")
        self.image = builder.get_object("image")
        self.image.set_from_file("lenna.png")
        self.window.show_all()
        gtk.main()
        
        
    def destroy(self,widget,data=None):
        self.gtk.main_quit()
