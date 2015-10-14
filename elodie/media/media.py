"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Media package that handles all video operations
"""

# load modules
from sys import argv
from fractions import Fraction
import LatLon
import mimetypes
import os
import pyexiv2
import re
import subprocess
import time

"""
Media class for general video operations
"""
class Media(object):
    """
    @param, source, string, The fully qualified path to the video file
    """
    def __init__(self, source=None):
        self.source = source
        self.exif_map = {
            'date_taken': ['Exif.Photo.DateTimeOriginal', 'Exif.Image.DateTime'], #, 'EXIF FileDateTime'],
            'latitude': 'Exif.GPSInfo.GPSLatitude',
            'latitude_ref': 'Exif.GPSInfo.GPSLatitudeRef',
            'longitude': 'Exif.GPSInfo.GPSLongitude',
            'longitude_ref': 'Exif.GPSInfo.GPSLongitudeRef',
            'album': 'Xmp.elodie.album'
        }
        try:
            pyexiv2.xmp.register_namespace('https://github.com/jmathai/elodie/', 'elodie')
        except KeyError:
            pass

    def get_album(self):
        if(not self.is_valid()):
            return None

        exif = self.get_exif()
        try:
            return exif[self.exif_map['album']].value
        except KeyError:
            return None

    """
    Get the full path to the video.

    @returns string
    """
    def get_file_path(self):
        return self.source

    """
    Check the file extension against valid file extensions as returned by get_valid_extensions()
    
    @returns, boolean
    """
    def is_valid(self):
        source = self.source
        # we can't use self.__get_extension else we'll endlessly recurse
        return os.path.splitext(source)[1][1:].lower() in self.get_valid_extensions()

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
            if(key == self.exif_map['latitude'] and str(exif[self.exif_map['latitude_ref']].value) == 'S'):
                latdir = -1
            londir = 1
            if(key == self.exif_map['longitude'] and str(exif[self.exif_map['longitude_ref']].value) == 'W'):
                londir = -1

            coords = exif[key].value
            if(key == 'latitude'):
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
                    seconds_since_epoch = time.mktime(datetime.strptime(str(exif[key].value), '%Y:%m:%d %H:%M:%S').timetuple())
                    break;
            except:
                pass

        if(seconds_since_epoch == 0):
            return None

        return time.gmtime(seconds_since_epoch)

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
        self.exif = pyexiv2.ImageMetadata(source)
        self.exif.read()

        return self.exif

    """
    Get the file extension as a lowercased string.

    @returns, string or None for a non-video
    """
    def get_extension(self):
        if(not self.is_valid()):
            return None

        source = self.source
        return os.path.splitext(source)[1][1:].lower()

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
            'date_taken': self.get_date_taken(),
            'latitude': self.get_coordinate('latitude'),
            'longitude': self.get_coordinate('longitude'),
            'album': self.get_album(),
            'mime_type': self.get_mimetype(),
            'base_name': os.path.splitext(os.path.basename(source))[0],
            'extension': self.get_extension()
        }

        return metadata
    
    """
    Get the mimetype of the file.

    @returns, string or None for a non-video
    """
    def get_mimetype(self):
        if(not self.is_valid()):
            return None

        source = self.source
        mimetype = mimetypes.guess_type(source)
        if(mimetype == None):
            return None

        return mimetype[0]

    def get_class_by_file(Media, _file):
        extension = os.path.splitext(_file)[1][1:].lower()
        if(extension in Photo.get_valid_extensions()):
            return Photo
        elif(extension in Video.get_valid_extensions()):
            return Video
        else:
            return None

