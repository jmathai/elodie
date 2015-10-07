"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Video package that handles all video operations
"""

# load modules
from sys import argv
import mimetypes
import os
import re
import subprocess
import time

from elodie.media.media import Media

"""
Video class for general video operations
"""
class Video(Media):
    # class / static variable accessible through get_valid_extensions()
    __valid_extensions = ('avi','m4v','mov','mp4','3gp')

    """
    @param, source, string, The fully qualified path to the video file
    """
    def __init__(self, source=None):
        super(Video, self).__init__(source)

    """
    Get a dictionary of metadata for a video.
    All keys will be present and have a value of None if not obtained.

    @returns, dictionary or None for non-video files
    """
    def get_metadata(self):
        if(not self.is_valid()):
            return None

        source = self.source
        metadata = {
            "date_taken": self.get_date_taken(),
            "length": self.get_duration(),
            "mime_type": self.get_mimetype(),
            "base_name": os.path.splitext(os.path.basename(source))[0],
            "extension": self.get_extension()
        }

        return metadata

    """
    Get the date which the video was taken.
    The date value returned is defined by the min() of mtime and ctime.

    @returns, time object or None for non-video files or 0 timestamp
    """
    def get_date_taken(self):
        if(not self.is_valid()):
            return None

        source = self.source
        seconds_since_epoch = min(os.path.getmtime(source), os.path.getctime(source))
        if(seconds_since_epoch == 0):
            return None

        return time.gmtime(seconds_since_epoch)
        
    """
    Get the duration of a video in seconds.
    Uses ffmpeg/ffprobe

    @returns, string or None for a non-video file
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
    def get_valid_extensions(Video):
        return Video.__valid_extensions

class Transcode(object):
    # Constructor takes a video object as it's parameter
    def __init__(self, video=None):
        self.video = video
