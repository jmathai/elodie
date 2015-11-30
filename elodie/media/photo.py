"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Photo package that handles all photo operations
"""

# load modules
from datetime import datetime
from sys import argv

import mimetypes
import os
import pyexiv2
import re
import subprocess
import time

from media import Media
from elodie import geolocation

"""
Photo class for general photo operations
"""
class Photo(Media):
    __name__ = 'Photo'

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

        exif_metadata['Exif.GPSInfo.GPSLatitude'] = geolocation.decimal_to_dms(latitude)
        exif_metadata['Exif.GPSInfo.GPSLatitudeRef'] = pyexiv2.ExifTag('Exif.GPSInfo.GPSLatitudeRef', 'N' if latitude >= 0 else 'S')
        exif_metadata['Exif.GPSInfo.GPSLongitude'] = geolocation.decimal_to_dms(longitude)
        exif_metadata['Exif.GPSInfo.GPSLongitudeRef'] = pyexiv2.ExifTag('Exif.GPSInfo.GPSLongitudeRef', 'E' if longitude >= 0 else 'W')

        exif_metadata.write()
        return True

    """
    Set lat/lon for a photo

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
        return Media.photo_extensions
