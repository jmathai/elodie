from __future__ import division
from __future__ import unicode_literals
from builtins import range
import hashlib
import os
import random
import string
import tempfile
import re
import time
import urllib

from datetime import datetime
from datetime import timedelta

from elodie.compatability import _rename
from elodie.external.pyexiftool import ExifTool
from elodie.dependencies import get_exiftool
from elodie import constants

def checksum(file_path, blocksize=65536):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read(blocksize)

        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)
        return hasher.hexdigest()
    return None

def create_working_folder(format=None):
    temporary_folder = tempfile.gettempdir()
    folder = os.path.join(temporary_folder, random_string(10, format), random_string(10, format))
    os.makedirs(folder)

    return (temporary_folder, folder)

def download_file(name, destination):
    try:
        url_to_file = 'https://s3.amazonaws.com/jmathai/github/elodie/{}'.format(name)
        # urlretrieve works differently for python 2 and 3
        if constants.python_version < 3:
            final_name = '{}/{}{}'.format(destination, random_string(10), os.path.splitext(name)[1])
            urllib.urlretrieve(
                url_to_file,
                final_name
            )
        else:
            final_name, headers = urllib.request.urlretrieve(url_to_file)
        return final_name
    except Exception as e:
        return False
    
def get_file(name):
    file_path = get_file_path(name)
    if not os.path.isfile(file_path):
        return False

    return file_path

def get_file_path(name):
    current_folder = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_folder, 'files', name)

def get_test_location():
    return (61.013710, 99.196656, 'Siberia')

def populate_folder(number_of_files, include_invalid=False):
    folder = '%s/%s' % (tempfile.gettempdir(), random_string(10))
    os.makedirs(folder)

    for x in range(0, number_of_files):
        ext = 'jpg' if x % 2 == 0 else 'txt'
        fname = '%s/%s.%s' % (folder, x, ext)
        with open(fname, 'a'):
            os.utime(fname, None)

    if include_invalid:
        fname = '%s/%s' % (folder, 'invalid.invalid')
        with open(fname, 'a'):
            os.utime(fname, None)

    return folder

def random_string(length, format=None):
    format_choice = string.ascii_uppercase + string.digits
    if format == 'int':
        format_choice = string.digits
    elif format == 'str':
        format_choice = string.asci_uppercase

    return ''.join(random.SystemRandom().choice(format_choice) for _ in range(length))

def random_decimal():
    return random.random()

def random_coordinate(coordinate, precision):
    # Here we add to the decimal section of the coordinate by a given precision
    return coordinate + (((10.0 / (10.0**precision))) * random_decimal())

def temp_dir():
    return tempfile.gettempdir()

def is_windows():
    return os.name == 'nt'

# path_tz_fix(file_name)
# Change timestamp in file_name by the offset
# between UTC and local time, i.e.
#  2015-12-05_00-59-26-with-title-some-title.jpg ->
#  2015-12-04_20-59-26-with-title-some-title.jpg
# (Windows only)

def path_tz_fix(file_name):
  if is_windows():
      # Calculate the offset between UTC and local time
      tz_shift = (datetime.fromtimestamp(0) -
                  datetime.utcfromtimestamp(0)).seconds / 3600
      # replace timestamp in file_name
      m = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})',file_name)
      t_date = datetime.fromtimestamp(time.mktime(time.strptime(m.group(0), '%Y-%m-%d_%H-%M-%S')))
      s_date_fix = (t_date-timedelta(hours=tz_shift)).strftime('%Y-%m-%d_%H-%M-%S')
      return re.sub(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}',s_date_fix,file_name)
  else:
      return file_name

# time_convert(s_time)
# Change s_time (struct_time) by the offset
# between UTC and local time
# (Windows only)

def time_convert(s_time):
    if is_windows():
        return time.gmtime((time.mktime(s_time)))
    else:
        return s_time


# isclose(a,b,rel_tol)
# To compare float coordinates a and b
# with relative tolerance, default 13-4 which is ≈30ft depending on location
def isclose(a, b, rel_tol = 1e-4):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return False

    diff = abs(a - b)
    return (diff <= abs(rel_tol * a) and
            diff <= abs(rel_tol * b))

def reset_dbs():
    """ Back up hash_db and location_db """
    # This is no longer needed. See gh-322
    # https://github.com/jmathai/elodie/issues/322
    pass

def restore_dbs():
    """ Restore back ups of hash_db and location_db """
    # This is no longer needed. See gh-322
    # https://github.com/jmathai/elodie/issues/322
    pass


def setup_module():
    exiftool_addedargs = [
            u'-config',
            u'"{}"'.format(constants.exiftool_config)
        ]
    ExifTool(executable_=get_exiftool(), addedargs=exiftool_addedargs).start()

def teardown_module():
    ExifTool().terminate
