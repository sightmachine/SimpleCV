from gtk.gdk import Pixbuf, COLORSPACE_RGB, get_default_root_window
from yapsy.IPlugin import IPlugin
import Image
import gtk
import tempfile

class GtkPixbufWrapper(IPlugin):
    #home_url = 'http://???'
    ubuntu_package = 'python-gtk2'
    def __init__(self):
        pass
        
#    def validate(self):
#        from gtk.gdk import Pixbuf, COLORSPACE_RGB, get_default_root_window

    def grab(self, bbox=None):
        f = tempfile.NamedTemporaryFile(suffix='.png', prefix='screenshot_gtkpixbuf_')
        filename = f.name
        self.grab_to_file(filename) 
        im = Image.open(filename)
        if bbox:
            im = im.crop(bbox)
        return im

    def grab_to_file(self, filename):
        '''
        based on: http://stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-linux
        
        http://www.pygtk.org/docs/pygtk/class-gdkpixbuf.html
        
        only "jpeg" or "png"
        '''
        w = get_default_root_window()
        sz = w.get_size()
        #print "The size of the window is %d x %d" % sz
        pb = Pixbuf(COLORSPACE_RGB, False, 8, sz[0], sz[1]) # 24bit RGB
        pb = pb.get_from_drawable(w, w.get_colormap(), 0, 0, 0, 0, sz[0], sz[1])
        assert pb
        type = "png"
        if filename.endswith('.jpeg'):
            type = "jpeg"
            
        pb.save(filename, type)
        
    def backend_version(self):
        # TODO:
        return '.'.join(map(str,gtk.ver))
