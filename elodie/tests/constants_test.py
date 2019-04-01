from __future__ import absolute_import
# Project imports

import os
import sys
import unittest 

try:
    reload  # Python 2.7
except NameError:
    try:
        from importlib import reload  # Python 3.4+
    except ImportError:
        from imp import reload  # Python 3.0 - 3.3

from mock import patch

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from elodie import constants

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

def test_debug():
    # This seems pointless but on Travis we explicitly modify the file to be True
    assert constants.debug == constants.debug, constants.debug

def test_application_directory_default():
    reload(constants)
    expected_path = '{}/.elodie'.format(os.path.expanduser('~'))
    assert constants.application_directory == expected_path, constants.application_directory

def test_application_directory_override_invalid():
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = '/foo/bar'
    reload(constants)
    expected_path = '{}/.elodie'.format(os.path.expanduser('~'))
    assert constants.application_directory == expected_path, constants.application_directory

def test_application_directory_override_valid():
    cwd = os.getcwd()
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = cwd
    reload(constants)

    assert constants.application_directory == cwd, constants.application_directory
    assert cwd in constants.hash_db, constants.hash_db

# must come after test_application_directory_override_valid due to env var reset
def test_hash_db():
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = ''
    reload(constants)
    assert constants.hash_db == '{}/hash.json'.format(constants.application_directory), constants.hash_db

def test_location_db():
    assert constants.location_db == '{}/location.json'.format(constants.application_directory), constants.location_db

def test_script_directory():
    path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    assert path == constants.script_directory, constants.script_directory

def test_exiftool_config():
    path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    assert '{}/configs/ExifTool_config'.format(path) == constants.exiftool_config, constants.exiftool_config

def test_mapquest_base_url_default():
    assert constants.mapquest_base_url == 'https://open.mapquestapi.com', constants.mapquest_base_url

def test_mapquest_base_url_override():
    os.environ['ELODIE_MAPQUEST_BASE_URL'] = 'foobar'
    reload(constants)
    assert constants.mapquest_base_url == 'foobar', constants.mapquest_base_url

def test_mapquest_Key():
    assert constants.mapquest_key == None, constants.mapquest_key

def test_mapquest_key_override():
    os.environ['ELODIE_MAPQUEST_KEY'] = 'foobar'
    reload(constants)
    assert constants.mapquest_key == 'foobar', constants.mapquest_key

def test_accepted_language():
    assert constants.accepted_language == 'en', constants.accepted_language

def test_python_version():
    assert constants.python_version == sys.version_info.major, constants.python_version
