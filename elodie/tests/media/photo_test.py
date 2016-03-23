# -*- coding: utf-8
# Project imports
import os
import sys

from datetime import datetime
import shutil
import tempfile
import time

from nose.plugins.skip import SkipTest

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import helper
from elodie.media.media import Media
from elodie.media.photo import Photo

os.environ['TZ'] = 'GMT'

def test_photo_extensions():
    photo = Photo()
    extensions = photo.extensions

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

def test_get_date_taken():
    photo = Photo(helper.get_file('plain.jpg'))
    date_taken = photo.get_date_taken()

#    assert date_taken == (2015, 12, 5, 0, 59, 26, 5, 339, 0), date_taken
    assert date_taken == helper.time_convert((2015, 12, 5, 0, 59, 26, 5, 339, 0)), date_taken

def test_get_date_taken_without_exif():
    source = helper.get_file('no-exif.jpg')
    photo = Photo(source)
    date_taken = photo.get_date_taken()

    date_taken_from_file = time.gmtime(min(os.path.getmtime(source), os.path.getctime(source)))

    assert date_taken == date_taken_from_file, date_taken

def test_is_valid():
    photo = Photo(helper.get_file('with-location.jpg'))

    assert photo.is_valid()

def test_is_not_valid():
    photo = Photo(helper.get_file('text.txt'))

    assert not photo.is_valid()

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
    raise SkipTest('gh-31, precision is lost in conversion from decimal to dms')
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
    assert metadata['latitude'] == 11.1111111111, metadata['latitude']
    assert metadata['longitude'] == 99.9999999999, metadata['longitude']

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
    utf8_title = unicode_title.encode('utf-8')

    status = photo.set_title(unicode_title)
    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['title'] == utf8_title, metadata['title']

def test_get_metadata_from_nef():
    temporary_folder, folder = helper.create_working_folder()

    photo_file = helper.get_file('photo.nef')
    origin = '%s/photo.nef' % folder

    if not photo_file:
        photo_file = helper.download_file('photo.nef', folder)
        if not photo_file or not os.path.isfile(photo_file):
            raise SkipTest('nef file not downlaoded')

        # downloading for each test is costly so we save it in the working directory
        file_path_save_as = helper.get_file_path('photo.nef')
        if os.path.isfile(photo_file):
            shutil.copyfile(photo_file, file_path_save_as)

    shutil.copyfile(photo_file, origin)

    photo = Photo(origin)
    metadata = photo.get_metadata()

    shutil.rmtree(folder)

    assert metadata['date_taken'] == helper.time_convert((2008, 10, 24, 9, 12, 56, 4, 298, 0)), metadata['date_taken']

def test_set_metadata_on_nef():
    temporary_folder, folder = helper.create_working_folder()

    photo_file = helper.get_file('photo.nef')
    origin = '%s/photo.nef' % folder

    if not photo_file:
        photo_file = helper.download_file('photo.nef', folder)
        if not photo_file or not os.path.isfile(photo_file):
            raise SkipTest('nef file not downlaoded')

    shutil.copyfile(photo_file, origin)

    photo = Photo(origin)
    origin_metadata = photo.get_metadata()

    status = photo.set_location(11.1111111111, 99.9999999999)

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['date_taken'] == helper.time_convert((2008, 10, 24, 9, 12, 56, 4, 298, 0)), metadata['date_taken']
    assert helper.isclose(metadata['latitude'], 11.1111111111), metadata['latitude']
    assert helper.isclose(metadata['longitude'], 99.9999999999), metadata['longitude']

def test_get_metadata_from_dng():
    temporary_folder, folder = helper.create_working_folder()

    photo_file = helper.get_file('photo.dng')
    origin = '%s/photo.dng' % folder

    if not photo_file:
        photo_file = helper.download_file('photo.dng', folder)
        if not photo_file or not os.path.isfile(photo_file):
            raise SkipTest('dng file not downlaoded')

        # downloading for each test is costly so we save it in the working directory
        file_path_save_as = helper.get_file_path('photo.dng')
        if os.path.isfile(photo_file):
            shutil.copyfile(photo_file, file_path_save_as)

    shutil.copyfile(photo_file, origin)

    photo = Photo(origin)
    metadata = photo.get_metadata()

    shutil.rmtree(folder)

    assert metadata['date_taken'] == helper.time_convert((2009, 10, 20, 9, 10, 46, 1, 293, 0)), metadata['date_taken']

def test_set_metadata_on_dng():
    temporary_folder, folder = helper.create_working_folder()

    photo_file = helper.get_file('photo.dng')
    origin = '%s/photo.dng' % folder

    if not photo_file:
        photo_file = helper.download_file('photo.dng', folder)
        if not photo_file or not os.path.isfile(photo_file):
            raise SkipTest('dng file not downlaoded')

    shutil.copyfile(photo_file, origin)

    photo = Photo(origin)
    origin_metadata = photo.get_metadata()

    status = photo.set_location(11.1111111111, 99.9999999999)

    assert status == True, status

    photo_new = Photo(origin)
    metadata = photo_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['date_taken'] == helper.time_convert((2009, 10, 20, 9, 10, 46, 1, 293, 0)), metadata['date_taken']
    assert helper.isclose(metadata['latitude'], 11.1111111111), metadata['latitude']
    assert helper.isclose(metadata['longitude'], 99.9999999999), metadata['longitude']
