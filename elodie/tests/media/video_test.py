# -*- coding: utf-8
# Project imports
import os
import sys

import shutil
import tempfile
import time
import datetime

from nose.plugins.skip import SkipTest

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import helper
from elodie.media.media import Media
from elodie.media.video import Video

os.environ['TZ'] = 'GMT'

def test_video_extensions():
    video = Video()
    extensions = video.extensions

    assert 'avi' in extensions
    assert 'm4v' in extensions
    assert 'mov' in extensions
    assert 'm4v' in extensions
    assert '3gp' in extensions

    valid_extensions = Video.get_valid_extensions()

    assert extensions == valid_extensions, valid_extensions

def test_get_coordinate():
    video = Video(helper.get_file('video.mov'))
    coordinate = video.get_coordinate()

    assert coordinate == 38.189299999999996, coordinate

def test_get_coordinate_latitude():
    video = Video(helper.get_file('video.mov'))
    coordinate = video.get_coordinate('latitude')

    assert coordinate == 38.189299999999996, coordinate

def test_get_coordinate_longitude():
    video = Video(helper.get_file('video.mov'))
    coordinate = video.get_coordinate('longitude')

    assert coordinate == -119.9558, coordinate

def test_get_date_taken():
    video = Video(helper.get_file('video.mov'))
    date_taken = video.get_date_taken()

    assert date_taken == (2015, 1, 19, 12, 45, 11, 0, 19, 0), date_taken

def test_get_exif():
    video = Video(helper.get_file('video.mov'))
    exif = video.get_exif()

    assert exif is not None, exif

def test_is_valid():
    video = Video(helper.get_file('video.mov'))

    assert video.is_valid()

def test_is_not_valid():
    video = Video(helper.get_file('text.txt'))

    assert not video.is_valid()

def test_set_date_taken():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    video = Video(origin)
    status = video.set_date_taken(datetime.datetime(2013, 9, 30, 7, 6, 5))

    assert status == True, status

    video_new = Video(origin)
    metadata = video_new.get_metadata()

    date_taken = metadata['date_taken']

    shutil.rmtree(folder)

    assert date_taken == (2013, 9, 30, 7, 6, 5, 0, 273, 0), metadata['date_taken']

def test_set_location():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    raise SkipTest('gh-31, precision is lost in conversion from decimal to dms')
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    video = Video(origin)
    origin_metadata = video.get_metadata()

    # Verify that original photo has no location information
    #assert origin_metadata['latitude'] is None, origin_metadata['latitude']
    #assert origin_metadata['longitude'] is None, origin_metadata['longitude']

    status = video.set_location(11.1111111111, 99.9999999999)

    assert status == True, status

    video_new = Video(origin)
    metadata = video_new.get_metadata()

    shutil.rmtree(folder)

    # @TODO: understand why the decimal to degree conversion loses accuracy
    assert metadata['latitude'] == 11.1111111111, metadata['latitude']
    assert metadata['longitude'] == 99.9999999999, metadata['longitude']

def test_set_title():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    video = Video(origin)
    origin_metadata = video.get_metadata()

    status = video.set_title('my video title')

    assert status == True, status

    video_new = Video(origin)
    metadata = video_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['title'] == 'my video title', metadata['title']

def test_set_title_non_ascii():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    raise SkipTest('gh-27, non-ascii characters')
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/video.mov' % folder
    shutil.copyfile(helper.get_file('video.mov'), origin)

    video = Video(origin)
    origin_metadata = video.get_metadata()

    status = video.set_title('形声字 / 形聲字')

    assert status == True, status

    video_new = Video(origin)
    metadata = video_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['title'] == '形声字 / 形聲字', metadata['title']

def can_edit_exif():
    video = Video()
    return video.get_avmetareadwrite()
