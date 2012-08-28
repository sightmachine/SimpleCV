from yapsy.IPlugin import IPlugin
import Image
import wx

class WxScreen(IPlugin):
    '''based on: http://stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-linux
    '''
    #home_url = 'http://???'
    #ubuntu_package = '???'
    def __init__(self):
        self.app=None
        
    def grab(self, bbox=None):
        if not self.app:
            self.app = wx.App()
        screen = wx.ScreenDC()
        size = screen.GetSize()
        bmp = wx.EmptyBitmap(size[0], size[1])
        mem = wx.MemoryDC(bmp)
        mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
        del mem
        myWxImage = wx.ImageFromBitmap( bmp )
        im = Image.new( 'RGB', (myWxImage.GetWidth(), myWxImage.GetHeight()) )
        im.fromstring( myWxImage.GetData() )
        if bbox:
            im = im.crop(bbox)
        return im

    def grab_to_file(self, filename):
        #bmp.SaveFile('screenshot.png', wx.BITMAP_TYPE_PNG)
        im = self.grab()
        im.save(filename)
        
    def backend_version(self):
        return wx.__version__
