# -*- coding: utf-8
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
import datetime

from nose.plugins.skip import SkipTest

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import helper
from elodie.media.media import Media
from elodie.media.photo import Photo

os.environ['TZ'] = 'GMT'

def test_photo_extensions():
    photo = Photo()
    extensions = photo.photo_extensions

    assert 'jpg' in extensions
    assert 'jpeg' in extensions
    assert 'nef' in extensions
    assert 'dng' in extensions
    assert 'gif' in extensions

    valid_extensions = Photo.get_valid_extensions()

    assert extensions == valid_extensions, valid_extensions

def test_empty_album():
    photo = Photo(helper.get_file('plain.jpg'))
    assert photo.get_album() is None

def test_has_album():
    photo = Photo(helper.get_file('with-album.jpg'))
    album = photo.get_album()

    assert album == 'Test Album', album

def test_is_valid():
    photo = Photo(helper.get_file('plain.jpg'))

    assert photo.is_valid()

def test_is_not_valid():
    photo = Photo(helper.get_file('text.txt'))

    assert not photo.is_valid()

def test_get_coordinate_default():
    photo = Photo(helper.get_file('with-location.jpg'))
    coordinate = photo.get_coordinate()

    assert coordinate == 37.3667027222, coordinate

def test_get_coordinate_latitude():
    photo = Photo(helper.get_file('with-location.jpg'))
    coordinate = photo.get_coordinate('latitude')

    assert coordinate == 37.3667027222, coordinate

def test_get_coordinate_longitude():
    photo = Photo(helper.get_file('with-location.jpg'))
    coordinate = photo.get_coordinate('longitude')

    assert coordinate == -122.033383611, coordinate

def test_is_valid():
    photo = Photo(helper.get_file('with-location.jpg'))

    assert photo.is_valid()

def test_is_not_valid():
    photo = Photo(helper.get_file('text.txt'))

    assert not photo.is_valid()

def test_set_date_taken():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    status = photo.set_date_taken(datetime.datetime(2013, 9, 30, 7, 6, 5))

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    date_taken = metadata['date_taken']

    shutil.rmtree(folder)

    assert date_taken == (2013, 9, 30, 7, 6, 5, 0, 273, 0), metadata['date_taken']

def test_set_location():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    origin_metadata = photo.get_metadata()

    # Verify that original photo has no location information
    assert origin_metadata['latitude'] is None, origin_metadata['latitude']
    assert origin_metadata['longitude'] is None, origin_metadata['longitude']

    status = photo.set_location(11.1111111111, 99.9999999999)

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    # @TODO: understand why the decimal to degree conversion loses accuracy
    assert metadata['latitude'] == 11.1001851852, metadata['latitude']
    assert metadata['longitude'] == 99.9836111111, metadata['longitude']

def test_set_title():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    origin_metadata = photo.get_metadata()

    # Verify that original photo has no location information
    assert origin_metadata['latitude'] is None, origin_metadata['latitude']
    assert origin_metadata['longitude'] is None, origin_metadata['longitude']

    status = photo.set_title('my photo title')

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['title'] == 'my photo title', metadata['title']

def test_set_title_non_ascii():
    raise SkipTest('gh-27, non-ascii characters')
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    origin_metadata = photo.get_metadata()

    # Verify that original photo has no location information
    assert origin_metadata['latitude'] is None, origin_metadata['latitude']
    assert origin_metadata['longitude'] is None, origin_metadata['longitude']

    status = photo.set_title('形声字 / 形聲字')

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['title'] == '形声字 / 形聲字', metadata['title']
