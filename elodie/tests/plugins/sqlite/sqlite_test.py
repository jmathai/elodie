from __future__ import absolute_import
# Project imports
import mock
import os
import sys
from tempfile import gettempdir

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import helper
from elodie.config import load_config
from elodie.plugins.sqlite.sqlite import SQLite
from elodie.media.audio import Audio
from elodie.media.photo import Photo

# Globals to simplify mocking configs
db_schema = helper.get_file('plugins/sqlite/schema.sql')
config_string = """
[Plugins]
plugins=SQLite

[PluginSQLite]
database_file={}
        """
config_string_fmt = config_string.format(
    ':memory:'
)

setup_module = helper.setup_module
teardown_module = helper.teardown_module

@mock.patch('elodie.config.config_file', '%s/config.ini-sqlite-insert' % gettempdir())
def test_sqlite_insert():
    with open('%s/config.ini-sqlite-insert' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    sqlite_plugin = SQLite()
    sqlite_plugin.create_schema()
    sqlite_plugin.after('/some/source/path', '/folder/path', '/file/path.jpg', {})
    results = sqlite_plugin.run_query(
        'SELECT * FROM `metadata` WHERE `pathOriginal`=:pathOriginal',
        {'pathOriginal': '/folder/path/file/path.jpg'}
    );

    if hasattr(load_config, 'config'):
        del load_config.config

    assert len(results) == 1, results

@mock.patch('elodie.config.config_file', '%s/config.ini-sqlite-insert-multiple' % gettempdir())
def test_sqlite_insert_multiple():
    with open('%s/config.ini-sqlite-insert-multiple' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    sqlite_plugin = SQLite()
    sqlite_plugin.create_schema()
    sqlite_plugin.after('/some/source/path', '/folder/path', '/file/path.jpg', {})
    sqlite_plugin.after('/some/source/path', '/folder/path', '/file/path2.jpg', {})
    results = sqlite_plugin.run_query(
        'SELECT * FROM `metadata`',
        {}
    );

    if hasattr(load_config, 'config'):
        del load_config.config

    assert len(results) == 2, results

@mock.patch('elodie.config.config_file', '%s/config.ini-sqlite-update' % gettempdir())
def test_sqlite_insert_multiple():
    with open('%s/config.ini-sqlite-update' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    sqlite_plugin = SQLite()
    sqlite_plugin.create_schema()
    sqlite_plugin.after('/some/source/path', '/folder/path', '/file/path.jpg', {})
    sqlite_plugin.after('/folder/path/file/path.jpg', '/new-folder/path', '/new-file/path.jpg', {})
    results = sqlite_plugin.run_query(
        'SELECT * FROM `metadata`',
        {}
    );
    print(results)

    if hasattr(load_config, 'config'):
        del load_config.config

    assert len(results) == 1, results
    assert results[0]['pathOriginal'] == '/new-folder/path/new-file/path.jpg', results
