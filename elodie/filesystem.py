"""
General file system methods.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function
from builtins import object

import os
import re
import shutil
import time
import sys

from elodie import geolocation
from elodie import log
from elodie.config import load_config
from elodie.localstorage import Db
from elodie.media.base import Base, get_all_subclasses
from elodie import constants
from elodie import compatability

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
        :returns: generator
        """
        # If extensions is None then we get all supported extensions
        if not extensions:
            extensions = set()
            subclasses = get_all_subclasses(Base)
            for cls in subclasses:
                extensions.update(cls.extensions)

        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:
                # If file extension is in `extensions` then append to the list
                if os.path.splitext(filename)[1][1:].lower() in extensions:
                    yield os.path.join(dirname, filename)

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

    def get_folder_path_definition(self):
        # If we've done this already then return it immediately without
        # incurring any extra work
        if self.cached_folder_path_definition is not None:
            return self.cached_folder_path_definition

        config = load_config()

        # If Directory is in the config we assume full_path and its
        #  corresponding values (date, location) are also present
        if('Directory' not in config):
            return self.default_folder_path_definition

        config_directory = config['Directory']

        path_parts = re.search(
                         '\%([^/]+)\/\%([^/]+)',
                         config_directory['full_path']
                     )

        if not path_parts or len(path_parts.groups()) != 2:
            return self.default_folder_path_definition

        path_part_groups = path_parts.groups()
        self.cached_folder_path_definition = [
            (path_part_groups[0], config_directory[path_part_groups[0]]),
            (path_part_groups[1], config_directory[path_part_groups[1]]),
        ]
        return self.cached_folder_path_definition

    def get_folder_path(self, metadata):
        """Get folder path by various parameters.

        :param metadata dict: Metadata dictionary.
        :returns: str
        """
        path_parts = self.get_folder_path_definition()
        path = []
        for path_part in path_parts:
            part, mask = path_part
            if part == 'date':
                path.append(time.strftime(mask, metadata['date_taken']))
            elif part == 'location':
                if(
                    metadata['latitude'] is not None and
                    metadata['longitude'] is not None
                ):
                    place_name = geolocation.place_name(
                        metadata['latitude'],
                        metadata['longitude']
                    )
                    if(place_name is not None):
                        location_parts = re.findall('(%[^%]+)', mask)
                        parsed_folder_name = self.parse_mask_for_location(
                            mask,
                            location_parts,
                            place_name,
                        )
                        path.append(parsed_folder_name)

        # For now we always make the leaf folder an album if it's in the EXIF.
        # This is to preserve backwards compatability until we figure out how
        # to include %album in the config.ini syntax.
        if(metadata['album'] is not None):
            if(len(path) == 1):
                path.append(metadata['album'])
            elif(len(path) == 2):
                path[1] = metadata['album']

        # if we don't have a 2nd level directory we use 'Unknown Location'
        if(len(path) < 2):
            path.append('Unknown Location')

        # return '/'.join(path[::-1])
        return os.path.join(*path)

    def parse_mask_for_location(self, mask, location_parts, place_name):
        """Takes a mask for a location and interpolates the actual place names.

        Given these parameters here are the outputs.

        mask=%city
        location_parts=[('%city','%city','city')]
        place_name={'city': u'Sunnyvale'}
        output=Sunnyvale

        mask=%city-%state
        location_parts=[('%city-','%city','city'), ('%state','%state','state')]
        place_name={'city': u'Sunnyvale', 'state': u'California'}
        output=Sunnyvale-California

        mask=%country
        location_parts=[('%country','%country','country')]
        place_name={'default': u'Sunnyvale', 'city': u'Sunnyvale'}
        output=Sunnyvale


        :param str mask: The location mask in the form of %city-%state, etc
        :param list location_parts: A list of tuples in the form of
            [('%city-', '%city', 'city'), ('%state', '%state', 'state')]
        :param dict place_name: A dictionary of place keywords and names like
            {'default': u'California', 'state': u'California'}
        :returns: str
        """
        found = False
        folder_name = mask
        for loc_part in location_parts:
            # We assume the search returns a tuple of length 2.
            # If not then it's a bad mask in config.ini.
            # loc_part = '%country-random'
            # component_full = '%country-random'
            # component = '%country'
            # key = 'country
            component_full, component, key = re.search(
                '((%([a-z]+))[^%]*)',
                loc_part
            ).groups()

            if(key in place_name):
                found = True
                replace_target = component
                replace_with = place_name[key]
            else:
                replace_target = component_full
                replace_with = ''

            folder_name = folder_name.replace(
                replace_target,
                replace_with,
            )

        if(not found and folder_name == ''):
            folder_name = place_name['default']

        return folder_name

    def process_file(self, _file, destination, media, **kwargs):
        move = False
        if('move' in kwargs):
            move = kwargs['move']

        allow_duplicate = False
        if('allowDuplicate' in kwargs):
            allow_duplicate = kwargs['allowDuplicate']

        if(not media.is_valid()):
            print('%s is not a valid media file. Skipping...' % _file)
            return

        metadata = media.get_metadata()

        directory_name = self.get_folder_path(metadata)

        dest_directory = os.path.join(destination, directory_name)
        file_name = self.get_file_name(media)
        dest_path = os.path.join(dest_directory, file_name)

        db = Db()
        checksum = db.checksum(_file)
        if(checksum is None):
            log.info('Could not get checksum for %s. Skipping...' % _file)
            return

        # If duplicates are not allowed then we check if we've seen this file
        #  before via checksum. We also check that the file exists at the
        #   location we believe it to be.
        # If we find a checksum match but the file doesn't exist where we
        #  believe it to be then we write a debug log and proceed to import.
        checksum_file = db.get_hash(checksum)
        if(allow_duplicate is False and checksum_file is not None):
            if(os.path.isfile(checksum_file)):
                log.info('%s already exists at %s. Skipping...' % (
                    _file,
                    checksum_file
                ))
                return
            else:
                log.info('%s matched checksum but file not found at %s. Importing again...' % (  # noqa
                    _file,
                    checksum_file
                ))

        self.create_directory(dest_directory)

        if(move is True):
            stat = os.stat(_file)
            shutil.move(_file, dest_path)
            os.utime(dest_path, (stat.st_atime, stat.st_mtime))
        else:
            # Do not use copy2(), will have an issue when copying to a network/mounted drive
            # using copy and manual set_date_from_filename gets the job done
            # shutil.copy(_file, dest_path)
            
            # shutil.copy seems slow, changing to streaming according to
            # http://stackoverflow.com/questions/22078621/python-how-to-copy-files-fast
            if (constants.python_version == 3):
                shutil.copy(_file, dest_path)
            else:
                compatability._copyfile(_file, dest_path)
            self.set_utime(media)


        db.add_hash(checksum, dest_path)
        db.update_hash_db()

        return dest_path

    def copyfile(self, src, dst):
        try:
            O_BINARY = os.O_BINARY
        except:
            O_BINARY = 0

        READ_FLAGS = os.O_RDONLY | O_BINARY
        WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
        BUFFER_SIZE = 128*1024
        
        try:
            fin = os.open(src, READ_FLAGS)
            stat = os.fstat(fin)
            fout = os.open(dst, WRITE_FLAGS, stat.st_mode)
            for x in iter(lambda: os.read(fin, BUFFER_SIZE), ""):
                os.write(fout, x)
        finally:
            try: os.close(fin)
            except: pass
            try: os.close(fout)
            except: pass
        

    def set_date_from_filename(self, file):
        """ Set the modification time on the file base on the file name.
        """
    
        date_taken = None
        file_name = os.path.basename(file)
        # Initialize date taken to what's returned from the metadata function.
        # If the folder and file name follow a time format of
        #   YYYY-MM/DD-IMG_0001.JPG then we override the date_taken
        (year, month, day, hour, minute, second) = [None] * 6
        year_month_day_match = re.search('(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})', file_name)
        if(year_month_day_match is not None):
            (year, month, day, hour, minute, second) = year_month_day_match.groups()        

        # check if the file system path indicated a date and if so we
        #   override the metadata value
        if(year is not None and month is not None and day is not None and hour is not None and minute is not None and second is not None):
                date_taken = time.strptime(
                    '{}-{}-{} {}:{}:{}'.format(year, month, day, hour, minute, second),
                    '%Y-%m-%d %H:%M:%S'
                )            
        
                os.utime(file, (time.time(), time.mktime(date_taken)))
    
    def set_date_from_path_video(self, video):
        """Set the modification time on the file based on the file path.

        Noop if the path doesn't match the format YYYY-MM/DD-IMG_0001.JPG.

        :param elodie.media.video.Video video: An instance of Video.
        """

        # Initialize date taken to what's returned from the metadata function.
        # If the folder and file name follow a time format of
        #   YYYY-MM-DD_HH-MM-SS-IMG_0001.JPG then we override the date_taken
        file_path = media.get_file_path()
        metadata = media.get_metadata()
        date_taken = metadata['date_taken']
        base_name = metadata['base_name']
        year_month_day_match = re.search(
            '^(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})',
            base_name
        )
        if(year_month_day_match is not None):
            (year, month, day, hour, minute, second) = year_month_day_match.groups()  # noqa
            date_taken = time.strptime(
                '{}-{}-{} {}:{}:{}'.format(year, month, day, hour, minute, second),  # noqa
                '%Y-%m-%d %H:%M:%S'
            )

            os.utime(file_path, (time.time(), time.mktime(date_taken)))
        else:
            # We don't make any assumptions about time zones and
            # assume local time zone.
            date_taken_in_seconds = time.mktime(date_taken)
            os.utime(file_path, (time.time(), (date_taken_in_seconds)))
