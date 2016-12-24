from __future__ import absolute_import
# Project imports
import mock
import os
import re
import shutil
import sys
import time
from datetime import datetime
from datetime import timedelta
from tempfile import gettempdir

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from . import helper
from elodie.config import load_config
from elodie.filesystem import FileSystem
from elodie.media.media import Media
from elodie.media.photo import Photo
from elodie.media.video import Video
from nose.plugins.skip import SkipTest

os.environ['TZ'] = 'GMT'


def test_create_directory_success():
    filesystem = FileSystem()
    folder = os.path.join(helper.temp_dir(), helper.random_string(10))
    status = filesystem.create_directory(folder)

    # Needs to be a subdirectory
    assert helper.temp_dir() != folder

    assert status == True
    assert os.path.isdir(folder) == True
    assert os.path.exists(folder) == True

    # Clean up
    shutil.rmtree(folder)


def test_create_directory_recursive_success():
    filesystem = FileSystem()
    folder = os.path.join(helper.temp_dir(), helper.random_string(10), helper.random_string(10))
    status = filesystem.create_directory(folder)

    # Needs to be a subdirectory
    assert helper.temp_dir() != folder

    assert status == True
    assert os.path.isdir(folder) == True
    assert os.path.exists(folder) == True

    shutil.rmtree(folder)

@mock.patch('elodie.filesystem.os.makedirs')
def test_create_directory_invalid_permissions(mock_makedirs):
    if os.name == 'nt':
       raise SkipTest("It isn't implemented on Windows")

    # Mock the case where makedirs raises an OSError because the user does
    # not have permission to create the given directory.
    mock_makedirs.side_effect = OSError()

    filesystem = FileSystem()
    status = filesystem.create_directory('/apathwhichdoesnotexist/afolderwhichdoesnotexist')

    assert status == False

def test_delete_directory_if_empty():
    filesystem = FileSystem()
    folder = os.path.join(helper.temp_dir(), helper.random_string(10))
    os.makedirs(folder)

    assert os.path.isdir(folder) == True
    assert os.path.exists(folder) == True

    filesystem.delete_directory_if_empty(folder)

    assert os.path.isdir(folder) == False
    assert os.path.exists(folder) == False

def test_delete_directory_if_empty_when_not_empty():
    filesystem = FileSystem()
    folder = os.path.join(helper.temp_dir(), helper.random_string(10), helper.random_string(10))
    os.makedirs(folder)
    parent_folder = os.path.dirname(folder)

    assert os.path.isdir(folder) == True
    assert os.path.exists(folder) == True
    assert os.path.isdir(parent_folder) == True
    assert os.path.exists(parent_folder) == True

    filesystem.delete_directory_if_empty(parent_folder)

    assert os.path.isdir(folder) == True
    assert os.path.exists(folder) == True
    assert os.path.isdir(parent_folder) == True
    assert os.path.exists(parent_folder) == True

    shutil.rmtree(parent_folder)

def test_get_all_files_success():
    filesystem = FileSystem()
    folder = helper.populate_folder(5)
    files = filesystem.get_all_files(folder)
    shutil.rmtree(folder)

    length = len(files)
    assert length == 5, length


def test_get_all_files_by_extension():
    filesystem = FileSystem()
    folder = helper.populate_folder(5)

    files = filesystem.get_all_files(folder)
    length = len(files)
    assert length == 5, length

    files = filesystem.get_all_files(folder, 'jpg')
    length = len(files)
    assert length == 3, length

    files = filesystem.get_all_files(folder, 'txt')
    length = len(files)
    assert length == 2, length

    files = filesystem.get_all_files(folder, 'gif')
    length = len(files)
    assert length == 0, length

    shutil.rmtree(folder)

def test_get_current_directory():
    filesystem = FileSystem()
    assert os.getcwd() == filesystem.get_current_directory()

def test_get_file_name_plain():
    filesystem = FileSystem()
    media = Photo(helper.get_file('plain.jpg'))
    file_name = filesystem.get_file_name(media)

    assert file_name == helper.path_tz_fix('2015-12-05_00-59-26-plain.jpg'), file_name

def test_get_file_name_with_title():
    filesystem = FileSystem()
    media = Photo(helper.get_file('with-title.jpg'))
    file_name = filesystem.get_file_name(media)

    assert file_name == helper.path_tz_fix('2015-12-05_00-59-26-with-title-some-title.jpg'), file_name

def test_get_folder_name_by_date():
    filesystem = FileSystem()
    time_tuple = (2010, 4, 15, 1, 2, 3, 0, 0, 0)
    folder_name = filesystem.get_folder_name_by_date(time_tuple)

    assert folder_name == '2010-04-Apr', folder_name

    time_tuple = (2010, 9, 15, 1, 2, 3, 0, 0, 0)
    folder_name = filesystem.get_folder_name_by_date(time_tuple)

    assert folder_name == '2010-09-Sep', folder_name

def test_get_folder_path_plain():
    filesystem = FileSystem()
    media = Photo(helper.get_file('plain.jpg'))
    path = filesystem.get_folder_path(media.get_metadata())

    assert path == os.path.join('2015-12-Dec','Unknown Location'), path

def test_get_folder_path_with_title():
    filesystem = FileSystem()
    media = Photo(helper.get_file('with-title.jpg'))
    path = filesystem.get_folder_path(media.get_metadata())

    assert path == os.path.join('2015-12-Dec','Unknown Location'), path

def test_get_folder_path_with_location():
    filesystem = FileSystem()
    media = Photo(helper.get_file('with-location.jpg'))
    path = filesystem.get_folder_path(media.get_metadata())

    assert path == os.path.join('2015-12-Dec','Sunnyvale'), path

def test_get_folder_path_with_location_and_title():
    filesystem = FileSystem()
    media = Photo(helper.get_file('with-location-and-title.jpg'))
    path = filesystem.get_folder_path(media.get_metadata())

    assert path == os.path.join('2015-12-Dec','Sunnyvale'), path

def test_process_file_invalid():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = os.path.join(folder,'photo.jpg')
    shutil.copyfile(helper.get_file('invalid.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    assert destination is None

def test_process_file_plain():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = os.path.join(folder,'photo.jpg')
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = helper.checksum(origin)
    destination_checksum = helper.checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None, origin_checksum
    assert origin_checksum == destination_checksum, destination_checksum
    assert helper.path_tz_fix(os.path.join('2015-12-Dec','Unknown Location','2015-12-05_00-59-26-photo.jpg')) in destination, destination

def test_process_file_with_title():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('with-title.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = helper.checksum(origin)
    destination_checksum = helper.checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None, origin_checksum
    assert origin_checksum == destination_checksum, destination_checksum
    assert helper.path_tz_fix(os.path.join('2015-12-Dec','Unknown Location','2015-12-05_00-59-26-photo-some-title.jpg')) in destination, destination

def test_process_file_with_location():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = os.path.join(folder,'photo.jpg')
    shutil.copyfile(helper.get_file('with-location.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = helper.checksum(origin)
    destination_checksum = helper.checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None, origin_checksum
    assert origin_checksum == destination_checksum, destination_checksum
    assert helper.path_tz_fix(os.path.join('2015-12-Dec','Sunnyvale','2015-12-05_00-59-26-photo.jpg')) in destination, destination

def test_process_file_with_location_and_title():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = os.path.join(folder,'photo.jpg')
    shutil.copyfile(helper.get_file('with-location-and-title.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = helper.checksum(origin)
    destination_checksum = helper.checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None, origin_checksum
    assert origin_checksum == destination_checksum, destination_checksum
    assert helper.path_tz_fix(os.path.join('2015-12-Dec','Sunnyvale','2015-12-05_00-59-26-photo-some-title.jpg')) in destination, destination

def test_process_file_with_album():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = os.path.join(folder,'photo.jpg')
    shutil.copyfile(helper.get_file('with-album.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = helper.checksum(origin)
    destination_checksum = helper.checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None, origin_checksum
    assert origin_checksum == destination_checksum, destination_checksum
    assert helper.path_tz_fix(os.path.join('2015-12-Dec','Test Album','2015-12-05_00-59-26-photo.jpg')) in destination, destination

def test_process_file_with_album_and_title():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = os.path.join(folder,'photo.jpg')
    shutil.copyfile(helper.get_file('with-album-and-title.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = helper.checksum(origin)
    destination_checksum = helper.checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None, origin_checksum
    assert origin_checksum == destination_checksum, destination_checksum
    assert helper.path_tz_fix(os.path.join('2015-12-Dec','Test Album','2015-12-05_00-59-26-photo-some-title.jpg')) in destination, destination

def test_process_file_with_album_and_title_and_location():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = os.path.join(folder,'photo.jpg')
    shutil.copyfile(helper.get_file('with-album-and-title-and-location.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = helper.checksum(origin)
    destination_checksum = helper.checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None, origin_checksum
    assert origin_checksum == destination_checksum, destination_checksum
    assert helper.path_tz_fix(os.path.join('2015-12-Dec','Test Album','2015-12-05_00-59-26-photo-some-title.jpg')) in destination, destination

# gh-89 (setting album then title reverts album)
def test_process_video_with_album_then_title():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = os.path.join(folder,'movie.mov')
    shutil.copyfile(helper.get_file('video.mov'), origin)

    origin_checksum = helper.checksum(origin)

    media = Video(origin)
    media.set_album('test_album')
    media.set_title('test_title')
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    destination_checksum = helper.checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None, origin_checksum
    assert origin_checksum != destination_checksum, destination_checksum
    assert helper.path_tz_fix(os.path.join('2015-01-Jan','test_album','2015-01-19_12-45-11-movie-test_title.mov')) in destination, destination

def test_set_utime_with_exif_date():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = os.path.join(folder,'photo.jpg')
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    media_initial = Photo(origin)
    metadata_initial = media_initial.get_metadata()

    initial_stat = os.stat(origin)
    initial_time = int(min(initial_stat.st_mtime, initial_stat.st_ctime))
    initial_checksum = helper.checksum(origin)

    assert initial_time != time.mktime(metadata_initial['date_taken'])

    filesystem.set_utime(media_initial)
    final_stat = os.stat(origin)
    final_checksum = helper.checksum(origin)

    media_final = Photo(origin)
    metadata_final = media_final.get_metadata()

    shutil.rmtree(folder)

    assert initial_stat.st_mtime != final_stat.st_mtime
    assert final_stat.st_mtime == time.mktime(metadata_final['date_taken'])
    assert initial_checksum == final_checksum

def test_set_utime_without_exif_date():
    filesystem = FileSystem()
    temporary_folder, folder = helper.create_working_folder()

    origin = os.path.join(folder,'photo.jpg')
    shutil.copyfile(helper.get_file('no-exif.jpg'), origin)

    media_initial = Photo(origin)
    metadata_initial = media_initial.get_metadata()

    initial_stat = os.stat(origin)
    initial_time = int(min(initial_stat.st_mtime, initial_stat.st_ctime))
    initial_checksum = helper.checksum(origin)

    assert initial_time == time.mktime(metadata_initial['date_taken'])

    filesystem.set_utime(media_initial)
    final_stat = os.stat(origin)
    final_checksum = helper.checksum(origin)

    media_final = Photo(origin)
    metadata_final = media_final.get_metadata()

    shutil.rmtree(folder)

    assert initial_time == final_stat.st_mtime
    assert final_stat.st_mtime == time.mktime(metadata_final['date_taken']), (final_stat.st_mtime, time.mktime(metadata_final['date_taken']))
    assert initial_checksum == final_checksum

@mock.patch('elodie.config.config_file', '%s/config.ini-does-not-exist' % gettempdir())
def test_get_folder_path_definition_default():
    if hasattr(load_config, 'config'):
        del load_config.config
    filesystem = FileSystem()
    path_definition = filesystem.get_folder_path_definition()
    if hasattr(load_config, 'config'):
        del load_config.config

    assert path_definition == filesystem.default_folder_path_definition, path_definition

@mock.patch('elodie.config.config_file', '%s/config.ini-date-location' % gettempdir())
def test_get_folder_path_definition_date_location():
    with open('%s/config.ini-date-location' % gettempdir(), 'w') as f:
        f.write("""
[Directory]
date=%Y-%m-%d
location=%country
full_path=%date/%location
        """)

    if hasattr(load_config, 'config'):
        del load_config.config
    filesystem = FileSystem()
    path_definition = filesystem.get_folder_path_definition()
    expected = [
        ('date', '%Y-%m-%d'), ('location', '%country')
    ]
    if hasattr(load_config, 'config'):
        del load_config.config

    assert path_definition == expected, path_definition

@mock.patch('elodie.config.config_file', '%s/config.ini-location-date' % gettempdir())
def test_get_folder_path_definition_location_date():
    with open('%s/config.ini-location-date' % gettempdir(), 'w') as f:
        f.write("""
[Directory]
date=%Y-%m-%d
location=%country
full_path=%location/%date
        """)

    if hasattr(load_config, 'config'):
        del load_config.config
    filesystem = FileSystem()
    path_definition = filesystem.get_folder_path_definition()
    expected = [
        ('location', '%country'), ('date', '%Y-%m-%d')
    ]
    if hasattr(load_config, 'config'):
        del load_config.config

    assert path_definition == expected, path_definition

@mock.patch('elodie.config.config_file', '%s/config.ini-cached' % gettempdir())
def test_get_folder_path_definition_cached():
    with open('%s/config.ini-cached' % gettempdir(), 'w') as f:
        f.write("""
[Directory]
date=%Y-%m-%d
location=%country
full_path=%date/%location
        """)

    if hasattr(load_config, 'config'):
        del load_config.config
    filesystem = FileSystem()
    path_definition = filesystem.get_folder_path_definition()
    expected = [
        ('date', '%Y-%m-%d'), ('location', '%country')
    ]

    assert path_definition == expected, path_definition

    with open('%s/config.ini-cached' % gettempdir(), 'w') as f:
        f.write("""
[Directory]
date=%uncached
location=%uncached
full_path=%date/%location
        """)
    if hasattr(load_config, 'config'):
        del load_config.config
    filesystem = FileSystem()
    path_definition = filesystem.get_folder_path_definition()
    expected = [
        ('date', '%Y-%m-%d'), ('location', '%country')
    ]
    if hasattr(load_config, 'config'):
        del load_config.config
