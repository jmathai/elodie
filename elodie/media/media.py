"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Media package that handles all video operations
"""

# load modules
from sys import argv
import mimetypes
import os
import re
import subprocess
import time

"""
Media class for general video operations
"""
class Media(object):
    """
    @param, source, string, The fully qualified path to the video file
    """
    def __init__(self, source=None):
        self.source = source

    """
    Get the full path to the video.

    @returns string
    """
    def get_file_path(self):
        return self.source

    """
    Check the file extension against valid file extensions as returned by get_valid_extensions()
    
    @returns, boolean
    """
    def is_valid(self):
        source = self.source
        # we can't use self.__get_extension else we'll endlessly recurse
        return os.path.splitext(source)[1][1:].lower() in self.get_valid_extensions()

    """
    Get the file extension as a lowercased string.

    @returns, string or None for a non-video
    """
    def get_extension(self):
        if(not self.is_valid()):
            return None

        source = self.source
        return os.path.splitext(source)[1][1:].lower()
    
    """
    Get the mimetype of the file.

    @returns, string or None for a non-video
    """
    def get_mimetype(self):
        if(not self.is_valid()):
            return None

        source = self.source
        mimetype = mimetypes.guess_type(source)
        if(mimetype == None):
            return None

        return mimetype[0]
