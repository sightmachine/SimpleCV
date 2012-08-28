from entrypoint2 import entrypoint
from pyscreenshot.backendloader import BackendLoader
from pyscreenshot.loader import PluginLoaderError
from pyvirtualdisplay.display import Display
import pyscreenshot
import time

# they make exceptions that can not be catched
SKIP=['pygtk','wx','pyqt']


def run(force_backend, bbox, bgcolor):
    color=255 if bgcolor=='white' else 0
    print force_backend, ' '*(20 - len(force_backend)),
    if force_backend in SKIP:
        print 'SKIP'
        return
    
    BackendLoader().force(force_backend)
    im=pyscreenshot.grab(bbox=bbox)
    ls=list(im.getdata())
    print 'OK' if all([x==color or x==(color,color,color) for x in ls]) else 'FAIL'


def run_all(bgcolor, display, bbox):
    print 
    print 'bgcolor=',bgcolor
    print '-------------------------------------'
    backends = BackendLoader().all_names
    for x in backends:
        try:
            with Display(size=display, bgcolor=bgcolor):
#                time.sleep(1)
                try:
                    run(x, bbox, bgcolor=bgcolor)
                except PluginLoaderError as e:
                    print e
        except Exception as e:
            print e
        


@entrypoint
def main():
    bbox = (15, 15, 120, 120)
    display = (200, 200)
    run_all('black',display,bbox)
    run_all('white',display,bbox)


