import hashlib
import os
import random
import shutil
import string
import tempfile

def checksum(file_path, blocksize=65536):
    hasher = hashlib.sha256()
    with open(file_path, 'r') as f:
        buf = f.read(blocksize)

        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)
        return hasher.hexdigest()
    return None

def create_working_folder():
    temporary_folder = tempfile.gettempdir()
    folder = '%s/%s/%s' % (temporary_folder, random_string(10), random_string(10))
    os.makedirs(folder)

    return (temporary_folder, folder)

def get_file(name):
    current_folder = os.path.dirname(os.path.realpath(__file__))
    return '%s/files/%s' % (current_folder, name)

def get_test_location():
    return (61.013710, 99.196656, 'Siberia')

def populate_folder(number_of_files):
    folder = '%s/%s' % (tempfile.gettempdir(), random_string(10))
    os.makedirs(folder)

    for x in range(0, number_of_files):
        ext = 'jpg' if x % 2 == 0 else 'txt'
        fname = '%s/%s.%s' % (folder, x, ext)
        with open(fname, 'a'):
            os.utime(fname, None)

    return folder

def random_string(length):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))

def random_decimal():
    return random.random()

def random_coordinate(coordinate, precision):
    # Here we add to the decimal section of the coordinate by a given precision
    return coordinate + ((10.0 / (10.0**precision)) * random_decimal())

def temp_dir():
    return tempfile.gettempdir()
