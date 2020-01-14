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

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import helper
from elodie.media.audio import Audio
from elodie.media.media import Media
from elodie.media.photo import Photo
from elodie.media.video import Video

os.environ['TZ'] = 'GMT'

setup_module = helper.setup_module
teardown_module = helper.teardown_module

def test_get_file_path():
    media = Media(helper.get_file('plain.jpg'))
    path = media.get_file_path()

    assert 'plain.jpg' in path, path

def test_get_class_by_file_photo():
    media = Media.get_class_by_file(helper.get_file('plain.jpg'), [Photo, Video])

    assert media.__name__ == 'Photo'

def test_get_class_by_file_video():
    media = Media.get_class_by_file(helper.get_file('video.mov'), [Photo, Video])

    assert media.__name__ == 'Video'

def test_get_class_by_file_unsupported():
    media = Media.get_class_by_file(helper.get_file('text.txt'), [Photo, Video])

    assert media is None

def test_get_class_by_file_ds_store():
    media = Media.get_class_by_file(helper.get_file('.DS_Store'),
                                    [Photo, Video, Audio])
    assert media is None

def test_get_class_by_file_invalid_type():
    media = Media.get_class_by_file(None,
                                    [Photo, Video, Audio])
    assert media is None

    media = Media.get_class_by_file(False,
                                    [Photo, Video, Audio])
    assert media is None

    media = Media.get_class_by_file(True,
                                    [Photo, Video, Audio])
    assert media is None

def test_get_original_name():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/%s' % (folder, 'with-original-name.jpg')
    file = helper.get_file('with-original-name.jpg')
    
    shutil.copyfile(file, origin)

    media = Media.get_class_by_file(origin, [Photo])
    original_name = media.get_original_name()

    assert original_name == 'originalfilename.jpg', original_name

def test_get_original_name_invalid_file():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/%s' % (folder, 'invalid.jpg')
    file = helper.get_file('invalid.jpg')
    
    shutil.copyfile(file, origin)

    media = Media.get_class_by_file(origin, [Photo])
    original_name = media.get_original_name()

    assert original_name is None, original_name

def test_set_original_name_when_exists():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/%s' % (folder, 'with-original-name.jpg')
    file = helper.get_file('with-original-name.jpg')
    
    shutil.copyfile(file, origin)

    media = Media.get_class_by_file(origin, [Photo])
    result = media.set_original_name()

    assert result is None, result

def test_set_original_name_when_does_not_exist():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/%s' % (folder, 'plain.jpg')
    file = helper.get_file('plain.jpg')
    
    shutil.copyfile(file, origin)

    media = Media.get_class_by_file(origin, [Photo])
    metadata_before = media.get_metadata()
    result = media.set_original_name()
    metadata_after = media.get_metadata()

    assert metadata_before['original_name'] is None, metadata_before
    assert metadata_after['original_name'] == 'plain.jpg', metadata_after
    assert result is True, result

def test_set_original_name_with_arg():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/%s' % (folder, 'plain.jpg')
    file = helper.get_file('plain.jpg')
    
    shutil.copyfile(file, origin)

    new_name = helper.random_string(15)

    media = Media.get_class_by_file(origin, [Photo])
    metadata_before = media.get_metadata()
    result = media.set_original_name(new_name)
    metadata_after = media.get_metadata()

    assert metadata_before['original_name'] is None, metadata_before
    assert metadata_after['original_name'] == new_name, metadata_after
    assert result is True, result

def test_set_original_name():
    files = ['plain.jpg', 'audio.m4a', 'photo.nef', 'video.mov']

    for file in files:
        ext = os.path.splitext(file)[1]

        temporary_folder, folder = helper.create_working_folder()

        random_file_name = '%s%s' % (helper.random_string(10), ext)
        origin = '%s/%s' % (folder, random_file_name)
        file_path = helper.get_file(file)
        if file_path is False:
            file_path = helper.download_file(file, folder)

        shutil.copyfile(file_path, origin)

        media = Media.get_class_by_file(origin, [Audio, Media, Photo, Video])
        metadata = media.get_metadata()
        media.set_original_name()
        metadata_updated = media.get_metadata()

        shutil.rmtree(folder)

        assert metadata['original_name'] is None, metadata['original_name']
        assert metadata_updated['original_name'] == random_file_name, metadata_updated['original_name']

def is_valid():
    media = Media()

    assert not media.is_valid()
