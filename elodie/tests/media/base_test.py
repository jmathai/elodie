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
from elodie.media.base import Base
from elodie.media.media import Media
from elodie.media.audio import Audio
from elodie.media.text import Text
from elodie.media.photo import Photo
from elodie.media.video import Video

os.environ['TZ'] = 'GMT'


def test_set_album_from_folder_invalid_file():
    temporary_folder, folder = helper.create_working_folder()

    base_file = helper.get_file('invalid.jpg')
    origin = '%s/invalid.jpg' % folder

    shutil.copyfile(base_file, origin)

    base = Base(origin)

    status = base.set_album_from_folder()

    assert status == False, status

def test_get_class_by_file_without_extension():
    base_file = helper.get_file('withoutextension')

    cls = Base.get_class_by_file(base_file, [Audio, Text, Photo, Video])
    
    assert cls is None, cls
