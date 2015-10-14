"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Photo package that handles all photo operations
"""

# load modules
from sys import argv
from datetime import datetime

import mimetypes
import os
import re
import time

from elodie.media.media import Media

"""
Video class for general photo operations
"""
class Photo(Media):
    # class / static variable accessible through get_valid_extensions()
    __valid_extensions = ('jpg', 'jpeg', 'nef', 'dng')

    """
    @param, source, string, The fully qualified path to the photo file
    """
    def __init__(self, source=None):
        super(Photo, self).__init__(source)

        # We only want to parse EXIF once so we store it here
        self.exif = None

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
                    seconds_since_epoch = time.mktime(datetime.strptime(str(exif[key]), '%Y:%m:%d %H:%M:%S').timetuple())
                    break;
            except:
                pass

        if(seconds_since_epoch == 0):
            return None

        return time.gmtime(seconds_since_epoch)
        
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
    Static method to access static __valid_extensions variable.

    @returns, tuple
    """
    @classmethod
    def get_valid_extensions(Photo):
        return Photo.__valid_extensions
