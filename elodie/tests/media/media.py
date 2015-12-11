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
from elodie.media.media import Media
from elodie.media.photo import Photo
from elodie.media.video import Video

os.environ['TZ'] = 'GMT'

def test_exiftool():
    media = Media()
    exiftool = media.get_exiftool()

    assert exiftool is not None, exiftool

def test_get_file_path():
    media = Media(helper.get_file('plain.jpg'))
    path = media.get_file_path()

    assert 'plain.jpg' in path, path

def is_valid():
    media = Media()

    assert not media.is_valid()
