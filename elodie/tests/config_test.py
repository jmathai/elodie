from __future__ import absolute_import
# Project imports

import os
import sys
import unittest 


from mock import patch
from tempfile import gettempdir

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from elodie import constants
from elodie.config import load_config, load_plugin_config

@patch('elodie.config.config_file', '%s/config.ini-singleton-success' % gettempdir())
def test_load_config_singleton_success():
    with open('%s/config.ini-singleton-success' % gettempdir(), 'w') as f:
        f.write("""
[MapQuest]
key=your-api-key-goes-here
prefer_english_names=False
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    config = load_config()
    assert config['MapQuest']['key'] == 'your-api-key-goes-here', config.get('MapQuest', 'key')
    config.set('MapQuest', 'key', 'new-value')

    config = load_config()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert config['MapQuest']['key'] == 'new-value', config.get('MapQuest', 'key')

@patch('elodie.config.config_file', '%s/config.ini-does-not-exist' % gettempdir())
def test_load_config_singleton_no_file():
    if hasattr(load_config, 'config'):
        del load_config.config

    config = load_config()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert config == {}, config

@patch('elodie.config.config_file', '%s/config.ini-load-plugin-config-unset-backwards-compat' % gettempdir())
def test_load_plugin_config_unset_backwards_compat():
    with open('%s/config.ini-load-plugin-config-unset-backwards-compat' % gettempdir(), 'w') as f:
        f.write("""
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = load_plugin_config()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins == [], plugins

@patch('elodie.config.config_file', '%s/config.ini-load-plugin-config-exists-not-set' % gettempdir())
def test_load_plugin_config_exists_not_set():
    with open('%s/config.ini-load-plugin-config-exists-not-set' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = load_plugin_config()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins == [], plugins

@patch('elodie.config.config_file', '%s/config.ini-load-plugin-config-one' % gettempdir())
def test_load_plugin_config_one():
    with open('%s/config.ini-load-plugin-config-one' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=Dummy
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = load_plugin_config()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins == ['Dummy'], plugins

@patch('elodie.config.config_file', '%s/config.ini-load-plugin-config-one-with-invalid' % gettempdir())
def test_load_plugin_config_one_with_invalid():
    with open('%s/config.ini-load-plugin-config-one' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=DNE
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = load_plugin_config()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins == [], plugins

@patch('elodie.config.config_file', '%s/config.ini-load-plugin-config-many' % gettempdir())
def test_load_plugin_config_many():
    with open('%s/config.ini-load-plugin-config-many' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=GooglePhotos,Dummy
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = load_plugin_config()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins == ['GooglePhotos','Dummy'], plugins
