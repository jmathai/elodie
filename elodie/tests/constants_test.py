from __future__ import absolute_import
from __builtin__ import __import__
# Project imports

import os
import sys
import unittest 

from mock import patch

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

def test_constants():
    constants_override_file = '%s/constants_override.py' % BASE_PATH
    with open(constants_override_file, 'w') as f:
        f.write("""
debug = 'foobar'
""")

    application_directory = '{}/.elodie'.format(os.path.expanduser('~'))
    script_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(script_directory)

    from elodie import constants

    test_values = {
        'debug': 'foobar',
        'application_directory': application_directory,
        'hash_db': '{}/hash.json'.format(application_directory),
        'location_db': '{}/location.json'.format(application_directory),
        'script_directory': script_directory,
        'accepted_language': 'en',
        'python_version': sys.version_info.major
    }
    
    for key in test_values:
        assert getattr(constants, key) == getattr(constants, key), '%s != %s, == %s' % (key, test_values[key], test_values[key])
