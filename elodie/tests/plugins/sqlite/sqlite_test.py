from __future__ import absolute_import
# Project imports
import mock
import os
import sys
import time
from tempfile import gettempdir

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import helper
from elodie.config import load_config
from elodie.localstorage import Db
from elodie.media.text import Text
from elodie.plugins.sqlite.sqlite import SQLite

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

mock_metadata = {
                    'checksum': 'checksum-val',
                    'date_taken': time.localtime(),
                    'camera_make': 'camera_make-val',
                    'camera_model': 'camera_model-val',
                    'latitude': 0.1,
                    'longitude': 0.2,
                    'album': 'album-val',
                    'title': 'title-val',
                    'mime_type': 'mime_type-val',
                    'original_name': 'original_name-val',
                    'base_name': 'base_name-val',
                    'extension': 'extension-val',
                    'directory_path': 'directory_path-val'
                }

setup_module = helper.setup_module
teardown_module = helper.teardown_module

@mock.patch('elodie.config.config_file', '%s/config.ini-sqlite-insert' % gettempdir())
def test_sqlite_insert():
    with open('%s/config.ini-sqlite-insert' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    sqlite_plugin = SQLite()
    sqlite_plugin.after('/some/source/path.jpg', '/folder/path', '/file/path.jpg', mock_metadata)
    results = sqlite_plugin._run_query(
        'SELECT * FROM `metadata` WHERE `path`=:path',
        {'path': '/folder/path/file/path.jpg'}
    );

    if hasattr(load_config, 'config'):
        del load_config.config

    assert len(results) == 1, results
    assert results[0]['path'] == '/folder/path/file/path.jpg', results[0]

@mock.patch('elodie.config.config_file', '%s/config.ini-sqlite-insert-multiple' % gettempdir())
def test_sqlite_insert_multiple():
    with open('%s/config.ini-sqlite-insert-multiple' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    sqlite_plugin = SQLite()
    sqlite_plugin.after('/some/source/path.jpg', '/folder/path', '/file/path.jpg', mock_metadata)
    mock_metadata_2 = {**mock_metadata, **{'checksum': 'new-hash'}}
    sqlite_plugin.after('/some/source/path.jpg', '/folder/path', '/file/path2.jpg', mock_metadata_2)
    results = sqlite_plugin._run_query(
        'SELECT * FROM `metadata`',
        {}
    );

    if hasattr(load_config, 'config'):
        del load_config.config

    assert len(results) == 2, results
    assert results[0]['path'] == '/folder/path/file/path.jpg', results[0]
    assert results[1]['path'] == '/folder/path/file/path2.jpg', results[1]

@mock.patch('elodie.config.config_file', '%s/config.ini-sqlite-update' % gettempdir())
def test_sqlite_update():
    with open('%s/config.ini-sqlite-update' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    sqlite_plugin = SQLite()
    # write to /folder/path/file/path.jpg and then update it
    sqlite_plugin.after('/some/source/path.jpg', '/folder/path', '/file/path.jpg', mock_metadata)
    mock_metadata_2 = {**mock_metadata, **{'title': 'title-val-new'}}
    sqlite_plugin.after('/folder/path/file/path.jpg', '/new-folder/path', '/new-file/path.jpg', mock_metadata_2)
    results = sqlite_plugin._run_query(
        'SELECT * FROM `metadata`',
        {}
    );

    if hasattr(load_config, 'config'):
        del load_config.config

    assert len(results) == 1, results
    assert results[0]['path'] == '/new-folder/path/new-file/path.jpg', results
    assert results[0]['title'] == 'title-val-new', results

@mock.patch('elodie.config.config_file', '%s/config.ini-sqlite-update-multiple' % gettempdir())
def test_sqlite_update_multiple():
    with open('%s/config.ini-sqlite-update-multiple' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    sqlite_plugin = SQLite()
    mock_metadata_1 = mock_metadata
    mock_metadata_2 = {**mock_metadata, **{'checksum': 'checksum-val-2', 'title': 'title-val-2'}}
    sqlite_plugin.after('/some/source/path.jpg', '/folder/path', '/file/path.jpg', mock_metadata)
    sqlite_plugin.after('/some/source/path2.jpg', '/folder/path', '/file/path2.jpg', mock_metadata_2)
    
    mock_metadata_1_upd = {**mock_metadata_1, **{'title': 'title-val-upd'}}
    mock_metadata_2_upd = {**mock_metadata_2, **{'title': 'title-val-2-upd'}}
    sqlite_plugin.after('/folder/path/file/path.jpg', '/new-folder/path', '/new-file/path.jpg', mock_metadata_1_upd)
    sqlite_plugin.after('/folder/path/file/path2.jpg', '/new-folder/path', '/new-file/path2.jpg', mock_metadata_2_upd)
    results = sqlite_plugin._run_query(
        'SELECT * FROM `metadata`',
        {}
    );

    if hasattr(load_config, 'config'):
        del load_config.config

    assert len(results) == 2, results
    assert results[0]['path'] == '/new-folder/path/new-file/path.jpg', results[0]
    assert results[0]['title'] == 'title-val-upd', results[0]
    assert results[1]['path'] == '/new-folder/path/new-file/path2.jpg', results[1]
    assert results[1]['title'] == 'title-val-2-upd', results[1]

@mock.patch('elodie.config.config_file', '%s/config.ini-sqlite-regenerate-db' % gettempdir())
def test_sqlite_regenerate_db():
    with open('%s/config.ini-sqlite-regenerate-db' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    sqlite_plugin = SQLite()
    db = Db()
    file_path_1 = helper.get_file('with-original-name.txt')
    file_path_2 = helper.get_file('valid.txt')
    db.add_hash('1', file_path_1, True)
    db.add_hash('2', file_path_2, True)

    sqlite_plugin.generate_db()

    results = sqlite_plugin._run_query(
        'SELECT * FROM `metadata`',
        {}
    );

    assert len(results) == 2, results
    assert results[0]['hash'] == 'e2275f3d95c4b55e35bd279bec3f86fcf76b3f3cc0abbf4183725c89a72f94c4', results[0]['hash']
    assert results[0]['path'] == file_path_1, results[0]['path']
    assert results[1]['hash'] == '3c19a5d751cf19e093b7447297731124d9cc987d3f91a9d1872c3b1c1b15639a', results[1]['hash']
    assert results[1]['path'] == file_path_2, results[1]['path']
