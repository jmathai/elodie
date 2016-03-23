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

def is_valid():
    media = Media()

    assert not media.is_valid()
