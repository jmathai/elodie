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
from elodie.media.audio import Audio

os.environ['TZ'] = 'GMT'

def test_audio_extensions():
    audio = Audio()
    extensions = audio.extensions

    assert 'm4a' in extensions

    valid_extensions = Audio.get_valid_extensions()

    assert extensions == valid_extensions, valid_extensions

def test_get_coordinate():
    raise SkipTest('gh-61 this test fails on travisci')
    audio = Audio(helper.get_file('audio.m4a'))
    coordinate = audio.get_coordinate()

    assert coordinate == 29.75893888888889, coordinate

def test_get_coordinate_latitude():
    raise SkipTest('gh-61 this test fails on travisci')
    audio = Audio(helper.get_file('audio.m4a'))
    coordinate = audio.get_coordinate('latitude')

    assert coordinate == 29.75893888888889, coordinate

def test_get_coordinate_longitude():
    raise SkipTest('gh-61 this test fails on travisci')
    audio = Audio(helper.get_file('audio.m4a'))
    coordinate = audio.get_coordinate('longitude')

    assert coordinate == -95.3677, coordinate

def test_get_date_taken():
    raise SkipTest('gh-32 this test fails on travisci')
    audio = Audio(helper.get_file('audio.m4a'))
    date_taken = audio.get_date_taken()

    print '%r' % date_taken
    assert date_taken == (2016, 1, 4, 5, 24, 15, 0, 19, 0), date_taken

def test_get_exif():
    audio = Audio(helper.get_file('audio.m4a'))
    exif = audio.get_exif()

    assert exif is not None, exif

def test_is_valid():
    audio = Audio(helper.get_file('audio.m4a'))

    assert audio.is_valid()

def test_is_not_valid():
    audio = Audio(helper.get_file('text.txt'))

    assert not audio.is_valid()

def test_set_date_taken():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    audio = Audio(origin)
    status = audio.set_date_taken(datetime.datetime(2013, 9, 30, 7, 6, 5))

    assert status == True, status

    audio_new = Audio(origin)
    metadata = audio_new.get_metadata()

    date_taken = metadata['date_taken']

    shutil.rmtree(folder)

    assert date_taken == (2013, 9, 30, 7, 6, 5, 0, 273, 0), metadata['date_taken']

def test_set_location():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    audio = Audio(origin)
    origin_metadata = audio.get_metadata()

    # Verify that original audio has different location info that what we
    #   will be setting and checking
    assert not helper.isclose(origin_metadata['latitude'], 11.1111111111), origin_metadata['latitude']
    assert not helper.isclose(origin_metadata['longitude'], 99.9999999999), origin_metadata['longitude']

    status = audio.set_location(11.1111111111, 99.9999999999)

    assert status == True, status

    audio_new = Audio(origin)
    metadata = audio_new.get_metadata()

    shutil.rmtree(folder)

    assert helper.isclose(metadata['latitude'], 11.1111111111), metadata['latitude']
    assert helper.isclose(metadata['longitude'], 99.9999999999), metadata['longitude']

def test_set_title():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    audio = Audio(origin)
    origin_metadata = audio.get_metadata()

    status = audio.set_title('my audio title')

    assert status == True, status

    audio_new = Audio(origin)
    metadata = audio_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['title'] == 'my audio title', metadata['title']

def test_set_title_non_ascii():
    if not can_edit_exif():
        raise SkipTest('avmetareadwrite executable not found')

    raise SkipTest('gh-27, non-ascii characters')
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    audio = Audio(origin)
    origin_metadata = audio.get_metadata()

    status = audio.set_title('形声字 / 形聲字')

    assert status == True, status

    audio_new = Audio(origin)
    metadata = audio_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['title'] == '形声字 / 形聲字', metadata['title']

def can_edit_exif():
    audio = Audio()
    return audio.get_avmetareadwrite()
