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
from elodie.plugins.googlephotos.googlephotos import GooglePhotos

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

@mock.patch('elodie.config.config_file', '%s/config.ini-googlephotos-set-session' % gettempdir())
def test_googlephotos_set_session():
    with open('%s/config.ini-googlephotos-set-session' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    gp = GooglePhotos()

    if hasattr(load_config, 'config'):
        del load_config.config

    assert gp.session is None, gp.session
    gp.set_session()
    assert gp.session is not None, gp.session

@mock.patch('elodie.config.config_file', '%s/config.ini-googlephotos-upload' % gettempdir())
def test_googlephotos_upload():
    with open('%s/config.ini-googlephotos-upload' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    gp = GooglePhotos()

    if hasattr(load_config, 'config'):
        del load_config.config

    gp.set_session()
    status = gp.upload(helper.get_file('plain.jpg'))
    
    assert status is not None, status

@mock.patch('elodie.config.config_file', '%s/config.ini-googlephotos-upload-invalid-empty' % gettempdir())
def test_googlephotos_upload_invalid_empty():
    with open('%s/config.ini-googlephotos-upload-invalid-empty' % gettempdir(), 'w') as f:
        f.write(config_string_fmt)
    if hasattr(load_config, 'config'):
        del load_config.config

    gp = GooglePhotos()

    if hasattr(load_config, 'config'):
        del load_config.config

    gp.set_session()
    status = gp.upload(helper.get_file('invalid.jpg'))
    
    assert status is None, status
