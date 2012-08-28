from PyQt4.Qt import QBuffer, QIODevice
from PyQt4.QtGui import QPixmap, QApplication
from yapsy.IPlugin import IPlugin
import Image
import StringIO

class QtGrabWindow(IPlugin):
    '''based on: http://stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-linux
    '''
    #home_url = 'http://???'
    #ubuntu_package = '???'
    def __init__(self):
        self.app=None
        
    def grab_to_buffer(self, buffer, file_type='png'):
        if not self.app:
            self.app = QApplication([])
        qbuffer = QBuffer()
        qbuffer.open(QIODevice.ReadWrite)
        QPixmap.grabWindow(QApplication.desktop().winId()).save(qbuffer, file_type)
        buffer.write(qbuffer.data())
        qbuffer.close()
#        del app

    def grab(self, bbox=None):
        strio = StringIO.StringIO()
        self.grab_to_buffer(strio)
        strio.seek(0)
        im = Image.open(strio)
        if bbox:
            im = im.crop(bbox)
        return im

    def grab_to_file(self, filename):
        file_type = "png"
        if filename.endswith('.jpeg'):
            file_type = "jpeg"
        buff = open(filename, 'wb')
        self.grab_to_buffer(buff, file_type)
        buff.close()
        
    def backend_version(self):
        # TODO:
        return 'not implemented'
