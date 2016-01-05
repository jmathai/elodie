"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Media package that's a parent class for media objects
"""

# load modules
from distutils.spawn import find_executable
from elodie import constants

import mimetypes
import os
import pyexiv2
import re
import subprocess


class Media(object):
    # class / static variable accessible through get_valid_extensions()
    __name__ = 'Media'

    """
    @param, source, string, The fully qualified path to the video file
    """
    def __init__(self, source=None):
        self.source = source
        self.exif_map = {
            'date_taken': ['Exif.Photo.DateTimeOriginal', 'Exif.Image.DateTime'],  # , 'EXIF FileDateTime'],  # noqa
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
            if(not os.path.isfile(exiftool) or not os.access(exiftool, os.X_OK)):  # noqa
                return None

        return exiftool

    """
    Get the full path to the video.

    @returns string
    """
    def get_file_path(self):
        return self.source

    """
    Define is_valid to always return false.
    This should be overridden in a child class.
    """
    def is_valid(self):
        return False

    """
    Read EXIF from a photo file.
    We store the result in a member variable so we can call get_exif() often
        without performance degredation

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
        process_output = subprocess.Popen(
            ['%s "%s"' % (exiftool, source)],
            stdout=subprocess.PIPE,
            shell=True
        )
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
                    break

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
    def get_metadata(self, update_cache=False):
        if(not self.is_valid()):
            return None

        if(self.metadata is not None and update_cache is False):
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
            'extension': self.get_extension(),
            'directory_path': os.path.dirname(source)
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
        if(mimetype is None):
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
        stat = os.stat(source)
        exiftool_config = constants.exiftool_config
        if(constants.debug is True):
            print '%s -config "%s" -xmp-elodie:Album="%s" "%s"' % (exiftool, exiftool_config, name, source)  # noqa
        process_output = subprocess.Popen(
            ['%s -config "%s" -xmp-elodie:Album="%s" "%s"' %
                (exiftool, exiftool_config, name, source)],
            stdout=subprocess.PIPE,
            shell=True
        )
        process_output.communicate()

        if(process_output.returncode != 0):
            return False

        os.utime(source, (stat.st_atime, stat.st_mtime))

        exiftool_backup_file = '%s%s' % (source, '_original')
        if(os.path.isfile(exiftool_backup_file) is True):
            os.remove(exiftool_backup_file)

        self.set_metadata(album=name)
        return True

    def set_album_from_folder(self):
        metadata = self.get_metadata()

        print 'huh/'

        # If this file has an album already set we do not overwrite EXIF
        if(metadata['album'] is not None):
            return False

        folder = os.path.basename(metadata['directory_path'])
        # If folder is empty we skip
        if(len(folder) == 0):
            return False

        self.set_album(folder)
        return True

    """
    Specifically update the basename attribute in the metadata
        dictionary for this instance.
    This is used for when we update the EXIF title of a media file.
    Since that determines the name of a file if we update the
        title of a file more than once it appends to the file name.
    I.e. 2015-12-31_00-00-00-my-first-title-my-second-title.jpg

    @param, string, new_basename, New basename of file
        (with the old title removed)
    """
    def set_metadata_basename(self, new_basename):
        self.get_metadata()
        self.metadata['base_name'] = new_basename

    """
    Method to manually update attributes in metadata.

    @params, named paramaters
    """
    def set_metadata(self, **kwargs):
        metadata = self.get_metadata()
        for key in kwargs:
            if(key in metadata):
                self.metadata[key] = kwargs[key]

    @classmethod
    def get_class_by_file(cls, _file, classes):
        extension = os.path.splitext(_file)[1][1:].lower()

        for i in classes:
            if(extension in i.extensions):
                return i(_file)

        return None
