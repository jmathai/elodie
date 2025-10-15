"""
Plugin object.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function
from builtins import object

import io

from json import dumps, loads
from importlib import import_module
from os.path import dirname, dirname, isdir, isfile
from os import mkdir
from sys import exc_info
from traceback import format_exc

from elodie.compatability import _bytes
from elodie.config import load_config_for_plugin, load_plugin_config
from elodie.constants import application_directory
from elodie import log


class ElodiePluginError(Exception):
    """Exception which can be thrown by plugins to return failures.
    """
    pass


class PluginBase(object):
    """Base class which all plugins should inherit from.
       Defines stubs for all methods and exposes logging and database functionality
    """
    __name__ = 'PluginBase'

    def __init__(self):
        # Loads the config for the plugin from config.ini
        self.config_for_plugin = load_config_for_plugin(self.__name__)
        self.db = PluginDb(self.__name__)

    def after(self, file_path, destination_folder, final_file_path, metadata):
        pass

    def batch(self):
        pass

    def before(self, file_path, destination_folder):
        pass

    def log(self, msg):
        # Writes an info log not shown unless being run in --debug mode.
        log.info(dumps(
            {self.__name__: msg}
        ))

    def display(self, msg):
        # Writes a log for all modes and will be displayed.
        log.all(dumps(
            {self.__name__: msg}
        ))

class PluginDb(object):
    """A database module which provides a simple key/value database.
       The database is a JSON file located at %application_directory%/plugins/%pluginname.lower()%.json
    """
    def __init__(self, plugin_name):
        self.db_file = '{}/plugins/{}.json'.format(
            application_directory(),
            plugin_name.lower()
        )

        # If the plugin db directory does not exist, create it
        if(not isdir(dirname(self.db_file))):
            mkdir(dirname(self.db_file))

        # If the db file does not exist we initialize it
        if(not isfile(self.db_file)):
            with io.open(self.db_file, 'wb') as f:
                f.write(_bytes(dumps({})))


    def get(self, key):
        with io.open(self.db_file, 'r') as f:
            db = loads(f.read())

        if(key not in db):
            return None

        return db[key]

    def set(self, key, value):
        with io.open(self.db_file, 'r') as f:
            data = f.read()
            db = loads(data)

        db[key] = value
        new_content = dumps(db, ensure_ascii=False).encode('utf8')
        with io.open(self.db_file, 'wb') as f:
            f.write(new_content)

    def get_all(self):
        with io.open(self.db_file, 'r') as f:
            db = loads(f.read())
        return db

    def delete(self, key):
        with io.open(self.db_file, 'r') as f:
            db = loads(f.read())

        # delete key without throwing an exception
        db.pop(key, None)
        new_content = dumps(db, ensure_ascii=False).encode('utf8')
        with io.open(self.db_file, 'wb') as f:
            f.write(new_content)


class Plugins(object):
    """Plugin object which manages all interaction with plugins.
       Exposes methods to load plugins and execute their methods.
    """

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

    def run_all_after(self, file_path, destination_folder, final_file_path, metadata):
        """Process `before` methods of each plugin that was loaded.
        """
        self.load()
        pass_status = True
        for cls in self.classes:
            this_method = getattr(self.classes[cls], 'after')
            # We try to call the plugin's `before()` method.
            # If the method explicitly raises an ElodiePluginError we'll fail the import
            #  by setting pass_status to False.
            # If any other error occurs we log the message and proceed as usual.
            # By default, plugins don't change behavior.
            try:
                this_method(file_path, destination_folder, final_file_path, metadata)
                log.info('Called after() for {}'.format(cls))
            except ElodiePluginError as err:
                log.warn('Plugin {} raised an exception in run_all_before: {}'.format(cls, err))
                log.error(format_exc())
                log.error('false')
                pass_status = False
            except:
                log.error(format_exc())
        return pass_status

    def run_batch(self):
        self.load()
        pass_status = True
        for cls in self.classes:
            this_method = getattr(self.classes[cls], 'batch')
            # We try to call the plugin's `before()` method.
            # If the method explicitly raises an ElodiePluginError we'll fail the import
            #  by setting pass_status to False.
            # If any other error occurs we log the message and proceed as usual.
            # By default, plugins don't change behavior.
            try:
                this_method()
                log.info('Called batch() for {}'.format(cls))
            except ElodiePluginError as err:
                log.warn('Plugin {} raised an exception in run_batch: {}'.format(cls, err))
                log.error(format_exc())
                pass_status = False
            except:
                log.error(format_exc())
        return pass_status

    def run_all_before(self, file_path, destination_folder):
        """Process `before` methods of each plugin that was loaded.
        """
        self.load()
        pass_status = True
        for cls in self.classes:
            this_method = getattr(self.classes[cls], 'before')
            # We try to call the plugin's `before()` method.
            # If the method explicitly raises an ElodiePluginError we'll fail the import
            #  by setting pass_status to False.
            # If any other error occurs we log the message and proceed as usual.
            # By default, plugins don't change behavior.
            try:
                this_method(file_path, destination_folder)
                log.info('Called before() for {}'.format(cls))
            except ElodiePluginError as err:
                log.warn('Plugin {} raised an exception in run_all_after: {}'.format(cls, err))
                log.error(format_exc())
                pass_status = False
            except:
                log.error(format_exc())
        return pass_status
