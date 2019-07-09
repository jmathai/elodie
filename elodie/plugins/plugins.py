"""
Plugin object.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function
from builtins import object

from importlib import import_module
from sys import exc_info
from traceback import format_exc

from elodie.config import load_config_for_plugin, load_plugin_config
from elodie import log

class ElodiePluginError(Exception):
    pass


class PluginBase(object):

    __name__ = 'PluginBase'

    def __init__(self):
        self.config_for_plugin = load_config_for_plugin(self.__name__)

    def after(self, file_path, destination_folder, final_file_path, media):
        pass

    def before(self, file_path, destination_folder, media):
        pass

    def log(self, msg):
        log.info(msg)



class Plugins(object):
    """A class to execute plugin actions."""

    def __init__(self):
        self.plugins = []
        self.classes = {}
        self.loaded = False

    def load(self):
        """Load plugins from config file.
        """
        # If plugins have been loaded then return
        if self.loaded == True:
            return

        plugin_list = load_plugin_config()
        for plugin in plugin_list:
            plugin_lower = plugin.lower()
            try:
                # We attempt to do the following.
                #  1. Load the module of the plugin.
                #  2. Instantiate an object of the plugin's class.
                #  3. Add the plugin to the list of plugins.
                #  
                #  #3 should only happen if #2 doesn't throw an error
                this_module = import_module('elodie.plugins.{}.{}'.format(plugin_lower, plugin_lower))
                self.classes[plugin] = getattr(this_module, plugin)()
                # We only append to self.plugins if we're able to load the class
                self.plugins.append(plugin)
            except:
                log.error('An error occurred initiating plugin {}'.format(plugin))
                log.error(format_exc())

        self.loaded = True

    def run_all_before(self, file_path, destination_folder, media):
        self.load()
        """Process `before` methods of each plugin that was loaded.
        """
        pass_status = True
        for cls in self.classes:
            this_method = getattr(self.classes[cls], 'before')
            # We try to call the plugin's `before()` method.
            # If the method explicitly raises an ElodiePluginError we'll fail the import
            #  by setting pass_status to False.
            # If any other error occurs we log the message and proceed as usual.
            # By default, plugins don't change behavior.
            try:
                this_method(file_path, destination_folder, media)
            except ElodiePluginError as err:
                log.warn('Plugin {} raised an exception: {}'.format(cls, err))
                log.error(format_exc())
                pass_status = False
            except:
                log.error(format_exc())
        return pass_status

    def run_all_after(self, file_path, destination_folder, final_file_path, media):
        pass
