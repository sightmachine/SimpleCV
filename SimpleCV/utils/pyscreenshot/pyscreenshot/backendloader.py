from pyscreenshot.loader import PluginLoader
from pyscreenshot.singl import singleton


default_preference = ['pil', 'scrot', 'wx', 'pygtk', 'pyqt', 'imagemagick']

@singleton 
class BackendLoader(PluginLoader):
    def __init__(self):
        PluginLoader.__init__(self, default_preference)
