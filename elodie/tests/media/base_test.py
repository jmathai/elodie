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

os.environ['TZ'] = 'GMT'


def test_set_album_from_folder_invalid_file():
    temporary_folder, folder = helper.create_working_folder()

    base_file = helper.get_file('invalid.jpg')
    origin = '%s/invalid.jpg' % folder

    shutil.copyfile(base_file, origin)

    base = Base(origin)

    status = base.set_album_from_folder()

    assert status == False, status

