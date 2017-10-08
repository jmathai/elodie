"""Load config file as a singleton."""
from configparser import RawConfigParser
from os import path
from sys import version_info


application_directory = '{}/.elodie'.format(path.expanduser('~'))
config_file = '{}/config.ini'.format(application_directory)
script_directory = path.dirname(path.dirname(path.abspath(__file__)))


def load_config():
    if hasattr(load_config, 'config'):
        print('config')
        return load_config.config

    if not path.exists(config_file):
        print('{}')
        return {}

    load_config.config = RawConfigParser()
    load_config.config.read(config_file)
    load_config.config.add_section(u'Constants')
    for k, v in constants_fallback().iteritems():
        load_config.config.set(u'Constants', k, v)
    return load_config.config


def constants_fallback():
    return {
        #: If True, debug messages will be printed.
        'debug': False,

        #: Directory in which to store Elodie settings.
        'application_directory': '{}/.elodie'.format(path.expanduser('~')),

        #: File in which to store details about media Elodie has seen.
        'hash_db': '{}/hash.json'.format(application_directory),

        #: File in which to store geolocation details about media Elodie has seen.
        'location_db': '{}/location.json'.format(application_directory),

        #: Elodie installation directory.
        'script_directory': script_directory,

        #: Path to Elodie's ExifTool config file.
        'exiftool_config': path.join(script_directory, 'configs', 'ExifTool_config'),

        #: Accepted language in responses from MapQuest
        'accepted_language': 'en',

        # check python version, required in filesystem.py to trigger appropriate method
        'python_version': version_info.major,
    }
