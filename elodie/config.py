"""Load config file as a singleton."""
from configparser import RawConfigParser
from os import path

from . import constants

config_file = '%s/config.ini' % constants.application_directory


def load_config():
    if hasattr(load_config, "config"):
        return load_config.config

    if not path.exists(config_file):
        return {}

    load_config.config = RawConfigParser()
    load_config.config.read(config_file)
    return load_config.config
