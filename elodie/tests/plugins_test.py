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
plugins=ThrowError,Dummy
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins.plugins == ['ThrowError','Dummy'], plugins.plugins
    assert plugins.classes['ThrowError'].__name__ == 'ThrowError', plugins.classes['ThrowError'].__name__
    assert plugins.classes['Dummy'].__name__ == 'Dummy', plugins.classes['Dummy'].__name__
    assert len(plugins.classes) == 2, len(plugins.classes)

@mock.patch('elodie.config.config_file', '%s/config.ini-load-plugins-many-with-invalid' % gettempdir())
def test_load_plugins_set_many_with_invalid():
    with open('%s/config.ini-load-plugins-many-with-invalid' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=ThrowError,Dummy,DNE
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins.plugins == ['ThrowError','Dummy'], plugins.plugins

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

@mock.patch('elodie.config.config_file', '%s/config.ini-throw-error' % gettempdir())
def test_throw_error():
    with open('%s/config.ini-throw-error' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=ThrowError
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()
    status = plugins.run_all_before('', '', '')

    if hasattr(load_config, 'config'):
        del load_config.config

    assert status == False, status

@mock.patch('elodie.config.config_file', '%s/config.ini-throw-error-one-of-many' % gettempdir())
def test_throw_error_one_of_many():
    with open('%s/config.ini-throw-error-one-of-many' % gettempdir(), 'w') as f:
        f.write("""
[Plugins]
plugins=Dummy,ThrowError
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()
    status = plugins.run_all_before('', '', '')

    if hasattr(load_config, 'config'):
        del load_config.config

    assert status == False, status
