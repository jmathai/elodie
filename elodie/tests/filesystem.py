# Project imports
import os
import sys

import random
import shutil
import string
import tempfile

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from elodie import filesystem

filesystem = filesystem.FileSystem()

def test_create_directory_success():
    folder = '%s/%s' % (tempfile.gettempdir(), random_string(10))
    status = filesystem.create_directory(folder)

    # Needs to be a subdirectory
    assert tempfile.gettempdir() != folder

    assert status == True
    assert os.path.isdir(folder) == True
    assert os.path.exists(folder) == True
    
    # Clean up
    shutil.rmtree(folder)


def test_create_directory_recursive_success():
    folder = '%s/%s/%s' % (tempfile.gettempdir(), random_string(10), random_string(10))
    status = filesystem.create_directory(folder)

    # Needs to be a subdirectory
    assert tempfile.gettempdir() != folder

    assert status == True
    assert os.path.isdir(folder) == True
    assert os.path.exists(folder) == True

    shutil.rmtree(folder)

def test_create_directory_invalid_permissions():
    status = filesystem.create_directory('/apathwhichdoesnotexist/afolderwhichdoesnotexist')

    assert status == False


def random_string(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))
