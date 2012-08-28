from yapsy.PluginManager import PluginManager
import logging
import os.path
import sys

log = logging.getLogger(__name__)

class PluginManager2(PluginManager):
    def loadPluginByName(self, name, callback=None):
        """
        """
        if not hasattr(self, '_candidates'):
            raise ValueError("locatePlugins must be called before loadPlugins")

        if not hasattr(self, 'load_cache'):
            self.load_cache=dict()

        if name in self.load_cache:
            return self.load_cache[name]
            
        plugin_object= None
        for candidate_infofile, candidate_filepath, plugin_info in self._candidates:
            if plugin_info.name == name:
                log.debug('plugin found:' + name)
                self._loadPlugin(candidate_infofile, candidate_filepath, plugin_info, callback)                
                plugin_object= plugin_info.plugin_object
                break
        
        if not plugin_object:
            log.debug('plugin not found:' + name)
        
        self.load_cache[name]=plugin_object
        return plugin_object

    def _loadPlugin(self, candidate_infofile, candidate_filepath, plugin_info, callback):
        if hasattr(plugin_info, 'is_loaded') and plugin_info.is_loaded:
            log.debug('plugin already loaded:' + plugin_info.name)
            return
        log.debug('loading:' + plugin_info.name)
        
        # if a callback exists, call it before attempting to load
        # the plugin so that a message can be displayed to the
        # user
        if callback is not None:
            callback(plugin_info)
        # now execute the file and get its content into a
        # specific dictionnary
        candidate_globals = {"__file__":candidate_filepath + ".py"}
        if "__init__" in  os.path.basename(candidate_filepath):
            sys.path.append(plugin_info.path)                
        try:
            candidateMainFile = open(candidate_filepath + ".py", "r")    
            exec(candidateMainFile, candidate_globals)
        except Exception, e:
            log.debug("Unable to execute the code in plugin: %s" % candidate_filepath)
            log.debug("\t The following problem occured: %s %s " % (os.linesep, e))
            if "__init__" in  os.path.basename(candidate_filepath):
                sys.path.remove(plugin_info.path)
            return
        
        if "__init__" in  os.path.basename(candidate_filepath):
            sys.path.remove(plugin_info.path)
        # now try to find and initialise the first subclass of the correct plugin interface
        for element in candidate_globals.itervalues():
            current_category = None
            for category_name in self.categories_interfaces:
                try:
                    is_correct_subclass = issubclass(element, self.categories_interfaces[category_name])
                except:
                    continue
                if is_correct_subclass:
                    if element is not self.categories_interfaces[category_name]:
                        current_category = category_name
                        break
            if current_category is not None:
                if not (candidate_infofile in self._category_file_mapping[current_category]): 
                    # we found a new plugin: initialise it and search for the next one
                    plugin_info.plugin_object = element()
                    plugin_info.category = current_category
                    self.category_mapping[current_category].append(plugin_info)
                    self._category_file_mapping[current_category].append(candidate_infofile)
                    current_category = None
                break
        
        plugin_info.plugin_object.name = plugin_info.name
        plugin_info.is_loaded = True
        log.debug('success:' + plugin_info.name)
