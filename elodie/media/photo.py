"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Photo package that handles all photo operations
"""

# load modules
from sys import argv
from datetime import datetime

import exifread
from fractions import Fraction
import LatLon
import mimetypes
import os
import re
import time

from elodie.media.media import Media

"""
Video class for general photo operations
"""
class Photo(Media):
    # class / static variable accessible through get_valid_extensions()
    __valid_extensions = ('jpg', 'jpeg')

    """
    @param, source, string, The fully qualified path to the photo file
    """
    def __init__(self, source=None):
        super(Photo, self).__init__(source)

        # We only want to parse EXIF once so we store it here
        self.exif = None

    """
    Get the date which the photo was taken.
    The date value returned is defined by the min() of mtime and ctime.

    @returns, time object or None for non-photo files or 0 timestamp
    """
    def get_date_taken(self):
        if(not self.is_valid()):
            return None

        source = self.source
        seconds_since_epoch = min(os.path.getmtime(source), os.path.getctime(source))
        # We need to parse a string from EXIF into a timestamp.
        # EXIF DateTimeOriginal and EXIF DateTime are both stored in %Y:%m:%d %H:%M:%S format
        # we use date.strptime -> .timetuple -> time.mktime to do the conversion in the local timezone
        # EXIF DateTime is already stored as a timestamp
        # Sourced from https://github.com/photo/frontend/blob/master/src/libraries/models/Photo.php#L500
        exif = self.get_exif()
        try:
            if('EXIF DateTimeOriginal' in exif):
                seconds_since_epoch = time.mktime(datetime.strptime(str(exif['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S').timetuple())
            elif('EXIF DateTime' in exif):
                seconds_since_epoch = time.mktime(datetime.strptime(str(exif['EXIF DateTime']), '%Y:%m:%d %H:%M:%S').timetuple())
            elif('EXIF FileDateTime' in exif):
                seconds_since_epoch = str(exif['EXIF DateTime'])
        except:
            pass

        if(seconds_since_epoch == 0):
            return None

        return time.gmtime(seconds_since_epoch)
        
    """
    Get the duration of a photo in seconds.
    Uses ffmpeg/ffprobe

    @returns, string or None for a non-photo file
    """
    def get_duration(self):
        if(not self.is_valid()):
            return None

        source = self.source
        result = subprocess.Popen(['ffprobe', source],
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        for key in result.stdout.readlines():
            if 'Duration' in key:
                return re.search('(\d{2}:\d{2}.\d{2})', key).group(1).replace('.', ':')
        return None

    """
    Read EXIF from a photo file.
    We store the result in a member variable so we can call get_exif() often without performance degredation

    @returns, list or none for a non-photo file
    """
    def get_exif(self):
        if(not self.is_valid()):
            return None
        
        if(self.exif is not None):
            return self.exif

        source = self.source
        with open(source, 'r') as f:
            self.exif = exifread.process_file(f, details=False)

        return self.exif

    """
    Get latitude or longitude of photo from EXIF

    @returns, float or None if not present in EXIF or a non-photo file
    """
    def get_coordinate(self, type='latitude'):
        if(not self.is_valid()):
            return None

        key = 'GPS GPSLongitude' if type == 'longitude' else 'GPS GPSLatitude'
        exif = self.get_exif()

        if(key not in exif):
            return None

        # this is a hack to get the proper direction by negating the values for S and W
        latdir = 1
        if(key == 'GPS GPSLatitude' and str(exif['GPS GPSLatitudeRef']) == 'S'):
            latdir = -1
        londir = 1
        if(key == 'GPS GPSLongitude' and str(exif['GPS GPSLongitudeRef']) == 'W'):
            londir = -1

        coords = [float(Fraction(ratio.num, ratio.den)) for ratio in exif[key].values]
        if(key == 'latitude'):
            return float(str(LatLon.Latitude(degree=coords[0], minute=coords[1], second=coords[2]))) * latdir
        else:
            return float(str(LatLon.Longitude(degree=coords[0], minute=coords[1], second=coords[2]))) * londir

    """
    Get a dictionary of metadata for a photo.
    All keys will be present and have a value of None if not obtained.

    @returns, dictionary or None for non-photo files
    """
    def get_metadata(self):
        if(not self.is_valid()):
            return None

        source = self.source

        metadata = {
            "date_taken": self.get_date_taken(),
            "latitude": self.get_coordinate('latitude'),
            "longitude": self.get_coordinate('longitude'),
            "mime_type": self.get_mimetype(),
            "base_name": os.path.splitext(os.path.basename(source))[0],
            "extension": self.get_extension()
        }

        return metadata

    """
    Static method to access static __valid_extensions variable.

    @returns, tuple
    """
    @classmethod
    def get_valid_extensions(Photo):
        return Photo.__valid_extensions
