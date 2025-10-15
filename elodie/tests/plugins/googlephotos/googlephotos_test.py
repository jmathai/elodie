from __future__ import absolute_import
# Project imports
import unittest.mock as mock
import os
import sys
from tempfile import gettempdir

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import helper
from elodie.config import load_config
from elodie.plugins.googlephotos.googlephotos import GooglePhotos
from elodie.media.audio import Audio
from elodie.media.photo import Photo

# Globals to simplify mocking configs
auth_file = helper.get_file('plugins/googlephotos/auth_file.json')
secrets_file = helper.get_file('plugins/googlephotos/secrets_file.json')
config_string = """
[Plugins]
plugins=GooglePhotos

[PluginGooglePhotos]
auth_file={}
secrets_file={}
        """
config_string_fmt = config_string.format(
    auth_file,
    secrets_file
)

setup_module = helper.setup_module
teardown_module = helper.teardown_module

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-googlephotos-set-session' % gettempdir())
def test_googlephotos_set_session(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    gp = GooglePhotos()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert gp.session is None, gp.session
    gp.set_session()
    assert gp.session is not None, gp.session

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-googlephotos-after-supported' % gettempdir())
def test_googlephotos_after_supported(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    sample_photo = Photo(helper.get_file('plain.jpg'))
    sample_metadata = sample_photo.get_metadata()
    sample_metadata['original_name'] = 'foobar'
    final_file_path = helper.get_file('plain.jpg')
    gp = GooglePhotos()
    gp.after('', '', final_file_path, sample_metadata)
    db_row = gp.db.get(final_file_path)

    if hasattr(load_config, 'config'):
        del load_config.config

    assert db_row == 'foobar', db_row

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-googlephotos-after-unsupported' % gettempdir())
def test_googlephotos_after_unsupported(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    final_file_path = helper.get_file('audio.m4a')
    sample_photo = Audio(final_file_path)
    sample_metadata = sample_photo.get_metadata()
    sample_metadata['original_name'] = 'foobar'
    gp = GooglePhotos()
    gp.after('', '', final_file_path, sample_metadata)
    db_row = gp.db.get(final_file_path)

    if hasattr(load_config, 'config'):
        del load_config.config

    assert db_row == None, db_row

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-googlephotos-upload' % gettempdir())
def test_googlephotos_upload(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    gp = GooglePhotos()

    if hasattr(load_config, 'config'):
        del load_config.config

    gp.set_session()
    status = gp.upload(helper.get_file('plain.jpg'))
    
    assert status is not None, status

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-googlephotos-upload-session-fail' % gettempdir())
def test_googlephotos_upload_session_fail(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string)
    if hasattr(load_config, 'config'):
        del load_config.config

    gp = GooglePhotos()

    if hasattr(load_config, 'config'):
        del load_config.config

    gp.set_session()
    status = gp.upload(helper.get_file('plain.jpg'))
    
    assert status is None, status

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-googlephotos-upload-invalid-empty' % gettempdir())
def test_googlephotos_upload_invalid_empty(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    gp = GooglePhotos()

    if hasattr(load_config, 'config'):
        del load_config.config

    gp.set_session()
    status = gp.upload(helper.get_file('invalid.jpg'))
    
    assert status is None, status

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-googlephotos-upload-dne' % gettempdir())
def test_googlephotos_upload_dne(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    gp = GooglePhotos()

    if hasattr(load_config, 'config'):
        del load_config.config

    gp.set_session()
    status = gp.upload('/file/does/not/exist')
    
    assert status is None, status

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-googlephotos-batch' % gettempdir())
def test_googlephotos_batch(mock_get_config_file):
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    sample_photo = Photo(helper.get_file('plain.jpg'))
    sample_metadata = sample_photo.get_metadata()
    sample_metadata['original_name'] = 'foobar'
    final_file_path = helper.get_file('plain.jpg')
    gp = GooglePhotos()
    gp.after('', '', final_file_path, sample_metadata)
    db_row = gp.db.get(final_file_path)
    assert db_row == 'foobar', db_row

    status, count = gp.batch()
    db_row_after = gp.db.get(final_file_path)
    assert status == True, status
    assert count == 1, count
    assert db_row_after is None, db_row_after


    if hasattr(load_config, 'config'):
        del load_config.config

        
    gp.set_session()
    status = gp.upload(helper.get_file('invalid.jpg'))
    
    assert status is None, status
