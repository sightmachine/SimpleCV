from easyprocess import EasyProcess
from easyprocess import extract_version
from yapsy.IPlugin import IPlugin
import Image
import tempfile


PROGRAM='scrot'
URL = None
PACKAGE = 'scrot'

EasyProcess([PROGRAM, '-version'], url=URL, ubuntu_package=PACKAGE).check_installed()

class ScrotWrapper(IPlugin):
    
    def __init__(self):
        pass
    
    def grab(self, bbox=None):
        f = tempfile.NamedTemporaryFile(suffix='.png', prefix='screenshot_scrot_')
        filename = f.name
        self.grab_to_file(filename) 
        im = Image.open(filename)
        if bbox:
            im = im.crop(bbox)
        return im

    def grab_to_file(self, filename):
        EasyProcess([PROGRAM , filename]).call()

    def backend_version(self):
        return extract_version(EasyProcess([PROGRAM,'-version']).call().stdout)
        
