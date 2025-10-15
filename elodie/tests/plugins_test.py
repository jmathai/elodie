from __future__ import absolute_import
# Project imports
import unittest.mock as mock
import os
import sys
from tempfile import gettempdir

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from . import helper
from elodie.config import load_config
from elodie.plugins.plugins import Plugins, PluginBase, PluginDb

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-load-plugins-unset-backwards-compat' % gettempdir())
def test_load_plugins_unset_backwards_compat(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write("""
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert plugins.plugins == [], plugins.plugins

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-load-plugins-exists-not-set' % gettempdir())
def test_load_plugins_exists_not_set(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
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

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-load-plugins-one' % gettempdir())
def test_load_plugins_one(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
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

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-load-plugins-one-with-invalid' % gettempdir())
def test_load_plugins_one_with_invalid(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
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

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-load-plugins-many' % gettempdir())
def test_load_plugins_many(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
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

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-load-plugins-many-with-invalid' % gettempdir())
def test_load_plugins_set_many_with_invalid(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
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

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-run-before' % gettempdir())
def test_run_before(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write("""
[Plugins]
plugins=Dummy
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()
    before_ran_1 = plugins.classes['Dummy'].before_ran
    plugins.run_all_before('', '')
    before_ran_2 = plugins.classes['Dummy'].before_ran

    if hasattr(load_config, 'config'):
        del load_config.config

    assert before_ran_1 == False, before_ran_1
    assert before_ran_2 == True, before_ran_2

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-throw-error' % gettempdir())
def test_throw_error(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write("""
[Plugins]
plugins=ThrowError
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()
    status_after = plugins.run_all_after('', '', '', '')
    status_batch = plugins.run_batch()
    status_before = plugins.run_all_before('', '')

    if hasattr(load_config, 'config'):
        del load_config.config

    assert status_after == False, status_after
    assert status_batch == False, status_batch
    assert status_before == False, status_before

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-throw-error-one-of-many' % gettempdir())
def test_throw_error_one_of_many(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write("""
[Plugins]
plugins=Dummy,ThrowError
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()
    status_after = plugins.run_all_after('', '', '', '')
    status_batch = plugins.run_batch()
    status_before = plugins.run_all_before('', '')

    if hasattr(load_config, 'config'):
        del load_config.config

    assert status_after == False, status_after
    assert status_batch == False, status_batch
    assert status_before == False, status_before

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-throw-runtime-error' % gettempdir())
def test_throw_error_runtime_error(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write("""
[Plugins]
plugins=RuntimeError
        """)
    if hasattr(load_config, 'config'):
        del load_config.config

    plugins = Plugins()
    plugins.load()
    status_after = plugins.run_all_after('', '', '', '')
    status_batch = plugins.run_batch()
    status_before = plugins.run_all_before('', '')

    if hasattr(load_config, 'config'):
        del load_config.config

    assert status_after == True, status_after
    assert status_batch == True, status_batch
    assert status_before == True, status_before

def test_plugin_base_inherits_db():
    plugin_base = PluginBase()
    assert hasattr(plugin_base.db, 'get')
    assert hasattr(plugin_base.db, 'set')
    assert hasattr(plugin_base.db, 'get_all')
    assert hasattr(plugin_base.db, 'delete')

def test_db_initialize_file():
    db = PluginDb('foobar')
    try:
        os.remove(db.db_file)
    except OSError:
        pass
    db = PluginDb('foobar')

def test_db_get_then_set_then_get_then_delete():
    db = PluginDb('foobar')
    foo = db.get('foo')
    assert foo is None, foo
    db.set('foo', 'bar')
    foo = db.get('foo')
    assert foo == 'bar', foo
    db.delete('foo')
    foo = db.get('foo')
    assert foo is None, foo

def test_db_get_all():
    # we initialize the db to get the file path to delete then reinitialize
    db = PluginDb('foobar')
    try:
        os.remove(db.db_file)
    except OSError:
        pass
    db = PluginDb('foobar')
    db.set('a', '1')
    db.set('b', '2')
    db.set('c', '3')
    db.set('d', '4')
    all_rows = db.get_all()

    assert all_rows == {'a': '1', 'b': '2', 'c': '3', 'd': '4'}, all_rows
