from __future__ import absolute_import
# Project imports
import mock
import os
import sys
from tempfile import gettempdir

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from . import helper
from elodie.config import load_config
from elodie.plugins.plugins import Plugins

@mock.patch('elodie.config.config_file', '%s/config.ini-load-plugins-unset-backwards-compat' % gettempdir())
def test_load_plugins_unset_backwards_compat():
    with open('%s/config.ini-load-plugins-unset-backwards-compat' % gettempdir(), 'w') as f:
        f.write("""
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins.plugins == [], plugins.plugins

@mock.patch('elodie.config.config_file', '%s/config.ini-load-plugins-exists-not-set' % gettempdir())
def test_load_plugins_exists_not_set():
    with open('%s/config.ini-load-plugins-exists-not-set' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins.plugins == [], plugins.plugins

@mock.patch('elodie.config.config_file', '%s/config.ini-load-plugins-one' % gettempdir())
def test_load_plugins_one():
    with open('%s/config.ini-load-plugins-one' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=Dummy
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins.plugins == ['Dummy'], plugins.plugins
    assert len(plugins.classes) == 1, len(plugins.classes)

@mock.patch('elodie.config.config_file', '%s/config.ini-load-plugins-one-with-invalid' % gettempdir())
def test_load_plugins_one_with_invalid():
    with open('%s/config.ini-load-plugins-one' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=DNE
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins.plugins == [], plugins.plugins
    assert len(plugins.classes) == 0, len(plugins.classes)

@mock.patch('elodie.config.config_file', '%s/config.ini-load-plugins-many' % gettempdir())
def test_load_plugins_many():
    with open('%s/config.ini-load-plugins-many' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=GooglePhotos,Dummy
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins.plugins == ['GooglePhotos','Dummy'], plugins.plugins
    assert len(plugins.classes) == 2, len(plugins.classes)

@mock.patch('elodie.config.config_file', '%s/config.ini-load-plugins-many-with-invalid' % gettempdir())
def test_load_plugins_set_many_with_invalid():
    with open('%s/config.ini-load-plugins-many-with-invalid' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=GooglePhotos,Dummy,DNE
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins.plugins == ['GooglePhotos','Dummy'], plugins.plugins

@mock.patch('elodie.config.config_file', '%s/config.ini-run-before' % gettempdir())
def test_run_before():
    with open('%s/config.ini-run-before' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=Dummy
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()
    before_ran_1 = plugins.classes['Dummy'].before_ran
    plugins.run_all_before('', '', '')
    before_ran_2 = plugins.classes['Dummy'].before_ran

    if hasattr(load_config, 'config'):
        del load_config.config

    assert before_ran_1 == False, before_ran_1
    assert before_ran_2 == True, before_ran_2
