"""
The media module provides a base :class:`Media` class for all objects that
are tracked by Elodie. The Media class provides some base functionality used
by all the media types, but isn't itself used to represent anything. Its
sub-classes (:class:`~elodie.media.audio.Audio`,
:class:`~elodie.media.photo.Photo`, and :class:`~elodie.media.video.Video`)
are used to represent the actual files.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""

# load modules
from elodie import constants
from elodie.dependencies import get_exiftool

import mimetypes
import os
import pyexiv2
import re
import subprocess


class Media(object):

    """The base class for all media objects.

    :param str source: The fully qualified path to the video file.
    """

    __name__ = 'Media'

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

    def get_album(self):
        """Get album from EXIF

        :returns: None or string
        """
        if(not self.is_valid()):
            return None

        exiftool_attributes = self.get_exiftool_attributes()
        if(exiftool_attributes is None or 'album' not in exiftool_attributes):
            return None

        return exiftool_attributes['album']

    def get_file_path(self):
        """Get the full path to the video.

        :returns: string
        """
        return self.source

    def is_valid(self):
        """The default is_valid() always returns false.

        This should be overridden in a child class to return true if the
        source is valid, and false otherwise.

        :returns: bool
        """
        return False

    def get_exif(self):
        """Read EXIF from a photo file.

        We store the result in a member variable so we can call get_exif()
        often without performance degredation.

        :returns: list or none for a non-photo file
        """
        if(not self.is_valid()):
            return None

        if(self.exif is not None):
            return self.exif

        source = self.source
        self.exif = pyexiv2.ImageMetadata(source)
        self.exif.read()

        return self.exif

    def get_exiftool_attributes(self):
        """Get attributes for the media object from exiftool.

        :returns: dict, or False if exiftool was not available.
        """
        if(self.exiftool_attributes is not None):
            return self.exiftool_attributes

        exiftool = get_exiftool()
        if(exiftool is None):
            return False

        source = self.source
        process_output = subprocess.Popen(
            '%s "%s"' % (exiftool, source),
            stdout=subprocess.PIPE,
            shell=True,
            universal_newlines=True
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

    def get_extension(self):
        """Get the file extension as a lowercased string.

        :returns: string or None for a non-video
        """
        if(not self.is_valid()):
            return None

        source = self.source
        return os.path.splitext(source)[1][1:].lower()

    def get_metadata(self, update_cache=False):
        """Get a dictionary of metadata for a photo.

        All keys will be present and have a value of None if not obtained.

        :returns: dict or None for non-photo files
        """
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

    def get_mimetype(self):
        """Get the mimetype of the file.

        :returns: str or None for a non-video
        """
        if(not self.is_valid()):
            return None

        source = self.source
        mimetype = mimetypes.guess_type(source)
        if(mimetype is None):
            return None

        return mimetype[0]

    def get_title(self):
        """Get the title for a photo of video

        :returns: str or None if no title is set or not a valid media type
        """
        if(not self.is_valid()):
            return None

        exiftool_attributes = self.get_exiftool_attributes()

        if(exiftool_attributes is None or 'title' not in exiftool_attributes):
            return None

        return exiftool_attributes['title']

    def set_album(self, name):
        """Set album for a photo

        :param str name: Name of album
        :returns: bool
        """
        if(name is None):
            return False

        exiftool = get_exiftool()
        if(exiftool is None):
            return False

        source = self.source
        stat = os.stat(source)
        exiftool_config = constants.exiftool_config
        if(constants.debug is True):
            print '%s -config "%s" -xmp-elodie:Album="%s" "%s"' % (exiftool, exiftool_config, name, source)  # noqa
        process_output = subprocess.Popen(
            '%s -config "%s" -xmp-elodie:Album="%s" "%s"' %
                  (exiftool, exiftool_config, name, source),
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

    def set_metadata_basename(self, new_basename):
        """Update the basename attribute in the metadata dict for this instance.

        This is used for when we update the EXIF title of a media file. Since
        that determines the name of a file if we update the title of a file
        more than once it appends to the file name.

        i.e. 2015-12-31_00-00-00-my-first-title-my-second-title.jpg

        :param str new_basename: New basename of file (with the old title
            removed).
        """
        self.get_metadata()
        self.metadata['base_name'] = new_basename

    def set_metadata(self, **kwargs):
        """Method to manually update attributes in metadata.

        :params dict kwargs: Named parameters to update.
        """
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

    @classmethod
    def get_valid_extensions(cls):
        """Static method to access static extensions variable.

        :returns: tuple(str)
        """
        return cls.extensions
