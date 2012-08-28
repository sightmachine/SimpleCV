from entrypoint2 import entrypoint
from pyscreenshot.backendloader import BackendLoader
from pyscreenshot.loader import PluginLoaderError
import pyscreenshot
import tempfile
import time


def run(force_backend, n, to_file, bbox=None):
    print force_backend,' '*(20-len(force_backend)),

    BackendLoader().force(force_backend)
        
    f = tempfile.NamedTemporaryFile(suffix='.png', prefix='test')
    filename=f.name
    start = time.time()
    for i in range(n):
        if to_file:
            pyscreenshot.grab_to_file(filename)
        else:
            pyscreenshot.grab(bbox=bbox)
    end = time.time()
    print int(10*(end - start))/10.0, 'sec'

def run_all(n, to_file, bbox=None):
    print
    print 'n=%s' %  n, ', to_file:', to_file,', bounding box:', bbox
    print '------------------------------------------------------'

    backends = BackendLoader().all_names
    for x in backends:
        try:
            run(x, n, to_file, bbox)
#            print 'grabbing by '+x
        except PluginLoaderError as e:
            print e
    

@entrypoint
def speedtest(): 
    n=10   
    run_all(n, True)
    run_all(n, False)
    run_all(n, False, (10,10,20,20))



