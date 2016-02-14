"""
General file system methods.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""

import os
import re
import shutil
import time

from elodie import geolocation
from elodie import constants
from elodie.localstorage import Db


class FileSystem(object):

    """A class for interacting with the file system."""

    def create_directory(self, directory_path):
        """Create a directory if it does not already exist.

        :param str directory_name: A fully qualified path of the
            to create.
        :returns: bool
        """
        try:
            if os.path.exists(directory_path):
                return True
            else:
                os.makedirs(directory_path)
                return True
        except OSError:
            # OSError is thrown for cases like no permission
            pass

        return False

    def delete_directory_if_empty(self, directory_path):
        """Delete a directory only if it's empty.

        Instead of checking first using `len([name for name in
        os.listdir(directory_path)]) == 0`, we catch the OSError exception.

        :param str directory_name: A fully qualified path of the directory
            to delete.
        """
        try:
            os.rmdir(directory_path)
            return True
        except OSError:
            pass

        return False

    def get_all_files(self, path, extensions=None):
        """Recursively get all files which match a path and extension.

        :param str path string: Path to start recursive file listing
        :param tuple(str) extensions: File extensions to include (whitelist)
        """
        files = []
        for dirname, dirnames, filenames in os.walk(path):
            # print path to all filenames.
            for filename in filenames:
                if(
                    extensions is None or
                    filename.lower().endswith(extensions)
                ):
                    files.append(os.path.join(dirname, filename))
        return files

    def get_current_directory(self):
        """Get the current working directory.

        :returns: str
        """
        return os.getcwd()

    def get_file_name(self, media):
        """Generate file name for a photo or video using its metadata.

        We use an ISO8601-like format for the file name prefix. Instead of
        colons as the separator for hours, minutes and seconds we use a hyphen.
        https://en.wikipedia.org/wiki/ISO_8601#General_principles

        :param media: A Photo or Video instance
        :type media: :class:`~elodie.media.photo.Photo` or
            :class:`~elodie.media.video.Video`
        :returns: str or None for non-photo or non-videos
        """
        if(not media.is_valid()):
            return None

        metadata = media.get_metadata()
        if(metadata is None):
            return None

        # If the file has EXIF title we use that in the file name
        #   (i.e. my-favorite-photo-img_1234.jpg)
        # We want to remove the date prefix we add to the name.
        # This helps when re-running the program on file which were already
        #   processed.
        base_name = re.sub(
            '^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-',
            '',
            metadata['base_name']
        )
        if(len(base_name) == 0):
            base_name = metadata['base_name']

        if(
            'title' in metadata and
            metadata['title'] is not None and
            len(metadata['title']) > 0
        ):
            title_sanitized = re.sub('\W+', '-', metadata['title'].strip())
            base_name = base_name.replace('-%s' % title_sanitized, '')
            base_name = '%s-%s' % (base_name, title_sanitized)

        file_name = '%s-%s.%s' % (
            time.strftime(
                '%Y-%m-%d_%H-%M-%S',
                metadata['date_taken']
            ),
            base_name,
            metadata['extension'])
        return file_name.lower()

    def get_folder_name_by_date(self, time_obj):
        """Get date based folder name.

        :param time time_obj: Time object to be used to determine folder name.
        :returns: str
        """
        return time.strftime('%Y-%m-%b', time_obj)

    def get_folder_path(self, metadata):
        """Get folder path by various parameters.

        :param time time_obj: Time object to be used to determine folder name.
        :returns: str
        """
        path = []
        if(metadata['date_taken'] is not None):
            path.append(time.strftime('%Y-%m-%b', metadata['date_taken']))

        if(metadata['album'] is not None):
            path.append(metadata['album'])
        elif(
            metadata['latitude'] is not None and
            metadata['longitude'] is not None
        ):
            place_name = geolocation.place_name(
                metadata['latitude'],
                metadata['longitude']
            )
            if(place_name is not None):
                path.append(place_name)

        # if we don't have a 2nd level directory we use 'Unknown Location'
        if(len(path) < 2):
            path.append('Unknown Location')

        # return '/'.join(path[::-1])
        return os.path.join(*path)

    def process_file(self, _file, destination, media, **kwargs):
        move = False
        if('move' in kwargs):
            move = kwargs['move']

        allow_duplicate = False
        if('allowDuplicate' in kwargs):
            allow_duplicate = kwargs['allowDuplicate']

        if(not media.is_valid()):
            print '%s is not a valid media file. Skipping...' % _file
            return

        metadata = media.get_metadata()

        directory_name = self.get_folder_path(metadata)

        dest_directory = os.path.join(destination, directory_name)
        file_name = self.get_file_name(media)
        dest_path = os.path.join(dest_directory, file_name)

        db = Db()
        checksum = db.checksum(_file)
        if(checksum is None):
            if(constants.debug is True):
                print 'Could not get checksum for %s. Skipping...' % _file
            return

        # If duplicates are not allowed and this hash exists in the db then we
        #   return
        if(allow_duplicate is False and db.check_hash(checksum) is True):
            if(constants.debug is True):
                print '%s already exists at %s. Skipping...' % (
                    _file,
                    db.get_hash(checksum)
                )
            return

        self.create_directory(dest_directory)

        if(move is True):
            stat = os.stat(_file)
            shutil.move(_file, dest_path)
            os.utime(dest_path, (stat.st_atime, stat.st_mtime))
        else:
            shutil.copy2(_file, dest_path)

        db.add_hash(checksum, dest_path)
        db.update_hash_db()

        return dest_path

    def set_date_from_path_video(self, video):
        """Set the modification time on the file based on the file path.

        Noop if the path doesn't match the format YYYY-MM/DD-IMG_0001.JPG.

        :param elodie.media.video.Video video: An instance of Video.
        """
        date_taken = None

        video_file_path = video.get_file_path()

        # Initialize date taken to what's returned from the metadata function.
        # If the folder and file name follow a time format of
        #   YYYY-MM/DD-IMG_0001.JPG then we override the date_taken
        (year, month, day) = [None] * 3
        directory = os.path.dirname(video_file_path)
        # If the directory matches we get back a match with
        #   groups() = (year, month)
        year_month_match = re.search('(\d{4})-(\d{2})', directory)
        if(year_month_match is not None):
            (year, month) = year_month_match.groups()
        day_match = re.search(
            '^(\d{2})',
            os.path.basename(video.get_file_path())
        )
        if(day_match is not None):
            day = day_match.group(1)

        # check if the file system path indicated a date and if so we
        #   override the metadata value
        if(year is not None and month is not None):
            if(day is not None):
                date_taken = time.strptime(
                    '{}-{}-{}'.format(year, month, day),
                    '%Y-%m-%d'
                )
            else:
                date_taken = time.strptime(
                    '{}-{}'.format(year, month),
                    '%Y-%m'
                )

            os.utime(video_file_path, (time.time(), time.mktime(date_taken)))
