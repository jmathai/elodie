# -*- coding: utf-8
# Project imports
from __future__ import unicode_literals
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
from elodie.media.media import Media
from elodie.media.photo import Photo

os.environ['TZ'] = 'GMT'

setup_module = helper.setup_module
teardown_module = helper.teardown_module

def test_photo_extensions():
    photo = Photo()
    extensions = photo.extensions

    assert 'arw' in extensions
    assert 'cr2' in extensions
    assert 'dng' in extensions
    assert 'gif' in extensions
    assert 'heic' in extensions
    assert 'jpg' in extensions
    assert 'jpeg' in extensions
    assert 'nef' in extensions
    assert 'png' in extensions
    assert 'rw2' in extensions

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

def test_get_metadata_of_invalid_photo():
    photo = Photo(helper.get_file('invalid.jpg'))
    metadata = photo.get_metadata()

    assert metadata is None

def test_get_coordinate_default():
    photo = Photo(helper.get_file('with-location.jpg'))
    coordinate = photo.get_coordinate()

    assert helper.isclose(coordinate,37.3667027222), coordinate

def test_get_coordinate_latitude():
    photo = Photo(helper.get_file('with-location.jpg'))
    coordinate = photo.get_coordinate('latitude')

    assert helper.isclose(coordinate,37.3667027222), coordinate

def test_get_coordinate_latitude_minus():
    photo = Photo(helper.get_file('with-location-inv.jpg'))
    coordinate = photo.get_coordinate('latitude')

    assert helper.isclose(coordinate,-37.3667027222), coordinate

def test_get_coordinate_longitude():
    photo = Photo(helper.get_file('with-location.jpg'))
    coordinate = photo.get_coordinate('longitude')

    assert helper.isclose(coordinate,-122.033383611), coordinate

def test_get_coordinate_longitude_plus():
    photo = Photo(helper.get_file('with-location-inv.jpg'))
    coordinate = photo.get_coordinate('longitude')

    assert helper.isclose(coordinate,122.033383611), coordinate

def test_get_coordinates_without_exif():
    photo = Photo(helper.get_file('no-exif.jpg'))
    latitude = photo.get_coordinate('latitude')
    longitude = photo.get_coordinate('longitude')

    assert latitude is None, latitude
    assert longitude is None, longitude

def test_get_coordinates_with_zero_coordinate():
    photo = Photo(helper.get_file('with-location-zero-coordinate.jpg'))
    latitude = photo.get_coordinate('latitude')
    longitude = photo.get_coordinate('longitude')

    assert helper.isclose(latitude,51.55325), latitude
    assert helper.isclose(longitude,-0.00417777777778), longitude

def test_get_coordinates_with_null_coordinate():
    photo = Photo(helper.get_file('with-null-coordinates.jpg'))
    latitude = photo.get_coordinate('latitude')
    longitude = photo.get_coordinate('longitude')

    assert latitude is None, latitude
    assert longitude is None, longitude

def test_get_date_taken():
    photo = Photo(helper.get_file('plain.jpg'))
    date_taken = photo.get_date_taken()

    #assert date_taken == (2015, 12, 5, 0, 59, 26, 5, 339, 0), date_taken
    assert date_taken == helper.time_convert((2015, 12, 5, 0, 59, 26, 5, 339, 0)), date_taken

def test_get_date_taken_without_exif():
    source = helper.get_file('no-exif.jpg')
    photo = Photo(source)
    date_taken = photo.get_date_taken()

    date_taken_from_file = time.gmtime(min(os.path.getmtime(source), os.path.getctime(source)))

    assert date_taken == date_taken_from_file, date_taken

def test_get_camera_make():
    photo = Photo(helper.get_file('with-location.jpg'))
    make = photo.get_camera_make()

    assert make == 'Canon', make

def test_get_camera_make_not_set():
    photo = Photo(helper.get_file('no-exif.jpg'))
    make = photo.get_camera_make()

    assert make is None, make

def test_get_camera_model():
    photo = Photo(helper.get_file('with-location.jpg'))
    model = photo.get_camera_model()

    assert model == 'Canon EOS REBEL T2i', model

def test_get_camera_model_not_set():
    photo = Photo(helper.get_file('no-exif.jpg'))
    model = photo.get_camera_model()

    assert model is None, model

def test_is_valid():
    photo = Photo(helper.get_file('with-location.jpg'))

    assert photo.is_valid()

def test_is_not_valid():
    photo = Photo(helper.get_file('text.txt'))

    assert not photo.is_valid()

def test_is_valid_fallback_using_pillow():
    photo = Photo(helper.get_file('imghdr-error.jpg'))

    assert photo.is_valid()


def test_set_album():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    metadata = photo.get_metadata()

    assert metadata['album'] is None, metadata['album']

    status = photo.set_album('Test Album')

    assert status == True, status

    photo_new = Photo(origin)
    metadata_new = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata_new['album'] == 'Test Album', metadata_new['album']

def test_set_date_taken_with_missing_datetimeoriginal():
    # When datetimeoriginal (or other key) is missing we have to add it gh-74
    # https://github.com/jmathai/elodie/issues/74
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('no-exif.jpg'), origin)

    photo = Photo(origin)
    status = photo.set_date_taken(datetime(2013, 9, 30, 7, 6, 5))

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    date_taken = metadata['date_taken']

    shutil.rmtree(folder)

    #assert date_taken == (2013, 9, 30, 7, 6, 5, 0, 273, 0), metadata['date_taken']
    assert date_taken == helper.time_convert((2013, 9, 30, 7, 6, 5, 0, 273, 0)), metadata['date_taken']

def test_set_date_taken():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    status = photo.set_date_taken(datetime(2013, 9, 30, 7, 6, 5))

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    date_taken = metadata['date_taken']

    shutil.rmtree(folder)

    #assert date_taken == (2013, 9, 30, 7, 6, 5, 0, 273, 0), metadata['date_taken']
    assert date_taken == helper.time_convert((2013, 9, 30, 7, 6, 5, 0, 273, 0)), metadata['date_taken']

def test_set_location():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    origin_metadata = photo.get_metadata()

    # Verify that original photo has different location info that what we
    #   will be setting and checking
    assert not helper.isclose(origin_metadata['latitude'], 11.1111111111), origin_metadata['latitude']
    assert not helper.isclose(origin_metadata['longitude'], 99.9999999999), origin_metadata['longitude']

    status = photo.set_location(11.1111111111, 99.9999999999)

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert helper.isclose(metadata['latitude'], 11.1111111111), metadata['latitude']
    assert helper.isclose(metadata['longitude'], 99.9999999999), metadata['longitude']

def test_set_location_minus():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    origin_metadata = photo.get_metadata()

    # Verify that original photo has different location info that what we
    #   will be setting and checking
    assert not helper.isclose(origin_metadata['latitude'], 11.1111111111), origin_metadata['latitude']
    assert not helper.isclose(origin_metadata['longitude'], 99.9999999999), origin_metadata['longitude']

    status = photo.set_location(-11.1111111111, -99.9999999999)

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert helper.isclose(metadata['latitude'], -11.1111111111), metadata['latitude']
    assert helper.isclose(metadata['longitude'], -99.9999999999), metadata['longitude']

def test_set_title():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    origin_metadata = photo.get_metadata()

    status = photo.set_title('my photo title')

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['title'] == 'my photo title', metadata['title']

def test_set_title_non_ascii():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/photo.jpg' % folder
    shutil.copyfile(helper.get_file('plain.jpg'), origin)

    photo = Photo(origin)
    origin_metadata = photo.get_metadata()

    unicode_title = u'形声字 / 形聲字'

    status = photo.set_title(unicode_title)
    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['title'] == unicode_title, metadata['title']

# This is a test generator that will test reading and writing to
# various RAW formats. Each sample file has a different date which
# is the only information which needs to be added to run the tests
# for that file type.
# https://nose.readthedocs.io/en/latest/writing_tests.html#test-generators
def test_various_types():
    types = Photo.extensions
    #extensions = ('arw', 'cr2', 'dng', 'gif', 'jpeg', 'jpg', 'nef', 'rw2')
    dates = {
        'arw': (2007, 4, 8, 17, 41, 18, 6, 98, 0),
        'cr2': (2005, 10, 29, 16, 14, 44, 5, 302, 0),
        'dng': (2009, 10, 20, 9, 10, 46, 1, 293, 0),
        'heic': (2019, 5, 26, 10, 33, 20, 6, 146, 0),
        'nef': (2008, 10, 24, 9, 12, 56, 4, 298, 0),
        'png': (2015, 1, 18, 12, 1, 1, 6, 18, 0),
        'rw2': (2014, 11, 19, 23, 7, 44, 2, 323, 0)
    }

    for type in types:
        if type in dates:
            yield (_test_photo_type_get, type, dates[type])
            yield (_test_photo_type_set, type, dates[type])

def _test_photo_type_get(type, date):
    temporary_folder, folder = helper.create_working_folder()

    photo_name = 'photo.{}'.format(type)
    photo_file = helper.get_file(photo_name)
    origin = '{}/{}'.format(folder, photo_name)

    if not photo_file:
        photo_file = helper.download_file(photo_name, folder)
        if not photo_file or not os.path.isfile(photo_file):
            pytest.skip('{} file not downlaoded'.format(type))

        # downloading for each test is costly so we save it in the working directory
        file_path_save_as = helper.get_file_path(photo_name)
        if os.path.isfile(photo_file):
            shutil.copyfile(photo_file, file_path_save_as)

    shutil.copyfile(photo_file, origin)

    photo = Photo(origin)
    metadata = photo.get_metadata()

    shutil.rmtree(folder)

    assert metadata['date_taken'] == helper.time_convert(date), '{} date {}'.format(type, metadata['date_taken'])

def _test_photo_type_set(type, date):
    temporary_folder, folder = helper.create_working_folder()

    photo_name = 'photo.{}'.format(type)
    photo_file = helper.get_file(photo_name)
    origin = '{}/{}'.format(folder, photo_name)

    if not photo_file:
        photo_file = helper.download_file(photo_name, folder)
        if not photo_file or not os.path.isfile(photo_file):
            pytest.skip('{} file not downlaoded'.format(type))

    shutil.copyfile(photo_file, origin)

    photo = Photo(origin)
    origin_metadata = photo.get_metadata()

    status = photo.set_location(11.1111111111, 99.9999999999)

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['date_taken'] == helper.time_convert(date), '{} date {}'.format(type, metadata['date_taken'])
    assert helper.isclose(metadata['latitude'], 11.1111111111), '{} lat {}'.format(type, metadata['latitude'])
    assert helper.isclose(metadata['longitude'], 99.9999999999), '{} lon {}'.format(type, metadata['latitude'])
