# -*- coding: utf-8
# Project imports
from __future__ import print_function
import os
import sys

import shutil
import tempfile
import time
import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))))
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

import helper
from elodie.media.media import Media
from elodie.media.video import Video
from elodie.media.audio import Audio
from elodie.external.pyexiftool import ExifTool
from elodie.dependencies import get_exiftool
from elodie import constants

os.environ['TZ'] = 'GMT'

def setup_module():
    exiftool_addedargs = [
            u'-config',
            u'"{}"'.format(constants.exiftool_config)
        ]
    ExifTool(executable_=get_exiftool(), addedargs=exiftool_addedargs).start()

def teardown_module():
    ExifTool().terminate

def test_audio_extensions():
    audio = Audio()
    extensions = audio.extensions

    assert 'm4a' in extensions

    valid_extensions = Audio.get_valid_extensions()

    assert extensions == valid_extensions, valid_extensions

def test_get_coordinate():
    audio = Audio(helper.get_file('audio.m4a'))
    coordinate = audio.get_coordinate()

    assert helper.isclose(coordinate, 29.758938), coordinate

def test_get_camera_make():
    audio = Audio(helper.get_file('audio.m4a'))
    coordinate = audio.get_camera_make()

    assert coordinate is None, coordinate

def test_get_camera_model():
    audio = Audio(helper.get_file('audio.m4a'))
    coordinate = audio.get_camera_model()

    assert coordinate is None, coordinate

def test_get_coordinate_latitude():
    audio = Audio(helper.get_file('audio.m4a'))
    coordinate = audio.get_coordinate('latitude')

    assert helper.isclose(coordinate, 29.758938), coordinate

def test_get_coordinate_longitude():
    audio = Audio(helper.get_file('audio.m4a'))
    coordinate = audio.get_coordinate('longitude')

    assert helper.isclose(coordinate, -95.3677), coordinate

def test_get_date_taken():
    audio = Audio(helper.get_file('audio.m4a'))
    date_taken = audio.get_date_taken()

    assert date_taken == (2016, 1, 4, 5, 28, 15, 0, 4, 0), date_taken

def test_get_exiftool_attributes():
    audio = Video(helper.get_file('audio.m4a'))
    exif = audio.get_exiftool_attributes()

    assert exif is not None, exif
    assert exif is not False, exif

def test_is_valid():
    audio = Audio(helper.get_file('audio.m4a'))

    assert audio.is_valid()

def test_is_not_valid():
    audio = Audio(helper.get_file('text.txt'))

    assert not audio.is_valid()

def test_set_date_taken():
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

def test_set_location_minus():
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    audio = Audio(origin)
    origin_metadata = audio.get_metadata()

    # Verify that original audio has different location info that what we
    #   will be setting and checking
    assert not helper.isclose(origin_metadata['latitude'], 11.111111), origin_metadata['latitude']
    assert not helper.isclose(origin_metadata['longitude'], 99.999999), origin_metadata['longitude']

    status = audio.set_location(-11.111111, -99.999999)

    assert status == True, status

    audio_new = Audio(origin)
    metadata = audio_new.get_metadata()

    shutil.rmtree(folder)

    assert helper.isclose(metadata['latitude'], -11.111111), metadata['latitude']
    assert helper.isclose(metadata['longitude'], -99.999999), metadata['longitude']

def test_set_title():
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
    temporary_folder, folder = helper.create_working_folder()

    origin = '%s/audio.m4a' % folder
    shutil.copyfile(helper.get_file('audio.m4a'), origin)

    audio = Audio(origin)
    origin_metadata = audio.get_metadata()

    unicode_title = u'形声字 / 形聲字'
    status = audio.set_title(unicode_title)

    assert status == True, status

    audio_new = Audio(origin)
    metadata = audio_new.get_metadata()

    shutil.rmtree(folder)

    assert metadata['title'] == unicode_title, metadata['title']
