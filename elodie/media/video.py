"""
The video module contains the :class:`Video` class, which represents video
objects (AVI, MOV, etc.).

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

# load modules
from datetime import datetime, timezone

import os
import re
import time

from .media import Media


class Video(Media):

    """A video object.

    :param str source: The fully qualified path to the video file.
    """

    __name__ = 'Video'

    #: Valid extensions for video files.
    extensions = ('avi', 'm4v', 'mov', 'mp4', 'mpg', 'mpeg', '3gp', 'mts')

    def __init__(self, source=None):
        super(Video, self).__init__(source)
        self.exif_map['date_taken'] = [
            'QuickTime:CreationDate',
            'QuickTime:CreateDate',
            'QuickTime:CreationDate-und-US',
            'QuickTime:MediaCreateDate',
            'H264:DateTimeOriginal'
        ]
        self.title_key = 'XMP:DisplayName'
        self.latitude_keys = [
            'XMP:GPSLatitude',
            # 'QuickTime:GPSLatitude',
            'Composite:GPSLatitude'
        ]
        self.longitude_keys = [
            'XMP:GPSLongitude',
            # 'QuickTime:GPSLongitude',
            'Composite:GPSLongitude'
        ]
        self.latitude_ref_key = 'EXIF:GPSLatitudeRef'
        self.longitude_ref_key = 'EXIF:GPSLongitudeRef'
        self.set_gps_ref = False

    def get_date_taken(self):
        """Get the date which the photo was taken.

        The date value returned is defined by the min() of mtime and ctime.

        :returns: time object or None for non-photo files or 0 timestamp
        """
        if(not self.is_valid()):
            return None

        source = self.source
        seconds_since_epoch = min(os.path.getmtime(source), os.path.getctime(source))  # noqa
        fallback_date = datetime.fromtimestamp(seconds_since_epoch, timezone.utc)
        best_date = fallback_date
        found_exif_date = False

        exif = self.get_exiftool_attributes()
        if not exif:
            if(seconds_since_epoch == 0):
                return None
            return fallback_date.utctimetuple()

        for date_key in self.exif_map['date_taken']:
            if date_key in exif:
                # Example date strings we want to parse
                # 2015:01:19 12:45:11-08:00
                # 2013:09:30 07:06:05
                date = re.search('([0-9: ]+)([-+][0-9:]+)?', exif[date_key])
                if(date is not None):
                    date_string = date.group(1)
                    try:
                        exif_date = datetime.strptime(
                            date_string,
                            '%Y:%m:%d %H:%M:%S'
                        ).replace(tzinfo=timezone.utc)
                        if(exif_date < best_date):
                            best_date = exif_date
                        found_exif_date = True
                    except:
                        pass

        if(seconds_since_epoch == 0 and found_exif_date is False):
            return None

        return best_date.utctimetuple()
