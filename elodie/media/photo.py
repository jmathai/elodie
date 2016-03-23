"""
The photo module contains the :class:`Photo` class, which is used to track
image objects (JPG, DNG, etc.).

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""

import imghdr
import os
import pyexiv2
import re
import subprocess
import time

from elodie import constants
from media import Media
from elodie import geolocation


class Photo(Media):

    """A photo object.

    :param str source: The fully qualified path to the photo file
    """

    __name__ = 'Photo'

    #: Valid extensions for photo files.
    extensions = ('nef', 'dng', 'gif', 'jpg', 'jpeg')

    def __init__(self, source=None):
        super(Photo, self).__init__(source)

        # We only want to parse EXIF once so we store it here
        self.exif = None

    def get_duration(self):
        """Get the duration of a photo in seconds. Uses ffmpeg/ffprobe.

        :returns: str or None for a non-photo file
        """
        if(not self.is_valid()):
            return None

        source = self.source
        result = subprocess.Popen(
            ['ffprobe', source],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for key in result.stdout.readlines():
            if 'Duration' in key:
                return re.search(
                    '(\d{2}:\d{2}.\d{2})',
                    key
                ).group(1).replace('.', ':')
        return None

    def get_coordinate(self, type='latitude'):
        """Get latitude or longitude of photo from EXIF

        :param str type: Type of coordinate to get. Either "latitude" or
            "longitude".
        :returns: float or None if not present in EXIF or a non-photo file
        """
        if(not self.is_valid()):
            return None

        key = self.exif_map[type]
        exif = self.get_exif()

        if(key not in exif):
            return None

        try:
            # this is a hack to get the proper direction by negating the
            #   values for S and W
            coords = exif[key].value
            return geolocation.dms_to_decimal(
                *coords,
                direction=exif[self.exif_map[self.d_coordinates[type]]].value
            )

        except KeyError:
            return None

    def get_date_taken(self):
        """Get the date which the photo was taken.

        The date value returned is defined by the min() of mtime and ctime.

        :returns: time object or None for non-photo files or 0 timestamp
        """
        if(not self.is_valid()):
            return None

        source = self.source
        seconds_since_epoch = min(os.path.getmtime(source), os.path.getctime(source))  # noqa
        # We need to parse a string from EXIF into a timestamp.
        # EXIF DateTimeOriginal and EXIF DateTime are both stored
        #   in %Y:%m:%d %H:%M:%S format
        # we use date.strptime -> .timetuple -> time.mktime to do
        #   the conversion in the local timezone
        # EXIF DateTime is already stored as a timestamp
        # Sourced from https://github.com/photo/frontend/blob/master/src/libraries/models/Photo.php#L500  # noqa
        exif = self.get_exif()
        for key in self.exif_map['date_taken']:
            try:
                if(key in exif):
                    if(re.match('\d{4}(-|:)\d{2}(-|:)\d{2}', str(exif[key].value)) is not None):  # noqa
                        seconds_since_epoch = time.mktime(exif[key].value.timetuple())  # noqa
                        break
            except BaseException as e:
                if(constants.debug is True):
                    print e
                pass

        if(seconds_since_epoch == 0):
            return None

        return time.gmtime(seconds_since_epoch)

    def is_valid(self):
        """Check the file extension against valid file extensions.

        The list of valid file extensions come from self.extensions. This
        also checks whether the file is an image.

        :returns: bool
        """
        source = self.source

        # gh-4 This checks if the source file is an image.
        # It doesn't validate against the list of supported types.
        if(imghdr.what(source) is None):
            return False

        return os.path.splitext(source)[1][1:].lower() in self.extensions

    def set_date_taken(self, time):
        """Set the date/time a photo was taken.

        :param datetime time: datetime object of when the photo was taken
        :returns: bool
        """
        if(time is None):
            return False

        source = self.source
        exif_metadata = pyexiv2.ImageMetadata(source)
        exif_metadata.read()

        # Writing exif with pyexiv2 differs if the key already exists so we
        #   handle both cases here.
        for key in self.exif_map['date_taken']:
            if(key in exif_metadata):
                exif_metadata[key].value = time
            else:
                exif_metadata[key] = pyexiv2.ExifTag(key, time)

        exif_metadata.write()
        self.reset_cache()
        return True

    def set_location(self, latitude, longitude):
        """Set latitude and longitude for a photo.

        :param float latitude: Latitude of the file
        :param float longitude: Longitude of the file
        :returns: bool
        """
        if(latitude is None or longitude is None):
            return False

        source = self.source
        exif_metadata = pyexiv2.ImageMetadata(source)
        exif_metadata.read()

        exif_metadata['Exif.GPSInfo.GPSLatitude'] = geolocation.decimal_to_dms(latitude, False)  # noqa
        exif_metadata['Exif.GPSInfo.GPSLatitudeRef'] = pyexiv2.ExifTag('Exif.GPSInfo.GPSLatitudeRef', 'N' if latitude >= 0 else 'S')  # noqa
        exif_metadata['Exif.GPSInfo.GPSLongitude'] = geolocation.decimal_to_dms(longitude, False)  # noqa
        exif_metadata['Exif.GPSInfo.GPSLongitudeRef'] = pyexiv2.ExifTag('Exif.GPSInfo.GPSLongitudeRef', 'E' if longitude >= 0 else 'W')  # noqa

        exif_metadata.write()
        self.reset_cache()
        return True

    def set_title(self, title):
        """Set title for a photo.

        :param str title: Title of the photo.
        :returns: bool
        """
        if(title is None):
            return False

        source = self.source
        exif_metadata = pyexiv2.ImageMetadata(source)
        exif_metadata.read()

        exif_metadata['Xmp.dc.title'] = title

        exif_metadata.write()
        self.reset_cache()
        return True
