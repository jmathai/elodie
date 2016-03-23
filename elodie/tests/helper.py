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
    folder = os.path.join(temporary_folder, random_string(10), random_string(10))
    os.makedirs(folder)

    return (temporary_folder, folder)

def download_file(name, destination):
    try:
        final_name = '{}/{}{}'.format(destination, random_string(10), os.path.splitext(name)[1])
        urllib.urlretrieve(
            'https://s3.amazonaws.com/jmathai/github/elodie/{}'.format(name),
            final_name
        )
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
                  datetime.utcfromtimestamp(0)).seconds/3600
      # replace timestamp in file_name
      m = re.search('(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})',file_name)
      t_date = datetime.fromtimestamp(time.mktime(time.strptime(m.group(0), '%Y-%m-%d_%H-%M-%S')))
      s_date_fix = (t_date-timedelta(hours=tz_shift)).strftime('%Y-%m-%d_%H-%M-%S')
      return re.sub('\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}',s_date_fix,file_name)
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
# with relative tolerance c

def isclose(a, b, rel_tol = 1e-8):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return False

    diff = abs(a - b)
    return (diff <= abs(rel_tol * a) and
            diff <= abs(rel_tol * b))
