# Project imports
import os
import sys

import hashlib
import random
import re
import shutil
import string
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from elodie import filesystem
from elodie.media.media import Media
from elodie.media.photo import Photo
from elodie.media.video import Video

os.environ['TZ'] = 'GMT'

filesystem = filesystem.FileSystem()

def test_create_directory_success():
    folder = '%s/%s' % (tempfile.gettempdir(), random_string(10))
    status = filesystem.create_directory(folder)

    # Needs to be a subdirectory
    assert tempfile.gettempdir() != folder

    assert status == True
    assert os.path.isdir(folder) == True
    assert os.path.exists(folder) == True
    
    # Clean up
    shutil.rmtree(folder)


def test_create_directory_recursive_success():
    folder = '%s/%s/%s' % (tempfile.gettempdir(), random_string(10), random_string(10))
    status = filesystem.create_directory(folder)

    # Needs to be a subdirectory
    assert tempfile.gettempdir() != folder

    assert status == True
    assert os.path.isdir(folder) == True
    assert os.path.exists(folder) == True

    shutil.rmtree(folder)

def test_create_directory_invalid_permissions():
    status = filesystem.create_directory('/apathwhichdoesnotexist/afolderwhichdoesnotexist')

    assert status == False

def test_delete_directory_if_empty():
    folder = '%s/%s' % (tempfile.gettempdir(), random_string(10))
    os.makedirs(folder)

    assert os.path.isdir(folder) == True
    assert os.path.exists(folder) == True

    filesystem.delete_directory_if_empty(folder)

    assert os.path.isdir(folder) == False
    assert os.path.exists(folder) == False

def test_delete_directory_if_empty_when_not_empty():
    folder = '%s/%s/%s' % (tempfile.gettempdir(), random_string(10), random_string(10))
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
    folder = populate_folder(5)
    files = filesystem.get_all_files(folder)
    shutil.rmtree(folder)

    assert len(files) == 5


def test_get_all_files_by_extension():
    folder = populate_folder(5)

    files = filesystem.get_all_files(folder)
    assert len(files) == 5

    files = filesystem.get_all_files(folder, 'jpg')
    assert len(files) == 3

    files = filesystem.get_all_files(folder, 'txt')
    assert len(files) == 2

    files = filesystem.get_all_files(folder, 'gif')
    assert len(files) == 0

    shutil.rmtree(folder)

def test_get_current_directory():
    assert os.getcwd() == filesystem.get_current_directory()

def test_get_file_name_plain():
    media = Photo(get_file('plain.jpg'))
    file_name = filesystem.get_file_name(media)

    assert file_name == '2015-12-05_00-59-26-plain.jpg'

def test_get_file_name_with_title():
    media = Photo(get_file('with-title.jpg'))
    file_name = filesystem.get_file_name(media)

    assert file_name == '2015-12-05_00-59-26-with-title-some-title.jpg'

def test_get_folder_name_by_date():
    time_tuple = (2010, 4, 15, 1, 2, 3, 0, 0, 0)
    folder_name = filesystem.get_folder_name_by_date(time_tuple)

    assert folder_name == '2010-04-Apr'

    time_tuple = (2010, 9, 15, 1, 2, 3, 0, 0, 0)
    folder_name = filesystem.get_folder_name_by_date(time_tuple)

    assert folder_name == '2010-09-Sep'

def test_get_folder_path_plain():
    media = Photo(get_file('plain.jpg'))
    path = filesystem.get_folder_path(media.get_metadata())

    assert path == '2015-12-Dec/Unknown Location'

def test_get_folder_path_with_title():
    media = Photo(get_file('with-title.jpg'))
    path = filesystem.get_folder_path(media.get_metadata())

    assert path == '2015-12-Dec/Unknown Location'

def test_get_folder_path_with_location():
    media = Photo(get_file('with-location.jpg'))
    path = filesystem.get_folder_path(media.get_metadata())

    assert path == '2015-12-Dec/Sunnyvale'

def test_get_folder_path_with_location_and_title():
    media = Photo(get_file('with-location-and-title.jpg'))
    path = filesystem.get_folder_path(media.get_metadata())

    assert path == '2015-12-Dec/Sunnyvale'

def test_process_file_plain():
    temporary_folder = tempfile.gettempdir()
    folder = '%s/%s/%s' % (temporary_folder, random_string(10), random_string(10))
    os.makedirs(folder)

    origin = '%s/plain.jpg' % folder
    shutil.copyfile(get_file('plain.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = checksum(origin)
    destination_checksum = checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None
    assert origin_checksum == destination_checksum
    assert '2015-12-Dec/Unknown Location/2015-12-05_00-59-26-plain.jpg' in destination

def test_process_file_with_title():
    temporary_folder = tempfile.gettempdir()
    folder = '%s/%s/%s' % (temporary_folder, random_string(10), random_string(10))
    os.makedirs(folder)

    origin = '%s/plain.jpg' % folder
    shutil.copyfile(get_file('with-title.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = checksum(origin)
    destination_checksum = checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None
    assert origin_checksum == destination_checksum
    assert '2015-12-Dec/Unknown Location/2015-12-05_00-59-26-plain-some-title.jpg' in destination

def test_process_file_with_location():
    temporary_folder = tempfile.gettempdir()
    folder = '%s/%s/%s' % (temporary_folder, random_string(10), random_string(10))
    os.makedirs(folder)

    origin = '%s/plain.jpg' % folder
    shutil.copyfile(get_file('with-location.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = checksum(origin)
    destination_checksum = checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None
    assert origin_checksum == destination_checksum
    assert '2015-12-Dec/Sunnyvale/2015-12-05_00-59-26-plain.jpg' in destination

def test_process_file_with_location_and_title():
    temporary_folder = tempfile.gettempdir()
    folder = '%s/%s/%s' % (temporary_folder, random_string(10), random_string(10))
    os.makedirs(folder)

    origin = '%s/plain.jpg' % folder
    shutil.copyfile(get_file('with-location-and-title.jpg'), origin)

    media = Photo(origin)
    destination = filesystem.process_file(origin, temporary_folder, media, allowDuplicate=True)

    origin_checksum = checksum(origin)
    destination_checksum = checksum(destination)

    shutil.rmtree(folder)
    shutil.rmtree(os.path.dirname(os.path.dirname(destination)))

    assert origin_checksum is not None
    assert origin_checksum == destination_checksum
    assert '2015-12-Dec/Sunnyvale/2015-12-05_00-59-26-plain-some-title.jpg' in destination

def checksum(file_path, blocksize=65536):
    hasher = hashlib.sha256()
    with open(file_path, 'r') as f:
        buf = f.read(blocksize)

        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)
        return hasher.hexdigest()
    return None

def get_file(name):
    current_folder = os.path.dirname(os.path.realpath(__file__))
    return '%s/files/%s' % (current_folder, name)

def populate_folder(number_of_files):
    folder = '%s/%s' % (tempfile.gettempdir(), random_string(10))
    os.makedirs(folder)

    for x in range(0, number_of_files):
        ext = 'jpg' if x % 2 == 0 else 'txt'
        fname = '%s/%s.%s' % (folder, x, ext)
        with open(fname, 'a'):
            os.utime(fname, None)

    return folder

def random_string(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))
