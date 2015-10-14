"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Video package that handles all video operations
"""
import os
import re
import shutil
import time

from elodie import geolocation
from elodie.localstorage import Db

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
    Delete a directory only if it's empty.
    Instead of checking first using `len([name for name in os.listdir(directory_path)]) == 0` we catch the OSError exception.

    @param, directory_name, string, A fully qualified path of the directory to delete.
    """
    def delete_directory_if_empty(self, directory_path):
        try:
            os.rmdir(directory_path)
        except OSError:
            pass

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
    def get_folder_path(self, metadata):
        path = []
        if(metadata['date_taken'] is not None):
            path.append(time.strftime('%Y-%m-%b', metadata['date_taken']))

        if(metadata['album'] is not None):
            path.append(metadata['album'])
        elif(metadata['latitude'] is not None and metadata['longitude'] is not None):
            place_name = geolocation.place_name(metadata['latitude'], metadata['longitude'])
            if(place_name is None):
                path.append('Unknown Location')
            else:
                path.append(place_name)

        return '/'.join(path)

    def process_file(self, _file, destination, media, **kwargs):
        move = False
        if('move' in kwargs):
            move = kwargs['move']

        allowDuplicate = False
        if('allowDuplicate' in kwargs):
            allowDuplicate = kwargs['allowDuplicate']

        metadata = media.get_metadata()

        directory_name = self.get_folder_path(metadata)

        dest_directory = '%s/%s' % (destination, directory_name)
        file_name = self.get_file_name(media)
        dest_path = '%s/%s' % (dest_directory, file_name)

        db = Db()
        checksum = db.checksum(_file)
        if(checksum == None):
            print 'Could not get checksum for %s. Skipping...' % _file
            return

        # If duplicates are not allowed and this hash exists in the db then we return
        if(allowDuplicate == False and db.check_hash(checksum) == True):
            print '%s already exists at %s. Skipping...' % (_file, db.get_hash(checksum))
            return

        self.create_directory(dest_directory)

        if(move == True):
            shutil.move(_file, dest_path)
        else:
            shutil.copy2(_file, dest_path)

        db.add_hash(checksum, dest_path)
        db.update_hash_db()

        return dest_path

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
