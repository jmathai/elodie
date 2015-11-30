"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Media package that handles all video operations
"""

# load modules
from datetime import datetime
from distutils.spawn import find_executable
from elodie import constants
from fractions import Fraction
from sys import argv

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
    # class / static variable accessible through get_valid_extensions()
    video_extensions = ('avi','m4v','mov','mp4','3gp')
    photo_extensions = ('jpg', 'jpeg', 'nef', 'dng', 'gif')

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
        }
        self.exiftool_attributes = None
        self.metadata = None

    """
    Get album from EXIF

    @returns, None or string
    """
    def get_album(self):
        if(not self.is_valid()):
            return None

        exiftool_attributes = self.get_exiftool_attributes()
        if(exiftool_attributes is None or 'album' not in exiftool_attributes):
            return None
        
        return exiftool_attributes['album']

    """
    Get path to executable exiftool binary.
    We wrap this since we call it in a few places and we do a fallback.

    @returns, None or string
    """
    def get_exiftool(self):
        exiftool = find_executable('exiftool')
        # If exiftool wasn't found we try to brute force the homebrew location
        if(exiftool is None):
            exiftool = '/usr/local/bin/exiftool'
            if(not os.path.isfile(exiftool) or not os.access(exiftool, os.X_OK)):
                return None

        return exiftool


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

    def get_exiftool_attributes(self):
        if(self.exiftool_attributes is not None):
            return self.exiftool_attributes

        exiftool = self.get_exiftool()
        if(exiftool is None):
            return False

        source = self.source
        process_output = subprocess.Popen(['%s "%s"' % (exiftool, source)], stdout=subprocess.PIPE, shell=True)
        output = process_output.stdout.read()

        # Get album from exiftool output
        album = None
        album_regex = re.search('Album +: +(.+)', output)
        if(album_regex is not None):
            album = album_regex.group(1)

        # Get title from exiftool output
        title = None
        for key in ['Displayname', 'Headline', 'Title', 'ImageDescription']:
            title_regex = re.search('%s +: +(.+)' % key, output)
            if(title_regex is not None):
                title_return = title_regex.group(1).strip()
                if(len(title_return) > 0):
                    title = title_return
                    break;

        self.exiftool_attributes = {
            'album': album,
            'title': title
        }

        return self.exiftool_attributes


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

        if(self.metadata is not None):
            return self.metadata

        source = self.source

        self.metadata = {
            'date_taken': self.get_date_taken(),
            'latitude': self.get_coordinate('latitude'),
            'longitude': self.get_coordinate('longitude'),
            'album': self.get_album(),
            'title': self.get_title(),
            'mime_type': self.get_mimetype(),
            'base_name': os.path.splitext(os.path.basename(source))[0],
            'extension': self.get_extension()
        }

        return self.metadata
    
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
    
    """
    Get the title for a photo of video

    @returns, string or None if no title is set or not a valid media type
    """
    def get_title(self):
        if(not self.is_valid()):
            return None

        exiftool_attributes = self.get_exiftool_attributes()

        if(exiftool_attributes is None or 'title' not in exiftool_attributes):
            return None

        return exiftool_attributes['title']

    """
    Set album for a photo

    @param, name, string, Name of album

    @returns, boolean
    """
    def set_album(self, name):
        if(name is None):
            return False

        exiftool = self.get_exiftool()
        if(exiftool is None):
            return False

        source = self.source
        exiftool_config = constants.exiftool_config
        if(constants.debug == True):
            print '%s -config "%s" -xmp-elodie:Album="%s" "%s"' % (exiftool, exiftool_config, name, source)
        process_output = subprocess.Popen(['%s -config "%s" -xmp-elodie:Album="%s" "%s"' % (exiftool, exiftool_config, name, source)], stdout=subprocess.PIPE, shell=True)
        streamdata = process_output.communicate()[0]
        if(process_output.returncode != 0):
            return False

        exiftool_backup_file = '%s%s' % (source, '_original')
        if(os.path.isfile(exiftool_backup_file) is True):
            os.remove(exiftool_backup_file)
        return True

    """
    Specifically update the basename attribute in the metadata dictionary for this instance.
    This is used for when we update the EXIF title of a media file.
    Since that determines the name of a file if we update the title of a file more than once it appends to the file name.
    I.e. 2015-12-31_00-00-00-my-first-title-my-second-title.jpg

    @param, string, new_basename, New basename of file (with the old title removed
    """
    def set_metadata_basename(self, new_basename):
        self.get_metadata()
        self.metadata['base_name'] = new_basename

    @classmethod
    def get_class_by_file(Media, _file, classes):
        extension = os.path.splitext(_file)[1][1:].lower()
        name = None
        if(extension in Media.photo_extensions):
            name = 'Photo'
        elif(extension in Media.video_extensions):
            name = 'Video'

        for i in classes:
            if(name == i.__name__):
                return i(_file)

        return None
