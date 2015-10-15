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
