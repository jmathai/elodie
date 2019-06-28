"""
Plugin object.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function
from builtins import object

from sys import exc_info
from importlib import import_module

from elodie.config import load_config
from elodie import log


class Plugins(object):
    """A class to execute plugin actions."""

    def __init__(self):
        self.plugins = []
        self.classes = {}

    def load(self):
        """Load plugins from config file.
        """
        config = load_config()
        if 'Plugins' in config and 'plugins' in config['Plugins']:
            config_plugins = config['Plugins']['plugins'].split(',')
            for plugin in config_plugins:
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
                    log.warn('Some error occurred initiating plugin {} - {}'.format(plugin, exc_info()[0]))
                    continue


    def run_all_before(self, file_path, destination_path, media):
        """Process `before` methods of each plugin that was loaded.
        """
        for cls in self.classes:
            this_method = getattr(self.classes[cls], 'before')
            this_method(file_path, destination_path, media)
