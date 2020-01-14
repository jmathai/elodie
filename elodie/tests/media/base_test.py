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
from elodie.media.base import Base, get_all_subclasses
from elodie.media.media import Media
from elodie.media.audio import Audio
from elodie.media.text import Text
from elodie.media.photo import Photo
from elodie.media.video import Video

os.environ['TZ'] = 'GMT'

setup_module = helper.setup_module
teardown_module = helper.teardown_module

def test_get_all_subclasses():
    subclasses = get_all_subclasses(Base)
    expected = {Media, Base, Text, Photo, Video, Audio}
    assert subclasses == expected, subclasses

def test_get_class_by_file_without_extension():
    base_file = helper.get_file('withoutextension')

    cls = Base.get_class_by_file(base_file, [Audio, Text, Photo, Video])
    
    assert cls is None, cls

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

def test_set_album_from_folder_invalid_file():
    temporary_folder, folder = helper.create_working_folder()

    base_file = helper.get_file('invalid.jpg')
    origin = '%s/invalid.jpg' % folder

    shutil.copyfile(base_file, origin)

    base = Base(origin)

    status = base.set_album_from_folder()

    assert status == False, status

def test_set_album_from_folder():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    metadata = photo.get_metadata()

    assert metadata['album'] is None, metadata['album']

    new_album_name = os.path.split(folder)[1]
    status = photo.set_album_from_folder()

    assert status == True, status

    photo_new = Photo(origin)
    metadata_new = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata_new['album'] == new_album_name, metadata_new['album']

def test_set_metadata():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)

    metadata = photo.get_metadata()

    assert metadata['title'] == None, metadata['title']

    new_title = 'Some Title'
    photo.set_metadata(title = new_title)

    new_metadata = photo.get_metadata()

    assert new_metadata['title'] == new_title, new_metadata['title']

def test_set_metadata_basename():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)

    metadata = photo.get_metadata()

    assert metadata['base_name'] == 'photo', metadata['base_name']

    new_basename = 'Some Base Name'
    photo.set_metadata_basename(new_basename)

    new_metadata = photo.get_metadata()

    assert new_metadata['base_name'] == new_basename, new_metadata['base_name']
