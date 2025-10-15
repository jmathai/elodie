"""
Settings used by Elodie.
"""

from os import environ, path
from sys import version_info

#: If True, debug messages will be printed.
debug = False

#: Directory in which to store Elodie settings.
def application_directory():
    """Get the application directory, checking environment variable each time."""
    default_dir = '{}/.elodie'.format(path.expanduser('~'))
    if (
            'ELODIE_APPLICATION_DIRECTORY' in environ and
            path.isdir(environ['ELODIE_APPLICATION_DIRECTORY'])
       ):
        return environ['ELODIE_APPLICATION_DIRECTORY']
    return default_dir

#: File in which to store details about media Elodie has seen.
def hash_db():
    """Get the hash database path."""
    return '{}/hash.json'.format(application_directory())

#: File in which to store geolocation details about media Elodie has seen.
def location_db():
    """Get the location database path."""
    return '{}/location.json'.format(application_directory())

#: Elodie installation directory.
script_directory = path.dirname(path.dirname(path.abspath(__file__)))

#: Path to Elodie's ExifTool config file.
exiftool_config = path.join(script_directory, 'configs', 'ExifTool_config')

#: Path to MapQuest base URL
mapquest_base_url = 'https://www.mapquestapi.com'
if (
        'ELODIE_MAPQUEST_BASE_URL' in environ and
        environ['ELODIE_MAPQUEST_BASE_URL'] != ''
    ):
    mapquest_base_url = environ['ELODIE_MAPQUEST_BASE_URL']

#: MapQuest key from environment
mapquest_key = None
if (
        'ELODIE_MAPQUEST_KEY' in environ and
        environ['ELODIE_MAPQUEST_KEY'] != ''
   ):
    mapquest_key = environ['ELODIE_MAPQUEST_KEY']

#: Accepted language in responses from MapQuest
accepted_language = 'en'

# check python version, required in filesystem.py to trigger appropriate method
python_version = version_info.major
