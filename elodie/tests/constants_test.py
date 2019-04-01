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
    assert constants.debug == False, constants.debug

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
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = os.getcwd()
    reload(constants)
    expected_path = os.getcwd()
    print expected_path
    assert constants.application_directory == expected_path, constants.application_directory
