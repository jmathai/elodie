"""
The media module provides a base :class:`Media` class for media objects that
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
from elodie.media.base import Base

import os
import pyexiv2
import re
import subprocess


class Media(Base):

    """The base class for all media objects.

    :param str source: The fully qualified path to the video file.
    """

    __name__ = 'Media'

    d_coordinates = {
        'latitude': 'latitude_ref',
        'longitude': 'longitude_ref'
    }

    def __init__(self, source=None):
        super(Media, self).__init__(source)
        self.exif_map = {
            'date_taken': ['Exif.Photo.DateTimeOriginal', 'Exif.Image.DateTime', 'Exif.Photo.DateTimeDigitized'],  # , 'EXIF FileDateTime'],  # noqa
            'latitude': 'Exif.GPSInfo.GPSLatitude',
            'latitude_ref': 'Exif.GPSInfo.GPSLatitudeRef',
            'longitude': 'Exif.GPSInfo.GPSLongitude',
            'longitude_ref': 'Exif.GPSInfo.GPSLongitudeRef',
        }

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

    def reset_cache(self):
        """Resets any internal cache
        """
        self.exiftool_attributes = None
        super(Media, self).reset_cache()

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
        self.reset_cache()
        return True
