# -*- coding: utf-8
# Project imports
import os
import sys

from datetime import datetime
import shutil
import tempfile
import time

import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import helper
from elodie.media.base import Base
from elodie.media.text import Text

os.environ['TZ'] = 'GMT'

def test_text_extensions():
    text = Text()
    extensions = text.extensions

    assert 'txt' in extensions

    valid_extensions = Text.get_valid_extensions()

    assert extensions == valid_extensions, valid_extensions

def test_get_original_name():
    media = Text(helper.get_file('with-original-name.txt'))
    original_name = media.get_original_name()

    assert original_name == 'originalname.txt', original_name

def test_get_original_name_when_does_not_exist():
    media = Text(helper.get_file('valid.txt'))
    original_name = media.get_original_name()

    assert original_name is None, original_name

def test_get_title():
    text = Text(helper.get_file('valid.txt'))
    text.get_metadata()
    assert text.get_title() == 'sample title', text.get_title()

def test_get_default_coordinate():
    text = Text(helper.get_file('valid.txt'))
    text.get_metadata()
    assert text.get_coordinate() == '51.521435', text.get_coordinate()

def test_get_coordinate_latitude():
    text = Text(helper.get_file('valid.txt'))
    text.get_metadata()
    assert text.get_coordinate('latitude') == '51.521435', text.get_coordinate('latitude')

def test_get_coordinate_longitude():
    text = Text(helper.get_file('valid.txt'))
    text.get_metadata()
    assert text.get_coordinate('longitude') == '0.162714', text.get_coordinate('longitude')

def test_get_date_taken():
    text = Text(helper.get_file('valid.txt'))
    text.get_metadata()

    date_taken = text.get_date_taken()

    assert date_taken == helper.time_convert((2016, 4, 7, 11, 15, 26, 3, 98, 0)), date_taken

def test_get_date_taken_from_invalid():
    origin = helper.get_file('valid-without-header.txt')
    text = Text(origin)
    text.get_metadata()

    date_taken = text.get_date_taken()

    seconds_since_epoch = min(
        os.path.getmtime(origin),
        os.path.getctime(origin)
    )
    expected_date_taken = time.gmtime(seconds_since_epoch)

    assert date_taken == expected_date_taken, date_taken

def test_get_metadata_with_numeric_header():
    # See gh-98 for details
    text = Text(helper.get_file('valid-with-numeric-header.txt'))

    # Should not throw error
    # TypeError: argument of type 'int' is not iterable
    metadata = text.get_metadata()

    assert metadata['mime_type'] == 'text/plain'

def test_set_album():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/text.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    text = Text(origin)
    metadata = text.get_metadata()

    with open(origin, 'r') as f:
        f.readline()
        contents = f.read()

    album_name = 'Test Album'
    assert album_name != metadata['album']

    status = text.set_album(album_name)
    assert status == True, status

    text_new = Text(origin)
    metadata_new = text_new.get_metadata()

    with open(origin, 'r') as f:
        f.readline()
        contents_new = f.read()
        assert contents == contents_new, contents_new

    shutil.rmtree(folder)

    assert album_name == metadata_new['album'], metadata_new

def test_set_date_taken():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/text.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    text = Text(origin)
    metadata = text.get_metadata()

    with open(origin, 'r') as f:
        f.readline()
        contents = f.read()

    assert helper.time_convert((2013, 9, 30, 7, 6, 5, 0, 273, 0)) != metadata['date_taken'], metadata['date_taken']

    status = text.set_date_taken(datetime(2013, 9, 30, 7, 6, 5))
    assert status == True, status

    text_new = Text(origin)
    metadata_new = text_new.get_metadata()

    with open(origin, 'r') as f:
        f.readline()
        contents_new = f.read()
        assert contents == contents_new, contents_new

    shutil.rmtree(folder)

    assert helper.time_convert((2013, 9, 30, 7, 6, 5, 0, 273, 0)) == metadata_new['date_taken'], metadata_new['date_taken']

def test_set_location():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/text.txt' % folder
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    text = Text(origin)
    origin_metadata = text.get_metadata()

    with open(origin, 'r') as f:
        f.readline()
        contents = f.read()

    # Verify that original photo has different location info that what we
    #   will be setting and checking
    assert not helper.isclose(origin_metadata['latitude'], 11.1111111111), origin_metadata['latitude']
    assert not helper.isclose(origin_metadata['longitude'], 99.9999999999), origin_metadata['longitude']

    status = text.set_location(11.1111111111, 99.9999999999)

    assert status == True, status

    text_new = Text(origin)
    metadata = text_new.get_metadata()

    with open(origin, 'r') as f:
        f.readline()
        contents_new = f.read()
        assert contents == contents_new, contents_new

    shutil.rmtree(folder)

    assert helper.isclose(metadata['latitude'], 11.1111111111), metadata['latitude']

def test_set_album_without_header():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/text.txt' % folder
    shutil.copyfile(helper.get_file('valid-without-header.txt'), origin)

    text = Text(origin)
    metadata = text.get_metadata()

    with open(origin, 'r') as f:
        contents = f.read()

    album_name = 'Test Album'
    assert album_name != metadata['album']

    status = text.set_album(album_name)
    assert status == True, status

    text_new = Text(origin)
    metadata_new = text_new.get_metadata()

    with open(origin, 'r') as f:
        f.readline()
        contents_new = f.read()
        assert contents == contents_new, contents_new

    shutil.rmtree(folder)

    assert album_name == metadata_new['album'], metadata_new

def test_set_date_taken_without_header():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/text.txt' % folder
    shutil.copyfile(helper.get_file('valid-without-header.txt'), origin)

    text = Text(origin)
    metadata = text.get_metadata()

    with open(origin, 'r') as f:
        contents = f.read()

    assert helper.time_convert((2013, 9, 30, 7, 6, 5, 0, 273, 0)) != metadata['date_taken'], metadata['date_taken']

    status = text.set_date_taken(datetime(2013, 9, 30, 7, 6, 5))
    assert status == True, status

    text_new = Text(origin)
    metadata_new = text_new.get_metadata()

    with open(origin, 'r') as f:
        f.readline()
        contents_new = f.read()
        assert contents == contents_new, contents_new

    shutil.rmtree(folder)

    assert helper.time_convert((2013, 9, 30, 7, 6, 5, 0, 273, 0)) == metadata_new['date_taken'], metadata_new['date_taken']

def test_set_location_without_header():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/text.txt' % folder
    shutil.copyfile(helper.get_file('valid-without-header.txt'), origin)

    text = Text(origin)
    origin_metadata = text.get_metadata()

    with open(origin, 'r') as f:
        contents = f.read()

    # Verify that original photo has different location info that what we
    #   will be setting and checking
    assert not helper.isclose(origin_metadata['latitude'], 11.1111111111), origin_metadata['latitude']
    assert not helper.isclose(origin_metadata['longitude'], 99.9999999999), origin_metadata['longitude']

    status = text.set_location(11.1111111111, 99.9999999999)

    assert status == True, status

    text_new = Text(origin)
    metadata = text_new.get_metadata()

    with open(origin, 'r') as f:
        f.readline()
        contents_new = f.read()
        assert contents == contents_new, contents_new

    shutil.rmtree(folder)

    assert helper.isclose(metadata['latitude'], 11.1111111111), metadata['latitude']

def test_set_original_name():
    temporary_folder, folder = helper.create_working_folder()

    random_file_name = '%s.txt' % helper.random_string(10)
    origin = '%s/%s' % (folder, random_file_name)
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    text = Text(origin)
    metadata = text.get_metadata()
    text.set_original_name()
    metadata_updated = text.get_metadata()

    shutil.rmtree(folder)

    assert metadata['original_name'] is None, metadata['original_name']
    assert metadata_updated['original_name'] == random_file_name, metadata_updated['original_name']

def test_set_original_name_with_arg():
    temporary_folder, folder = helper.create_working_folder()

    random_file_name = '%s.txt' % helper.random_string(10)
    origin = '%s/%s' % (folder, random_file_name)
    shutil.copyfile(helper.get_file('valid.txt'), origin)

    new_name = helper.random_string(15)

    text = Text(origin)
    metadata = text.get_metadata()
    text.set_original_name(new_name)
    metadata_updated = text.get_metadata()

    shutil.rmtree(folder)

    assert metadata['original_name'] is None, metadata['original_name']
    assert metadata_updated['original_name'] == new_name, metadata_updated['original_name']
