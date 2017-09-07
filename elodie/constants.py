"""
Settings used by Elodie.
"""

from os import path
from sys import version_info

try:
    import constants_override
except:
    class constants_override():
        def __getattr__(self, name):
            return None

def get_constant(name, default):
    if(hasattr(constants_override, name)):
        return getattr(constants_override, name)
    else:
        return default

#: If True, debug messages will be printed.
debug = get_constant('debug', False)

#: Directory in which to store Elodie settings.
application_directory = get_constant(
                            'application_directory',
                            '{}/.elodie'.format(path.expanduser('~'))
                        )

#: File in which to store details about media Elodie has seen.
hash_db = get_constant('hash_db', '{}/hash.json'.format(application_directory))

#: File in which to store geolocation details about media Elodie has seen.
location_db = get_constant(
                  'location_db',
                  '{}/location.json'.format(application_directory)
              )

#: Elodie installation directory.
script_directory = get_constant(
                       'script_directory',
                       path.dirname(path.dirname(path.abspath(__file__)))
                   )

#: Path to Elodie's ExifTool config file.
exiftool_config = get_constant(
                      'exiftool_config',
                      path.join(script_directory, 'configs', 'ExifTool_config')
                  )

#: Accepted language in responses from MapQuest
accepted_language = get_constant(
                        'accepted_language',
                        'en'
                    )

# check python version, required in filesystem.py to trigger appropriate method
python_version = version_info.major
