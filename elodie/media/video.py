"""
The video module contains the :class:`Video` class, which represents video
objects (AVI, MOV, etc.).

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

# load modules
from datetime import datetime

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

        exif = self.get_exiftool_attributes()
        for date_key in self.exif_map['date_taken']:
            if date_key in exif:
                # Example date strings we want to parse
                # 2015:01:19 12:45:11-08:00
                # 2013:09:30 07:06:05
                date = re.search('([0-9: ]+)([-+][0-9:]+)?', exif[date_key])
                if(date is not None):
                    date_string = date.group(1)
                    date_offset = date.group(2)
                    try:
                        exif_seconds_since_epoch = time.mktime(
                            datetime.strptime(
                                date_string,
                                '%Y:%m:%d %H:%M:%S'
                            ).timetuple()
                        )
                        if(exif_seconds_since_epoch < seconds_since_epoch):
                            seconds_since_epoch = exif_seconds_since_epoch
                            if date_offset is not None:
                                offset_parts = date_offset[1:].split(':')
                                offset_seconds = int(offset_parts[0]) * 3600
                                offset_seconds = offset_seconds + int(offset_parts[1]) * 60  # noqa
                                if date_offset[0] == '-':
                                    seconds_since_epoch - offset_seconds
                                elif date_offset[0] == '+':
                                    seconds_since_epoch + offset_seconds
                    except:
                        pass

        if(seconds_since_epoch == 0):
            return None

        return time.gmtime(seconds_since_epoch)
