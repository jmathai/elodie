from __future__ import absolute_import
# Project imports

import os
import sys
import unittest 

from mock import patch

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from elodie import constants
from elodie.config import load_config

BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

@patch('elodie.config.config_file', '%s/config.ini-sample' % BASE_PATH)
def test_load_config_singleton_success():
    config = load_config()
    assert config['MapQuest']['key'] == 'your-api-key-goes-here', config.get('MapQuest', 'key')
    config.set('MapQuest', 'key', 'new-value')

    config = load_config()
    assert config['MapQuest']['key'] == 'new-value', config.get('MapQuest', 'key')

    del load_config.config

@patch('elodie.config.config_file', '%s/config.ini-does-not-exist' % BASE_PATH)
def test_load_config_singleton_no_file():
    config = load_config()
    assert config == {}, config
