from path import path
from yapsy2 import PluginManager2
import logging
import platform

log = logging.getLogger(__name__)

class PluginLoaderError(Exception):
    pass

class PluginLoader(object):
    def __init__(self, default_preference=[]):
        places = [path(__file__).dirname() / 'plugins']
        ext = 'conf'
    
        self.pm = pm = PluginManager2()
        #pm = PluginManagerSingleton.get()
        pm.setPluginInfoExtension(ext)
        pm.setPluginPlaces(places)
        pm.locatePlugins()
        self.all_names = [ x[2].name for x in pm.getPluginCandidates()]
        #pm.loadPlugins()
    
        #all = pm.getAllPlugins()
        #for x in all:
        #    x.plugin_object.name = x.name

        self.changed = True
        self._force_backend = None
        self.preference = []
        self.default_preference = default_preference
        self._backend = None
        
    def set_preference(self, x):
        self.changed = True
        self.preference = x

    def force(self, name):
        log.debug('forcing:' + str(name))
        self.changed = True
        self._force_backend = name
    
    @property
    def is_forced(self):
        return self._force_backend is not None
            
    @property
    def loaded_plugins(self):
        return [x.plugin_object for x in self.pm.getAllPlugins()]     
        
    def get_valid_plugin_by_name(self, name):
        return self.pm.loadPluginByName(name)
#        x = self.pm.activatePluginByName(name)
#        if x:
#            if hasattr(x, 'is_valid'):
#                if not x.is_valid:
#                    x = None
#            else:
#                if hasattr(x, 'validate'):
#                    try:
#                        log.debug('validating:' + name)
#                        x.validate()
#                        x.is_valid = True
#                        log.debug('success')
#                    except Exception, detail:
#                        log.debug('error:' + str(detail))
#                        x.is_valid = False
#                        x = None
#                else:
#                    x.is_valid = True
#        return x
    
    def get_valid_plugin_by_list(self, ls):
        for name in ls:
            x = self.get_valid_plugin_by_name(name)
            if x :
                return x
    
    def selected(self):
        if self.changed:
            if self.is_forced:
                b = self.get_valid_plugin_by_name(self._force_backend)
                if not b:
                    raise PluginLoaderError('Forced backend not found, or cannot be loaded:' + self._force_backend)
            else:
                biglist = self.preference + self.default_preference + self.all_names
                b = self.get_valid_plugin_by_list(biglist)
                if not b:
                    self.raise_exc()
            self.changed = False
            self._backend = b
            log.debug('selecting plugin:' + self._backend.name)
        return self._backend
    
    def raise_exc(self):
        message = 'Install at least one backend!' 
#        for x in self.loaded_plugins():
#            message += '\n'
#            message += '[%s]' % (x.name)
#            if hasattr(x, 'home_url'):
#                home_url = x.home_url
#                message += '\n'
#                message += '%s' % (home_url)
#            message += '\n'
#            if hasattr(x, 'ubuntu_package'):
#                if platform.dist()[0].lower() == 'ubuntu':
#                    message += 'You can install it in terminal:'
#                    message += '\n'
#                    message += '\t'
#                    message += 'sudo apt-get install %s' % x.ubuntu_package
        raise PluginLoaderError(message)
    
    
     
