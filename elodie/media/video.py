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


"""
Video class for general video operations
"""
class Video(object):
    # class / static variable accessible through get_valid_extensions()
    __valid_extensions = ('avi','m4v','mov','mp4')

    """
    @param, source, string, The fully qualified path to the video file
    """
    def __init__(self, source=None):
        self.source = source

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
            "date_taken": self.__get_date_taken(),
            "length": self.__get_duration(),
            "mime_type": self.__get_mimetype(),
            "base_name": os.path.splitext(os.path.basename(source))[0],
            "extension": self.__get_extension()
        }

        return metadata

    """
    Check the file extension against valid file extensions as returned by get_valid_extensions()
    
    @returns, boolean
    """
    def is_valid(self):
        source = self.source
        # we can't use self.__get_extension else we'll endlessly recurse
        return os.path.splitext(source)[1][1:].lower() in self.get_valid_extensions()

    """
    Get the date which the video was taken.
    The date value returned is defined by the min() of mtime and ctime.

    @returns, time object or None for non-video files or 0 timestamp
    """
    def __get_date_taken(self):
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
    def __get_duration(self):
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
    Get the file extension as a lowercased string.

    @returns, string or None for a non-video
    """
    def __get_extension(self):
        if(not self.is_valid()):
            return None

        source = self.source
        return os.path.splitext(source)[1][1:].lower()
    
    """
    Get the mimetype of the video.

    @returns, string or None for a non-video
    """
    def __get_mimetype(self):
        if(not self.is_valid()):
            return None

        source = self.source
        mimetype = mimetypes.guess_type(source)
        if(mimetype == None):
            return None

        return mimetype[0]

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
