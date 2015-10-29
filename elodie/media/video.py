"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Video package that handles all video operations
"""

# load modules
from distutils.spawn import find_executable
import tempfile
from sys import argv
from datetime import datetime

import mimetypes
import os
import re
import shutil
import subprocess
import time

from elodie import constants
from elodie import plist_parser
from media import Media

"""
Video class for general video operations
"""
class Video(Media):
    # class / static variable accessible through get_valid_extensions()
    

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
        for key in ['Creation Date', 'Media Create Date']:
            date = re.search('%s +: +([0-9: ]+)' % key, exif_data)
            if(date is not None):
                date_string = date.group(1)
                try:
                    seconds_since_epoch = time.mktime(datetime.strptime(date_string, '%Y:%m:%d %H:%M:%S').timetuple())
                    break
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
        process_output = subprocess.Popen(['%s "%s"' % (exiftool, source)], stdout=subprocess.PIPE, shell=True)
        return process_output.stdout.read()

    """
    Set the date/time a photo was taken

    @param, time, datetime, datetime object of when the photo was taken

    @returns, boolean
    """
    def set_datetime(self, time):
        if(time is None):
            return False

        result = self.__update_using_plist(time=time)
        return result

    """
    Set lat/lon for a video

    @param, latitude, float, Latitude of the file
    @param, longitude, float, Longitude of the file

    @returns, boolean
    """
    def set_location(self, latitude, longitude):
        if(latitude is None or longitude is None):
            return False

        result = self.__update_using_plist(latitude=latitude, longitude=longitude)
        return result

    """
    Set title for a video

    @param, title, string, Title for the file

    @returns, boolean
    """

    def set_title(self, title):
        if(title is None):
            return False

        result = self.__update_using_plist(title=title)
        return result

    """
    Updates video metadata using avmetareadwrite.
    This method is a does a lot more than it should.
    The general steps are...
    1) Check if avmetareadwrite is installed
    2) Export a plist file to a temporary location from the source file
    3) Regex replace values in the plist file
    4) Update the source file using the updated plist and save it to a temporary location
    5) Validate that the metadata in the updated temorary movie is valid
    6) Copystat permission and time bits from the source file to the temporary movie
    7) Move the temporary file to overwrite the source file

    @param, latitude, float, Latitude of the file
    @param, longitude, float, Longitude of the file

    @returns, boolean
    """
    def __update_using_plist(self, **kwargs):
        if('latitude' not in kwargs and 'longitude' not in kwargs and 'time' not in kwargs and 'title' not in kwargs):
            if(constants.debug == True):
                print 'No lat/lon passed into __create_plist'
            return False

        avmetareadwrite = find_executable('avmetareadwrite')
        if(avmetareadwrite is None):
            if(constants.debug == True):
                print 'Could not find avmetareadwrite'
            return False

        source = self.source

        # First we need to write the plist for an existing file to a temporary location
        with tempfile.NamedTemporaryFile() as plist_temp:
            # We need to write the plist file in a child process but also block for it to be complete.
            # http://stackoverflow.com/a/5631819/1318758
            avmetareadwrite_generate_plist_command = '%s -p "%s" "%s"' % (avmetareadwrite, plist_temp.name, source)
            write_process = subprocess.Popen([avmetareadwrite_generate_plist_command], stdout=subprocess.PIPE, shell=True)
            streamdata = write_process.communicate()[0]
            if(write_process.returncode != 0):
                if(constants.debug == True):
                    print 'Failed to generate plist file'
                return False

            plist = plist_parser.Plist(plist_temp.name)
            # Depending on the kwargs that were passed in we regex the plist_text before we write it back.
            plist_should_be_written = False
            if('latitude' in kwargs and 'longitude' in kwargs):
                latitude = str(abs(kwargs['latitude'])).lstrip('0')
                longitude = kwargs['longitude']

                # Add a literal '+' to the lat/lon if it is positive.
                # Do this first because we convert longitude to a string below.
                lat_sign = '+' if latitude > 0 else '-'
                # We need to zeropad the longitude.
                # No clue why - ask Apple.
                # We set the sign to + or - and then we take the absolute value and fill it.
                lon_sign = '+' if longitude > 0 else '-'
                longitude_str = '{:9.5f}'.format(abs(longitude)).replace(' ', '0')
                lat_lon_str = '%s%s%s%s' % (lat_sign, latitude, lon_sign, longitude_str)

                plist.update_key('common/location', lat_lon_str)
                plist_should_be_written = True

            if('time' in kwargs):
                # The time formats can be YYYY-mm-dd or YYYY-mm-dd hh:ii:ss
                time_parts = str(kwargs['time']).split(' ')
                ymd, hms = [None, None]
                if(len(time_parts) >= 1):
                    ymd = [int(x) for x in time_parts[0].split('-')]

                    if(len(time_parts) == 2):
                        hms = [int(x) for x in time_parts[1].split(':')]

                    if(hms is not None):
                        d = datetime(ymd[0], ymd[1], ymd[2], hms[0], hms[1], hms[2])
                    else:
                        d = datetime(ymd[0], ymd[1], ymd[2], 12, 00, 00)

                    offset = time.strftime("%z", time.gmtime(time.time()))
                    time_string = d.strftime('%Y-%m-%dT%H:%M:%S{}'.format(offset))
                    #2015-10-09T17:11:30-0700
                    plist.update_key('common/creationDate', time_string)
                    plist_should_be_written = True

            if('title' in kwargs):
                if(len(kwargs['title']) > 0):
                    plist.update_key('common/title', kwargs['title'])
                    plist_should_be_written = True

            if(plist_should_be_written is True):
                plist_final = plist_temp.name
                plist.write_file(plist_final)
            else:
                if(constants.debug == True):
                    print 'Nothing to update, plist unchanged'
                return False

            # We create a temporary file to save the modified file to.
            # If the modification is successful we will update the existing file.
            metadata = self.get_metadata()
            temp_movie = None
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_movie = '%s.%s' % (temp_file.name, metadata['extension'])

            # We need to block until the child process completes.
            # http://stackoverflow.com/a/5631819/1318758
            avmetareadwrite_command = '%s -a %s "%s" "%s"' % (avmetareadwrite, plist_final, source, temp_movie)
            update_process = subprocess.Popen([avmetareadwrite_command], stdout=subprocess.PIPE, shell=True)
            streamdata = update_process.communicate()[0]
            if(update_process.returncode != 0):
                if(constants.debug == True):
                    print '%s did not complete successfully' % avmetareadwrite_command
                return False

            # Before we do anything destructive we confirm that the file is in tact.
            check_media = Video(temp_movie)
            check_metadata = check_media.get_metadata()
            if(check_metadata['latitude'] is None or check_metadata['longitude'] is None or check_metadata['date_taken'] is None):
                if(constants.debug == True):
                    print 'Something went wrong updating video metadata'
                return False

            # Copy file information from original source to temporary file before copying back over
            shutil.copystat(source, temp_movie)
            shutil.move(temp_movie, source)
            return True

    """
    Static method to access static __valid_extensions variable.

    @returns, tuple
    """
    @classmethod
    def get_valid_extensions(Video):
        return Media.video_extensions

class Transcode(object):
    # Constructor takes a video object as it's parameter
    def __init__(self, video=None):
        self.video = video
