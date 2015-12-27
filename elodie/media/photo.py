"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Photo package that handles all photo operations
"""

# load modules
from datetime import datetime
from sys import argv

import imghdr
import mimetypes
import LatLon
import os
import pyexiv2
import re
import subprocess
import time

from elodie import constants
from media import Media
from elodie import geolocation

"""
Photo class for general photo operations
"""
class Photo(Media):
    __name__ = 'Photo'
    extensions = ('jpg', 'jpeg', 'nef', 'dng', 'gif')

    """
    @param, source, string, The fully qualified path to the photo file
    """
    def __init__(self, source=None):
        super(Photo, self).__init__(source)

        # We only want to parse EXIF once so we store it here
        self.exif = None
        
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
    Get latitude or longitude of photo from EXIF

    @returns, float or None if not present in EXIF or a non-photo file
    """
    def get_coordinate(self, type='latitude'):
        if(not self.is_valid()):
            return None

        key = self.exif_map['longitude'] if type == 'longitude' else self.exif_map['latitude']
        exif = self.get_exif()

        if(key not in exif):
            return None

        try:
            # this is a hack to get the proper direction by negating the values for S and W
            latdir = 1
            if(type == 'latitude' and str(exif[self.exif_map['latitude_ref']].value) == 'S'):
                latdir = -1
            londir = 1
            if(type =='longitude' and str(exif[self.exif_map['longitude_ref']].value) == 'W'):
                londir = -1

            coords = exif[key].value
            if(type == 'latitude'):
                return float(str(LatLon.Latitude(degree=coords[0], minute=coords[1], second=coords[2]))) * latdir
            else:
                return float(str(LatLon.Longitude(degree=coords[0], minute=coords[1], second=coords[2]))) * londir
        except KeyError:
            return None

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
        for key in self.exif_map['date_taken']:
            try:
                if(key in exif):
                    if(re.match('\d{4}(-|:)\d{2}(-|:)\d{2}', str(exif[key].value)) is not None):
                        seconds_since_epoch = time.mktime(exif[key].value.timetuple())
                        break;
            except BaseException as e:
                if(constants.debug == True):
                    print e
                pass

        if(seconds_since_epoch == 0):
            return None

        return time.gmtime(seconds_since_epoch)

    """
    Check the file extension against valid file extensions as returned by self.extensions
    
    @returns, boolean
    """
    def is_valid(self):
        source = self.source

        # gh-4 This checks if the source file is an image.
        # It doesn't validate against the list of supported types.
        if(imghdr.what(source) is None):
            return False;

        return os.path.splitext(source)[1][1:].lower() in self.extensions

    """
    Set the date/time a photo was taken

    @param, time, datetime, datetime object of when the photo was taken

    @returns, boolean
    """
    def set_date_taken(self, time):
        if(time is None):
            return False

        source = self.source
        exif_metadata = pyexiv2.ImageMetadata(source)
        exif_metadata.read()

        exif_metadata['Exif.Photo.DateTimeOriginal'].value = time
        exif_metadata['Exif.Image.DateTime'].value = time

        exif_metadata.write()
        return True

    """
    Set lat/lon for a photo

    @param, latitude, float, Latitude of the file
    @param, longitude, float, Longitude of the file

    @returns, boolean
    """
    def set_location(self, latitude, longitude):
        if(latitude is None or longitude is None):
            return False

        source = self.source
        exif_metadata = pyexiv2.ImageMetadata(source)
        exif_metadata.read()

        exif_metadata['Exif.GPSInfo.GPSLatitude'] = geolocation.decimal_to_dms(latitude, False)
        exif_metadata['Exif.GPSInfo.GPSLatitudeRef'] = pyexiv2.ExifTag('Exif.GPSInfo.GPSLatitudeRef', 'N' if latitude >= 0 else 'S')
        exif_metadata['Exif.GPSInfo.GPSLongitude'] = geolocation.decimal_to_dms(longitude, False)
        exif_metadata['Exif.GPSInfo.GPSLongitudeRef'] = pyexiv2.ExifTag('Exif.GPSInfo.GPSLongitudeRef', 'E' if longitude >= 0 else 'W')

        exif_metadata.write()
        return True

    """
    Set title for a photo

    @param, latitude, float, Latitude of the file
    @param, longitude, float, Longitude of the file

    @returns, boolean
    """
    def set_title(self, title):
        if(title is None):
            return False

        source = self.source
        exif_metadata = pyexiv2.ImageMetadata(source)
        exif_metadata.read()

        exif_metadata['Xmp.dc.title'] = title

        exif_metadata.write()
        return True

    """
    Static method to access static __valid_extensions variable.

    @returns, tuple
    """
    @classmethod
    def get_valid_extensions(Photo):
        return Photo.extensions
