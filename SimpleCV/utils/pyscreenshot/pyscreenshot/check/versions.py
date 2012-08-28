from pyscreenshot.backendloader import BackendLoader
import pyscreenshot
from entrypoint2 import entrypoint

def print_name(name):
    print name, ' '*(20-len(name)),

@entrypoint
def print_versions():
    print_name('pyscreenshot')
    print pyscreenshot.__version__
    man=BackendLoader()
    for name in man.all_names:
        man.force(name)
        print_name(name)
        try :
            x=man.selected()
            print x.backend_version()
        except Exception:
            print 'missing'

