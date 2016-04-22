# Project imports
from imp import load_source
import os
import sys
import shutil

from nose.plugins.skip import SkipTest

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))))

import helper
elodie = load_source('elodie', os.path.abspath('{}/../../elodie.py'.format(os.path.dirname(os.path.realpath(__file__)))))

from elodie import constants
from elodie.media.audio import Audio
from elodie.media.photo import Photo
from elodie.media.text import Text
from elodie.media.video import Video

os.environ['TZ'] = 'GMT'


def test_import_file_text():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/valid.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    reset_hash_db()
    dest_path = elodie.import_file(origin, folder_destination, False, False)
    restore_hash_db()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2016-04-Apr','Unknown Location','2016-04-07_11-15-26-valid-sample-title.txt')) in dest_path, dest_path

def test_import_file_audio():
    raise SkipTest('gh-61 this test fails on travisci')
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    reset_hash_db()
    dest_path = elodie.import_file(origin, folder_destination, False, False)
    restore_hash_db()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2016-01-Jan','Houston','2016-01-04_05-28-15-audio-test-audio.m4a')) in dest_path, dest_path

def test_import_file_photo():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/plain.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    reset_hash_db()
    dest_path = elodie.import_file(origin, folder_destination, False, False)
    restore_hash_db()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2015-12-Dec','Unknown Location','2015-12-05_00-59-26-plain.jpg')) in dest_path, dest_path

def test_import_file_video():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    reset_hash_db()
    dest_path = elodie.import_file(origin, folder_destination, False, False)
    restore_hash_db()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert helper.path_tz_fix(os.path.join('2015-01-Jan','California','2015-01-19_12-45-11-video.mov')) in dest_path, dest_path

def test_update_location_on_audio():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    audio = Audio(origin)
    metadata = audio.get_metadata()

    reset_hash_db()
    status = elodie.update_location(audio, origin, 'Sunnyvale, CA')
    restore_hash_db()

    audio_processed = Audio(origin)
    metadata_processed = audio_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['latitude'] != metadata_processed['latitude']
    assert helper.isclose(metadata_processed['latitude'], 37.3688305556), metadata_processed['latitude']
    assert helper.isclose(metadata_processed['longitude'], -122.03635), metadata_processed['longitude']

def test_update_location_on_photo():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/plain.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    metadata = photo.get_metadata()

    reset_hash_db()
    status = elodie.update_location(photo, origin, 'Sunnyvale, CA')
    restore_hash_db()

    photo_processed = Photo(origin)
    metadata_processed = photo_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['latitude'] != metadata_processed['latitude']
    assert helper.isclose(metadata_processed['latitude'], 37.36883), metadata_processed['latitude']
    assert helper.isclose(metadata_processed['longitude'], -122.03635), metadata_processed['longitude']

def test_update_location_on_text():
    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/text.txt' % folder
    shutil.copyfile(helper.get_file('text.txt'), origin)

    text = Text(origin)
    metadata = text.get_metadata()

    reset_hash_db()
    status = elodie.update_location(text, origin, 'Sunnyvale, CA')
    restore_hash_db()

    text_processed = Text(origin)
    metadata_processed = text_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['latitude'] != metadata_processed['latitude']
    assert helper.isclose(metadata_processed['latitude'], 37.36883), metadata_processed['latitude']
    assert helper.isclose(metadata_processed['longitude'], -122.03635), metadata_processed['longitude']

def test_update_location_on_video():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    video = Video(origin)
    metadata = video.get_metadata()

    reset_hash_db()
    status = elodie.update_location(video, origin, 'Sunnyvale, CA')
    restore_hash_db()

    video_processed = Video(origin)
    metadata_processed = video_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['latitude'] != metadata_processed['latitude']
    assert helper.isclose(metadata_processed['latitude'], 37.3688305556), metadata_processed['latitude']
    assert helper.isclose(metadata_processed['longitude'], -122.03635), metadata_processed['longitude']

def test_update_time_on_audio():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    audio = Audio(origin)
    metadata = audio.get_metadata()

    reset_hash_db()
    status = elodie.update_time(audio, origin, '2000-01-01 12:00:00')
    restore_hash_db()

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

    reset_hash_db()
    status = elodie.update_time(photo, origin, '2000-01-01 12:00:00')
    restore_hash_db()

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

    reset_hash_db()
    status = elodie.update_time(text, origin, '2000-01-01 12:00:00')
    restore_hash_db()

    text_processed = Text(origin)
    metadata_processed = text_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['date_taken'] != metadata_processed['date_taken']
    assert metadata_processed['date_taken'] == helper.time_convert((2000, 1, 1, 12, 0, 0, 5, 1, 0)), metadata_processed['date_taken']

def test_update_time_on_video():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    temporary_folder, folder = helper.create_working_folder()
    temporary_folder_destination, folder_destination = helper.create_working_folder()

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    video = Video(origin)
    metadata = video.get_metadata()

    reset_hash_db()
    status = elodie.update_time(video, origin, '2000-01-01 12:00:00')
    restore_hash_db()

    video_processed = Video(origin)
    metadata_processed = video_processed.get_metadata()

    shutil.rmtree(folder)
    shutil.rmtree(folder_destination)

    assert status == True, status
    assert metadata['date_taken'] != metadata_processed['date_taken']
    assert metadata_processed['date_taken'] == helper.time_convert((2000, 1, 1, 12, 0, 0, 5, 1, 0)), metadata_processed['date_taken']

def reset_hash_db():
    hash_db = constants.hash_db
    if os.path.isfile(hash_db):
        os.rename(hash_db, '{}-test'.format(hash_db))

def restore_hash_db():
    hash_db = '{}-test'.format(constants.hash_db)
    if os.path.isfile(hash_db):
        os.rename(hash_db, hash_db.replace('-test', ''))

def can_edit_exif():
    video = Video()
    return video.get_avmetareadwrite()
