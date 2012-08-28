from easyprocess import EasyProcess
from easyprocess import extract_version
from yapsy.IPlugin import IPlugin
import Image
import tempfile

PROGRAM = 'import'
URL = 'http://www.imagemagick.org/'
PACKAGE = 'imagemagick'

EasyProcess([PROGRAM, '-version'], url=URL, ubuntu_package=PACKAGE).check_installed()

class ImagemagickWrapper(IPlugin):
    def __init__(self):
        pass
        
    def grab(self, bbox=None):
        f = tempfile.NamedTemporaryFile(suffix='.png', prefix='screenshot_imagemagick_')
        filename = f.name
        self.grab_to_file(filename, bbox=bbox) 
        im = Image.open(filename)
        #if bbox:
        #    im = im.crop(bbox)
        return im

    def grab_to_file(self, filename, bbox=None):
        command = 'import -window root '  
        if bbox:
            command += " -crop '%sx%s+%s+%s' " % (bbox[2] - bbox[0], bbox[3] - bbox[1], bbox[0], bbox[1])
        command += filename
        EasyProcess(command).call()
        
    def backend_version(self):
        return extract_version(EasyProcess([PROGRAM, '-version']).call().stdout.replace('-',' '))
