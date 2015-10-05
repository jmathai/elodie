#!/usr/bin/env python

from sys import argv
import mimetypes
import os
import re
import subprocess
import time

"""
Video package that handles all video operations
"""

"""
Video class for general video operations
"""
class Video(object):
    __valid_extensions = ('avi','m4v','mov','mp4')

    # Constructor
    def __init__(self, source=None):
        self.source = source

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

    def is_valid(self):
        source = self.source
        # we can't use self.__get_extension else we'll endlessly recurse
        return os.path.splitext(source)[1][1:].lower() in self.get_valid_extensions()

    #
    # Private methods
    #

    # get the min() of mtime and ctime
    # returns a time object
    def __get_date_taken(self):
        if(not self.is_valid()):
            return None

        source = self.source
        seconds_since_epoch = min(os.path.getmtime(source), os.path.getctime(source))
        if(seconds_since_epoch == 0):
            return None

        return time.gmtime(seconds_since_epoch)
        
    # get the duration of a video in seconds
    # uses ffmpeg
    def __get_duration(self):
        if(not self.is_valid()):
            return None

        source = self.source
        result = subprocess.Popen(['/usr/local/bin/ffprobe', source],
            stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        for key in result.stdout.readlines():
            if 'Duration' in key:
                return re.search('(\d{2}:\d{2}.\d{2})', key).group(1).replace('.', ':')

    # returns file extension
    def __get_extension(self):
        if(not self.is_valid()):
            return None

        source = self.source
        return os.path.splitext(source)[1][1:].lower()
    
    # returns the mime type
    def __get_mimetype(self):
        if(not self.is_valid()):
            return None

        source = self.source
        mimetype = mimetypes.guess_type(source)
        if(mimetype == None):
            return None

        return mimetype[0]

    @classmethod
    def get_valid_extensions(Video):
        return Video.__valid_extensions

class Transcode(object):
    # Constructor takes a video object as it's parameter
    def __init__(self, video=None):
        self.video = video
