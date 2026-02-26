# Project imports
import importlib.util
import unittest.mock as mock
import os
import sys
import shutil

from click.testing import CliRunner
import pytest
# assert_raises replaced with pytest.raises
from six import text_type, unichr as six_unichr
from tempfile import gettempdir

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))))

import helper
elodie_path = os.path.abspath('{}/../../elodie.py'.format(os.path.dirname(os.path.realpath(__file__))))
spec = importlib.util.spec_from_file_location('elodie', elodie_path)
elodie = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elodie)

from elodie.config import load_config
from elodie.localstorage import Db
from elodie.media.audio import Audio
from elodie.media.photo import Photo
from elodie.media.text import Text
from elodie.media.video import Video
from elodie.plugins.plugins import Plugins
from elodie.plugins.googlephotos.googlephotos import GooglePhotos

os.environ['TZ'] = 'GMT'

def test_import_file_text():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2016-04-Apr','Rainham','2016-04-07_11-15-26-valid-sample-title.txt')) in dest_path, dest_path

def test_import_file_audio():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2016-01-Jan','Houston','2016-01-04_05-28-15-audio.m4a')) in dest_path, dest_path

def test_import_file_photo():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/plain.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2015-12-Dec','Unknown Location','2015-12-05_00-59-26-plain.jpg')) in dest_path, dest_path

def test_import_file_video():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2015-01-Jan','Pinecrest','2015-01-19_12-45-11-video.mov')) in dest_path, dest_path

def test_import_file_path_utf8_encoded_ascii_checkmark():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = text_type(folder)+u'/unicode\u2713filename.txt'
    # encode the unicode string to ascii
    origin = origin.encode('utf-8')

    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2016-04-Apr','Rainham',u'2016-04-07_11-15-26-unicode\u2713filename-sample-title.txt')) in dest_path, dest_path

def test_import_file_path_unicode_checkmark():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = text_type(folder)+u'/unicode\u2713filename.txt'

    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2016-04-Apr','Rainham',u'2016-04-07_11-15-26-unicode\u2713filename-sample-title.txt')) in dest_path, dest_path

def test_import_file_path_utf8_encoded_ascii_latin_nbsp():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = text_type(folder)+u'/unicode'+six_unichr(160)+u'filename.txt'
    # encode the unicode string to ascii
    origin = origin.encode('utf-8')

    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2016-04-Apr','Rainham',u'2016-04-07_11-15-26-unicode\xa0filename-sample-title.txt')) in dest_path, dest_path

def test_import_file_path_unicode_latin_nbsp():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = text_type(folder)+u'/unicode'+six_unichr(160)+u'filename.txt'

    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2016-04-Apr','Rainham',u'2016-04-07_11-15-26-unicode\xa0filename-sample-title.txt')) in dest_path, dest_path
    
def test_import_file_allow_duplicate_false():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    dest_path1 = elodie.import_file(origin, folder_destination, False, False, False)
    dest_path2 = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert dest_path1 is not None
    assert dest_path2 is None

def test_import_file_allow_duplicate_true():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    dest_path1 = elodie.import_file(origin, folder_destination, False, False, True)
    dest_path2 = elodie.import_file(origin, folder_destination, False, False, True)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert dest_path1 is not None
    assert dest_path2 is not None
    assert dest_path1 == dest_path2

def test_import_file_send_to_trash_false():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    dest_path1 = elodie.import_file(origin, folder_destination, False, False, False)
    assert os.path.isfile(origin), origin
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert dest_path1 is not None

def test_import_file_send_to_trash_true():
    pytest.skip("Temporarily disable send2trash test gh-230")

    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    dest_path1 = elodie.import_file(origin, folder_destination, False, True, False)
    assert not os.path.isfile(origin), origin
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert dest_path1 is not None

def test_import_destination_in_source():
    temporary_folder, folder = helper.create_working_folder()
    folder_destination = '{}/destination'.format(folder)
    os.mkdir(folder_destination)

    origin = '%s/plain.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)

    assert dest_path is None, dest_path

def test_import_destination_in_source_gh_287():
    temporary_folder, folder = helper.create_working_folder()
    folder_destination = '{}-destination'.format(folder)
    os.mkdir(folder_destination)

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False)
    helper.restore_dbs()

    shutil.rmtree(folder)

    assert dest_path is not None, dest_path

def test_import_invalid_file_exit_code():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    # use a good and bad
    origin_invalid = '%s/invalid.jpg' % folder
    shutil.copyfile(helper.get_file('invalid.jpg'), origin_invalid)

    origin_valid = '%s/valid.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin_valid)

    helper.reset_dbs()
    runner = CliRunner()
    result = runner.invoke(elodie._import, ['--destination', folder_destination, '--allow-duplicates', origin_invalid, origin_valid])
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert result.exit_code == 1, result.exit_code

def test_import_file_with_single_exclude():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin_valid = '%s/valid.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin_valid)

    runner = CliRunner()
    result = runner.invoke(elodie._import, ['--destination', folder_destination, '--exclude-regex', origin_valid[0:5], '--allow-duplicates', origin_valid])

    assert 'Success                        0' in result.output, result.output
    assert 'Error                          0' in result.output, result.output

def test_import_file_with_multiple_exclude():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin_valid = '%s/valid.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin_valid)

    runner = CliRunner()
    result = runner.invoke(elodie._import, ['--destination', folder_destination, '--exclude-regex', 'does not exist in path', '--exclude-regex', origin_valid[0:5], '--allow-duplicates', origin_valid])

    assert 'Success                        0' in result.output, result.output
    assert 'Error                          0' in result.output, result.output

def test_import_hash_db_batch_size_default_writes_per_file():
    runner = CliRunner()
    captured_kwargs = []

    def fake_import_file(*args, **kwargs):
        captured_kwargs.append(kwargs)
        return '/tmp/imported-file.jpg'

    with mock.patch.object(elodie, 'load_config', return_value={}):
        with mock.patch.object(elodie, 'import_file', side_effect=fake_import_file):
            result = runner.invoke(
                elodie._import,
                ['--destination', '/tmp/elodie-import', '/tmp/a.jpg']
            )

    assert result.exit_code == 0, result.output
    assert len(captured_kwargs) == 1
    assert captured_kwargs[0]['db'] is None
    assert captured_kwargs[0]['write_db'] == True

def test_import_hash_db_batch_size_flushes_in_batches():
    class FakeDb(object):
        def __init__(self):
            self.update_calls = 0

        def update_hash_db(self):
            self.update_calls += 1

    fake_db = FakeDb()
    runner = CliRunner()
    captured_kwargs = []

    def fake_import_file(*args, **kwargs):
        captured_kwargs.append(kwargs)
        return '/tmp/imported-file.jpg'

    with mock.patch.object(elodie, 'Db', return_value=fake_db):
        with mock.patch.object(elodie, 'load_config', return_value={}):
            with mock.patch.object(elodie, 'import_file', side_effect=fake_import_file):
                result = runner.invoke(
                    elodie._import,
                    [
                        '--destination', '/tmp/elodie-import',
                        '--hash-db-batch-size', '2',
                        '/tmp/a.jpg', '/tmp/b.jpg', '/tmp/c.jpg'
                    ]
                )

    assert result.exit_code == 0, result.output
    assert len(captured_kwargs) == 3
    assert fake_db.update_calls == 2
    assert all(kwargs['db'] is fake_db for kwargs in captured_kwargs)
    assert all(kwargs['write_db'] == False for kwargs in captured_kwargs)

def test_import_file_with_non_matching_exclude():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin_valid = '%s/valid.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin_valid)

    runner = CliRunner()
    result = runner.invoke(elodie._import, ['--destination', folder_destination, '--exclude-regex', 'does not exist in path', '--allow-duplicates', origin_valid])

    assert 'Success                        1' in result.output, result.output
    assert 'Error                          0' in result.output, result.output

def test_import_directory_with_matching_exclude():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin_valid = '%s/valid.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin_valid)

    runner = CliRunner()
    result = runner.invoke(elodie._import, ['--destination', folder_destination, '--source', folder, '--exclude-regex', folder[1:5], '--allow-duplicates'])

    assert 'Success                        0' in result.output, result.output
    assert 'Error                          0' in result.output, result.output

def test_import_directory_with_non_matching_exclude():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin_valid = '%s/valid.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin_valid)

    runner = CliRunner()
    result = runner.invoke(elodie._import, ['--destination', folder_destination, '--source', folder, '--exclude-regex', 'non-matching', '--allow-duplicates'])

    assert 'Success                        1' in result.output, result.output
    assert 'Error                          0' in result.output, result.output

def test_import_file_with_location():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/no-exif.jpg' % folder
    shutil.copyfile(helper.get_file('no-exif.jpg'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False, 'New York, NY', None)
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    # Should be organized under New York instead of Unknown Location
    assert 'New York' in dest_path, dest_path
    assert 'Unknown Location' not in dest_path, dest_path

def test_import_file_with_location_and_time():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/no-exif.jpg' % folder
    shutil.copyfile(helper.get_file('no-exif.jpg'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False, 'San Francisco, CA', '2022-12-25 10:00:00')
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    # Should be organized under San Francisco and 2022-12-Dec
    assert '2022-12-Dec' in dest_path, dest_path
    assert 'San Francisco' in dest_path, dest_path
    assert '2022-12-25_10-00-00' in dest_path, dest_path

def test_import_file_with_time():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/no-exif.jpg' % folder
    shutil.copyfile(helper.get_file('no-exif.jpg'), origin)

    helper.reset_dbs()
    dest_path = elodie.import_file(origin, folder_destination, False, False, False, None, '2023-07-15 14:30:00')
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    # Should be organized under 2023-07-Jul based on specified time
    # Expected: 2023-07-Jul/Unknown Location/2023-07-15_14-30-00-no-exif.jpg
    assert '2023-07-Jul' in dest_path, dest_path
    assert '2023-07-15_14-30-00' in dest_path, dest_path

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-import-file-with-single-config-exclude' % gettempdir())
def test_import_file_with_single_config_exclude(mock_get_config_file):
    config_string = """
    [Exclusions]
    name1=valid
            """
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string)

    if hasattr(load_config, 'config'):
        del load_config.config

    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin_valid = '%s/valid.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin_valid)

    runner = CliRunner()
    result = runner.invoke(elodie._import, ['--destination', folder_destination, '--allow-duplicates', origin_valid, '--debug'])

    if hasattr(load_config, 'config'):
        del load_config.config

    assert 'Success                        0' in result.output, result.output
    assert 'Error                          0' in result.output, result.output

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-import-file-with-multiple-config-exclude' % gettempdir())
def test_import_file_with_multiple_config_exclude(mock_get_config_file):
    config_string = """
    [Exclusions]
    name1=notvalidatall
    name2=valid
            """
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string)

    if hasattr(load_config, 'config'):
        del load_config.config

    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin_valid = '%s/valid.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin_valid)

    runner = CliRunner()
    result = runner.invoke(elodie._import, ['--destination', folder_destination, '--allow-duplicates', origin_valid, '--debug'])

    if hasattr(load_config, 'config'):
        del load_config.config

    assert 'Success                        0' in result.output, result.output
    assert 'Error                          0' in result.output, result.output

def test_update_location_on_audio():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    audio = Audio(origin)
    metadata = audio.get_metadata()

    helper.reset_dbs()
    status = elodie.update_location(audio, origin, 'Sunnyvale, CA')
    helper.restore_dbs()

    audio_processed = Audio(origin)
    metadata_processed = audio_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['latitude'] != metadata_processed['latitude'], metadata_processed['latitude']
    assert helper.isclose(metadata_processed['latitude'], 37.37188), metadata_processed['latitude']
    assert helper.isclose(metadata_processed['longitude'], -122.03751), metadata_processed['longitude']

def test_update_location_on_photo():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/plain.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    metadata = photo.get_metadata()

    helper.reset_dbs()
    status = elodie.update_location(photo, origin, 'Sunnyvale, CA')
    helper.restore_dbs()

    photo_processed = Photo(origin)
    metadata_processed = photo_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['latitude'] != metadata_processed['latitude']
    assert helper.isclose(metadata_processed['latitude'], 37.37188), metadata_processed['latitude']
    assert helper.isclose(metadata_processed['longitude'], -122.03751), metadata_processed['longitude']

def test_update_location_on_text():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/text.txt' % folder
    shutil.copyfile(helper.get_file('text.txt'), origin)

    text = Text(origin)
    metadata = text.get_metadata()

    helper.reset_dbs()
    status = elodie.update_location(text, origin, 'Sunnyvale, CA')
    helper.restore_dbs()

    text_processed = Text(origin)
    metadata_processed = text_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['latitude'] != metadata_processed['latitude']
    assert helper.isclose(metadata_processed['latitude'], 37.37188), metadata_processed['latitude']
    assert helper.isclose(metadata_processed['longitude'], -122.03751), metadata_processed['longitude']

def test_update_location_on_video():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    video = Video(origin)
    metadata = video.get_metadata()

    helper.reset_dbs()
    status = elodie.update_location(video, origin, 'Sunnyvale, CA')
    helper.restore_dbs()

    video_processed = Video(origin)
    metadata_processed = video_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['latitude'] != metadata_processed['latitude']
    assert helper.isclose(metadata_processed['latitude'], 37.37188), metadata_processed['latitude']
    assert helper.isclose(metadata_processed['longitude'], -122.03751), metadata_processed['longitude']

def test_update_location_with_exiftool_fallback():
    """Test update_location uses ExifTool when MapQuest key is not available."""
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    metadata = photo.get_metadata()

    helper.reset_dbs()
    
    # Mock MapQuest key as None to force ExifTool usage
    with mock.patch('elodie.geolocation.get_key', return_value=None):
        status = elodie.update_location(photo, origin, 'Sunnyvale, California')
    
    helper.restore_dbs()

    photo_processed = Photo(origin)
    metadata_processed = photo_processed.get_metadata()

    shutil.rmtree(folder)

    assert status == True, status
    assert metadata['latitude'] != metadata_processed['latitude']
    # ExifTool returns 37.3688, -122.0365 for Sunnyvale, California
    # This is different from MapQuest which returns 37.37188, -122.03751
    assert helper.isclose(metadata_processed['latitude'], 37.3688), metadata_processed['latitude']
    assert helper.isclose(metadata_processed['longitude'], -122.0365), metadata_processed['longitude']

def test_update_time_on_audio():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    audio = Audio(origin)
    metadata = audio.get_metadata()

    helper.reset_dbs()
    status = elodie.update_time(audio, origin, '2000-01-01 12:00:00')
    helper.restore_dbs()

    audio_processed = Audio(origin)
    metadata_processed = audio_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['date_taken'] != metadata_processed['date_taken']
    assert metadata_processed['date_taken'] == helper.time_convert((2000, 1, 1, 12, 0, 0, 5, 1, 0)), metadata_processed['date_taken']

def test_update_time_on_photo():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/plain.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    metadata = photo.get_metadata()

    helper.reset_dbs()
    status = elodie.update_time(photo, origin, '2000-01-01 12:00:00')
    helper.restore_dbs()

    photo_processed = Photo(origin)
    metadata_processed = photo_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['date_taken'] != metadata_processed['date_taken']
    assert metadata_processed['date_taken'] == helper.time_convert((2000, 1, 1, 12, 0, 0, 5, 1, 0)), metadata_processed['date_taken']

def test_update_time_on_text():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/text.txt' % folder
    shutil.copyfile(helper.get_file('text.txt'), origin)

    text = Text(origin)
    metadata = text.get_metadata()

    helper.reset_dbs()
    status = elodie.update_time(text, origin, '2000-01-01 12:00:00')
    helper.restore_dbs()

    text_processed = Text(origin)
    metadata_processed = text_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['date_taken'] != metadata_processed['date_taken']
    assert metadata_processed['date_taken'] == helper.time_convert((2000, 1, 1, 12, 0, 0, 5, 1, 0)), metadata_processed['date_taken']

def test_update_time_on_video():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    video = Video(origin)
    metadata = video.get_metadata()

    helper.reset_dbs()
    status = elodie.update_time(video, origin, '2000-01-01 12:00:00')
    helper.restore_dbs()

    video_processed = Video(origin)
    metadata_processed = video_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['date_taken'] != metadata_processed['date_taken']
    assert metadata_processed['date_taken'] == helper.time_convert((2000, 1, 1, 12, 0, 0, 5, 1, 0)), metadata_processed['date_taken']

def test_update_with_directory_passed_in():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    runner = CliRunner()
    result = runner.invoke(elodie._import, ['--destination', folder_destination, folder])
    runner2 = CliRunner()
    result = runner2.invoke(elodie._update, ['--album', 'test', folder_destination])
    helper.restore_dbs()

    updated_file_path = "{}/2016-04-Apr/test/2016-04-07_11-15-26-valid-sample-title.txt".format(folder_destination)
    updated_file_exists = os.path.isfile(updated_file_path)

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert updated_file_exists, updated_file_path

def test_update_invalid_file_exit_code():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    # use a good and bad
    origin_invalid = '%s/invalid.jpg' % folder
    shutil.copyfile(helper.get_file('invalid.jpg'), origin_invalid)

    origin_valid = '%s/valid.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin_valid)

    helper.reset_dbs()
    runner = CliRunner()
    result = runner.invoke(elodie._update, ['--album', 'test', origin_invalid, origin_valid])
    helper.restore_dbs()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert result.exit_code == 1, result.exit_code

def test_regenerate_db_invalid_source():
    runner = CliRunner()
    result = runner.invoke(elodie._generate_db, ['--source', '/invalid/path'])
    assert result.exit_code == 1, result.exit_code

def test_regenerate_valid_source():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    runner = CliRunner()
    result = runner.invoke(elodie._generate_db, ['--source', folder])
    db = Db()
    helper.restore_dbs()

    shutil.rmtree(folder)

    assert result.exit_code == 0, result.exit_code
    assert '3c19a5d751cf19e093b7447297731124d9cc987d3f91a9d1872c3b1c1b15639a' in db.hash_db, db.hash_db

def test_regenerate_valid_source_with_invalid_files():
    temporary_folder, folder = helper.create_working_folder()

    origin_valid = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin_valid)
    origin_invalid = '%s/invalid.invalid' % folder
    shutil.copyfile(helper.get_file('invalid.invalid'), origin_invalid)

    helper.reset_dbs()
    runner = CliRunner()
    result = runner.invoke(elodie._generate_db, ['--source', folder])
    db = Db()
    helper.restore_dbs()

    shutil.rmtree(folder)

    assert result.exit_code == 0, result.exit_code
    assert '3c19a5d751cf19e093b7447297731124d9cc987d3f91a9d1872c3b1c1b15639a' in db.hash_db, db.hash_db
    assert 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' not in db.hash_db, db.hash_db

def test_import_stops_cleanly_on_interrupt_request():
    class FakeInterruptHandler(object):
        def __init__(self):
            self.interrupted = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    fake_interrupt = FakeInterruptHandler()
    import_calls = {'count': 0}

    def fake_import_file(*args, **kwargs):
        import_calls['count'] += 1
        fake_interrupt.interrupted = True
        return '/tmp/imported-file.jpg'

    runner = CliRunner()
    with mock.patch.object(elodie, '_GracefulInterruptHandler', return_value=fake_interrupt):
        with mock.patch.object(elodie, 'import_file', side_effect=fake_import_file):
            with mock.patch.object(elodie, 'load_config', return_value={}):
                result = runner.invoke(
                    elodie._import,
                    ['--destination', '/tmp/elodie-import', '/tmp/a.jpg', '/tmp/b.jpg']
                )

    assert result.exit_code == 130, result.output
    assert import_calls['count'] == 1, import_calls

def test_generate_db_stops_cleanly_on_interrupt_request():
    class FakeInterruptHandler(object):
        def __init__(self):
            self.interrupted = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    class FakeDb(object):
        def __init__(self, interrupt_handler):
            self.interrupt_handler = interrupt_handler
            self.update_calls = 0
            self.hash_db = {}

        def backup_hash_db(self):
            return None

        def reset_hash_db(self):
            self.hash_db = {}

        def checksum(self, file_path):
            return file_path

        def add_hash(self, key, value):
            self.hash_db[key] = value
            self.interrupt_handler.interrupted = True

        def update_hash_db(self):
            self.update_calls += 1

    fake_interrupt = FakeInterruptHandler()
    fake_db = FakeDb(fake_interrupt)

    runner = CliRunner()
    with mock.patch.object(elodie, '_GracefulInterruptHandler', return_value=fake_interrupt):
        with mock.patch.object(elodie, 'Db', return_value=fake_db):
            with mock.patch.object(elodie.FILESYSTEM, 'get_all_files', return_value=['/tmp/a.jpg', '/tmp/b.jpg']):
                result = runner.invoke(elodie._generate_db, ['--source', helper.temp_dir()])

    assert result.exit_code == 130, result.output
    assert fake_db.update_calls == 1

def test_verify_ok():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    runner = CliRunner()
    runner.invoke(elodie._generate_db, ['--source', folder])
    result = runner.invoke(elodie._verify)
    helper.restore_dbs()

    shutil.rmtree(folder)

    assert 'Success                        1' in result.output, result.output
    assert 'Error                          0' in result.output, result.output

def test_verify_error():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    helper.reset_dbs()
    runner = CliRunner()
    runner.invoke(elodie._generate_db, ['--source', folder])
    with open(origin, 'w') as f:
        f.write('changed text')
    result = runner.invoke(elodie._verify)
    helper.restore_dbs()

    shutil.rmtree(folder)

    assert origin in result.output, result.output
    assert 'Error                          1' in result.output, result.output

@mock.patch('elodie.config.get_config_file', return_value='%s/config.ini-cli-batch-plugin-googlephotos' % gettempdir())
def test_cli_batch_plugin_googlephotos(mock_get_config_file):
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
    with open(mock_get_config_file.return_value, 'w') as f:
        f.write(config_string_fmt)

    if hasattr(load_config, 'config'):
        del load_config.config

    final_file_path_1 = helper.get_file('plain.jpg')
    final_file_path_2 = helper.get_file('no-exif.jpg')
    sample_metadata_1 = Photo(final_file_path_1).get_metadata()
    sample_metadata_2 = Photo(final_file_path_2).get_metadata()
    gp = GooglePhotos()
    gp.after('', '', final_file_path_1, sample_metadata_1)
    gp.after('', '', final_file_path_2, sample_metadata_1)

    runner = CliRunner()
    result = runner.invoke(elodie._batch)

    if hasattr(load_config, 'config'):
        del load_config.config

    assert "elodie/tests/files/plain.jpg uploaded successfully.\"}\n" in result.output, result.output
    assert "elodie/tests/files/no-exif.jpg uploaded successfully.\"}\n" in result.output, result.output

def test_cli_debug_import():
    runner = CliRunner()
    # import
    result = runner.invoke(elodie._import, ['--destination', '/does/not/exist', '/does/not/exist'])
    assert "Could not find /does/not/exist\n" not in result.output, result.output
    result = runner.invoke(elodie._import, ['--destination', '/does/not/exist', '--debug', '/does/not/exist'])
    assert "Could not find /does/not/exist\n" in result.output, result.output

def test_cli_debug_update():
    runner = CliRunner()
    # update
    result = runner.invoke(elodie._update, ['--location', 'foobar', '/does/not/exist'])
    assert "Could not find /does/not/exist\n" not in result.output, result.output
    result = runner.invoke(elodie._update, ['--location', 'foobar', '--debug', '/does/not/exist'])
    assert "Could not find /does/not/exist\n" in result.output, result.output
