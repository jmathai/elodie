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

from elodie import compatability
from elodie import geolocation
from elodie import log
from elodie.config import load_config
from elodie.localstorage import Db
from elodie.media.base import Base, get_all_subclasses


class FileSystem(object):
    """A class for interacting with the file system."""

    def __init__(self):
        # The default directory path is along the lines of 2015-01-Jan/Chicago
        self.default_directory_path_definition = {
            'date': '%Y-%m-%b',
            'location': '%city',
            'full_path': '%date/%album|%location|"{}"'.format(
                            geolocation.__DEFAULT_LOCATION__
                         ),
        }
        self.default_file_path_definition = {
            'date': '%Y-%m-%d_%H-%M-%S',
            'full_path': '%date-%basename-%title.%extension',
        }
        self.cached_path_definitions = {}
        self.default_parts = ['album', 'city', 'state', 'country']
        self.kind = {'directory': 'directory', 'file': 'file'}

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
        return self.get_file_name_v1(media)


    def get_file_name_v1(self, media):
        """Original and depcrecated version of get_file_name.
        This method acts as a fallback. See #107 for details.
        Generate file name for a photo or video using its metadata.

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

        # First we check if we have metadata['original_name'].
        # We have to do this for backwards compatibility because
        #   we original did not store this back into EXIF.
        if('original_name' in metadata and metadata['original_name']):
            base_name = os.path.splitext(metadata['original_name'])[0]
        else:
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

        file_name = self.get_path(self.kind['file'], metadata).lower()
        """
        jmathai
        TODO
        .lower() shoud probably be elsewhere, maybe get_path
        """
        return file_name.lower()

        """
        jmathai
        TODO
        this is the old code which should be replaced with get_path
        """
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

    def get_path_definition(self, kind=None):
        """Returns a list of directory definitions.

        Each element in the list represents a directory.
        Fallback directories are supported and are nested lists.
        Return values take the following form.
        [
            [('date', '%Y-%m-%d')],
            [
                ('location', '%city'),
                ('album', ''),
                ('"Unknown Location", '')
            ]
        ]

        :returns: list
        """
        # If we've done this already then return it immediately without
        # incurring any extra work
        if kind in self.cached_path_definitions:
            return self.cached_path_definitions[kind]

        config = load_config()

        if kind == self.kind['directory']:
            # If Directory is in the config we assume full_path and its
            #  corresponding values (date, location) are also present
            config_def = self.default_directory_path_definition
            if 'Directory' in config:
                config_def = config['Directory']
        elif kind == self.kind['file']:
            config_def = self.default_file_path_definition
            if 'File' in config:
                config_def = config['File']
        else:
            pass

        # Find all subpatterns of full_path that map to directories.
        #  I.e. %foo/%bar => ['foo', 'bar']
        #  I.e. %foo/%bar|%example|"something" => ['foo', 'bar|example|"something"']
        valid_characters = '[^/]' if kind == self.kind['directory'] else '[a-z]'
        path_parts = re.findall(
                         '(\%{}+)'.format(valid_characters),
                         config_def['full_path']
                     )

        if not path_parts or len(path_parts) == 0:
            return self.default_directory_path_definition

        self.cached_path_definitions[kind] = []
        for part in path_parts:
            if part in config_def:
                part = part[1:]
                self.cached_path_definitions[kind].append(
                    [(part, config_def[part])]
                )
            elif part in self.default_parts:
                part = part[1:]
                self.cached_path_definitions[kind].append(
                    [(part, '')]
                )
            else:
                this_part = []
                for p in part.split('|'):
                    p = p[1:]
                    this_part.append(
                        (p, config_def[p] if p in config_def else '')
                    )
                self.cached_path_definitions[kind].append(this_part)

        return self.cached_path_definitions[kind]

    def get_path(self, kind, metadata):
        """Given a media's metadata this function returns the directory or file path as a string.

        :param metadata dict: Metadata dictionary.
        :returns: str
        """

        """
        jmathai
        TODO REFACTOR THIS
        This is the closest working code but there's an issue with trimming non template ccharacters.
        reproduce by running this test
        nosetests elodie/tests/filesystem_test.py:test_process_existing_file_without_changes
        """
        def build_path(path, part, value, kind):
            if kind == self.kind['directory']:
                path = list(os.path.split(path))
                path.append(value)
                return os.path.join(*path)
            else:
                if path == '':
                    config = load_config()
                    path = self.default_file_path_definition['full_path']
                    if 'File' in config and 'full_path' in config['File']:
                        path = config['File']['full_path']

                regex = r'(\%({})([^%]*))'.format(part)
                if not value or len(re.findall(regex, path)) == 0:
                    path = re.sub(
                        regex,
                        '',
                        path)
                else:
                    path = re.sub(
                        regex,
                        r'{}\3'.format(value),
                        path)
                return path

        path_parts = self.get_path_definition(kind)
        path = ''
        for path_part in path_parts:
            # We support fallback values so that
            #  'album|city|"Unknown Location"
            #  %album|%city|"Unknown Location" results in
            #  My Album - when an album exists
            #  Sunnyvale - when no album exists but a city exists
            #  Unknown Location - when neither an album nor location exist
            for this_part in path_part:
                part, mask = this_part
                if part in ('date', 'day', 'month', 'year'):
                    path = build_path(path, part, time.strftime(mask, metadata['date_taken']), kind)
                    break
                elif part in ('location', 'city', 'state', 'country'):
                    place_name = geolocation.place_name(
                        metadata['latitude'],
                        metadata['longitude']
                    )

                    location_parts = re.findall('(%[^%]+)', mask)
                    parsed_directory_name = self.parse_mask_for_location(
                        mask,
                        location_parts,
                        place_name,
                    )
                    path = build_path(path, part, parsed_directory_name, kind)
                    break
                elif part in ('album', 'title', 'extension'):
                    if part in metadata:
                        path = build_path(path, part, metadata[part], kind)
                        break
                elif part in ('basename'):
                    if 'base_name' in metadata:
                        path = build_path(path, part, metadata['base_name'], kind)
                        break
                elif part in ('filename'):
                    if 'original_name' in metadata:
                        path = build_path(path, part, metadata['original_name'], kind)
                        break
                elif part.startswith('"') and part.endswith('"'):
                    path = build_path(path, part, part[1:-1], kind)

        return path

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
        directory_name = mask
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

            directory_name = directory_name.replace(
                replace_target,
                replace_with,
            )

        if(not found and directory_name == ''):
            directory_name = place_name['default']

        return directory_name

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

        media.set_original_name()
        metadata = media.get_metadata()

        directory_name = self.get_path(self.kind['directory'], metadata)

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

        # If source and destination are identical then
        #  we should not write the file. gh-210
        if(_file == dest_path):
            print('Final source and destination path should not be identical')
            return

        self.create_directory(dest_directory)

        if(move is True):
            stat = os.stat(_file)
            shutil.move(_file, dest_path)
            os.utime(dest_path, (stat.st_atime, stat.st_mtime))
        else:
            compatability._copyfile(_file, dest_path)
            self.set_utime(media)

        db.add_hash(checksum, dest_path)
        db.update_hash_db()

        return dest_path

    def set_utime(self, media):
        """ Set the modification time on the file based on the file name.
        """

        # Initialize date taken to what's returned from the metadata function.
        # If the directory and file name follow a time format of
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
