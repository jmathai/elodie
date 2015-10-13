"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Video package that handles all video operations
"""
import os
import re
import time

from elodie import geolocation

"""
General file system methods
"""
class FileSystem:
    """
    Create a directory if it does not already exist..

    @param, directory_name, string, A fully qualified path of the directory to create.
    """
    def create_directory(self, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    """
    Recursively get all files which match a path and extension.

    @param, path, string, Path to start recursive file listing
    @param, extensions, tuple, File extensions to include (whitelist)
    """
    def get_all_files(self, path, extensions=None):
        files = []
        for dirname, dirnames, filenames in os.walk(path):
            # print path to all filenames.
            for filename in filenames:
                if(extensions == None or filename.lower().endswith(extensions)):
                    files.append('%s/%s' % (dirname, filename))
        return files

    """
    Get the current working directory

    @returns, string
    """
    def get_current_directory(self):
        return os.getcwd()

    """
    Generate file name for a video using its metadata.
    We use an ISO8601-like format for the file name prefix.
    Instead of colons as the separator for hours, minutes and seconds we use a hyphen.
    https://en.wikipedia.org/wiki/ISO_8601#General_principles

    @param, video, Video, A Video instance
    @returns, string or None for non-videos
    """
    def get_file_name(self, video):
        if(not video.is_valid()):
            return None

        metadata = video.get_metadata()
        if(metadata == None):
            return None

        # We want to remove the date prefix we add to the name.
        # This helps when re-running the program on file which were already processed. 
        base_name = re.sub('^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-', '', metadata['base_name'])
        if(len(base_name) == 0):
            base_name = metadata['base_name']

        file_name = '%s-%s.%s' % (time.strftime('%Y-%m-%d_%H-%M-%S', metadata['date_taken']), base_name, metadata['extension'])
        return file_name.lower()

    """
    Get date based folder name.

    @param, time_obj, time, Time object to be used to determine folder name.
    @returns, string
    """
    def get_folder_name_by_date(self, time_obj):
        return time.strftime('%Y-%m-%b', time_obj)

    """
    Get folder path by various parameters.

    @param, time_obj, time, Time object to be used to determine folder name.
    @returns, string
    """
    def get_folder_path(self, **kwargs):
        path = []
        if('date' in kwargs):
            path.append(time.strftime('%Y-%m-%b', kwargs['date']))

        if('latitude' in kwargs and 'longitude' in kwargs):
            place_name = geolocation.place_name(kwargs['latitude'], kwargs['longitude'])
            if(place_name is None):
                path.append('Unknown Location')
            else:
                path.append(place_name)

        return '/'.join(path)

    """
    Set the modification time on the file based on the file path.
    Noop if the path doesn't match the format YYYY-MM/DD-IMG_0001.JPG.
    """
    def set_date_from_path_video(self, video):
        date_taken = None

        video_file_path = video.get_file_path()

        # Initialize date taken to what's returned from the metadata function.
        # If the folder and file name follow a time format of YYYY-MM/DD-IMG_0001.JPG then we override the date_taken
        (year, month, day) = [None] * 3
        directory = os.path.dirname(video_file_path)
        # If the directory matches we get back a match with groups() = (year, month)
        year_month_match = re.search('(\d{4})-(\d{2})', directory)
        if(year_month_match is not None):
            (year, month) = year_month_match.groups()
        day_match = re.search('^(\d{2})', os.path.basename(video.get_file_path()))
        if(day_match is not None):
            day = day_match.group(1)

        # check if the file system path indicated a date and if so we override the metadata value
        if(year is not None and month is not None):
            if(day is not None):
                date_taken = time.strptime('{}-{}-{}'.format(year, month, day), '%Y-%m-%d')
            else:
                date_taken = time.strptime('{}-{}'.format(year, month), '%Y-%m')
            
            os.utime(video_file_path, (time.time(), time.mktime(date_taken)))
