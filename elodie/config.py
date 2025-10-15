"""Load config file as a singleton."""
from configparser import RawConfigParser
from os import path

from elodie import constants

def get_config_file():
    """Get the config file path."""
    return '%s/config.ini' % constants.application_directory()


def load_config():
    if hasattr(load_config, "config"):
        return load_config.config

    config_file = get_config_file()
    if not path.exists(config_file):
        return {}

    load_config.config = RawConfigParser()
    load_config.config.read(config_file)
    return load_config.config

def load_plugin_config():
    config = load_config()

    # If plugins are defined in the config we return them as a list
    # Else we return an empty list
    if 'Plugins' in config and 'plugins' in config['Plugins']:
        return config['Plugins']['plugins'].split(',')

    return []

def load_config_for_plugin(name):
    # Plugins store data using Plugin%PluginName% format.
    key = 'Plugin{}'.format(name)
    config = load_config()

    if key in config:
        return config[key]

    return {}
