from pyscreenshot.backendloader import BackendLoader
import logging

__version__ = '0.2.2'

log = logging.getLogger(__name__)
log.debug('version=' + __version__)

def grab(bbox=None):
    '''Copy the contents of the screen to PIL image memory.
    
    :param bbox: optional bounding box
    '''  
    return BackendLoader().selected().grab(bbox)

def grab_to_file(filename):  
    '''Copy the contents of the screen to a file.
    
    :param filename: file for saving
    '''  
    return BackendLoader().selected().grab_to_file(filename)



