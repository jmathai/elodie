"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Video package that handles all video operations
"""

# load modules
from distutils.spawn import find_executable
from sys import argv
from datetime import datetime

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
    Get latitude or longitude of photo from EXIF

    @returns, time object or None for non-video files or 0 timestamp
    """
    def get_coordinate(self, type='latitude'):
        exif_data = self.get_exif()
        if(exif_data is None):
            return None

        coords = re.findall('(GPS %s +: .+)' % type.capitalize(), exif_data)
        if(coords is None or len(coords) == 0):
            return None

        coord_string = coords[0]
        coordinate = re.findall('([0-9.]+)', coord_string)
        direction = re.search('[NSEW]$', coord_string)
        if(coordinate is None or direction is None):
            return None

        direction = direction.group(0)

        decimal_degrees = float(coordinate[0]) + float(coordinate[1])/60 + float(coordinate[2])/3600
        if(direction == 'S' or direction == 'W'):
            decimal_degrees = decimal_degrees * -1

        return decimal_degrees

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
        # We need to parse a string from EXIF into a timestamp.
        # we use date.strptime -> .timetuple -> time.mktime to do the conversion in the local timezone
        exif_data = self.get_exif()
        date = re.search('Media Create Date +: +(.+)', exif_data)
        if(date is not None):
            date_string = date.group(1)
            try:
                seconds_since_epoch = time.mktime(datetime.strptime(date_string, '%Y:%m:%d %H:%M:%S').timetuple())
            except:
                pass

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
    Get exif data from video file.
    Not all video files have exif and this currently relies on the CLI exiftool program

    @returns, string or None if exiftool is not found
    """
    def get_exif(self):
        exiftool = find_executable('exiftool')
        if(exiftool is None):
            return None

        source = self.source
        process_output = subprocess.Popen(['%s %s ' % (exiftool, source)], stdout=subprocess.PIPE, shell=True)
        return process_output.stdout.read()

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
            "latitude": self.get_coordinate('latitude'),
            "longitude": self.get_coordinate('longitude'),
            "length": self.get_duration(),
            "mime_type": self.get_mimetype(),
            "base_name": os.path.splitext(os.path.basename(source))[0],
            "extension": self.get_extension()
        }

        return metadata

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
