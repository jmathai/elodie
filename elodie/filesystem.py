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
from elodie.plugins.plugins import Plugins

class FileSystem(object):
    """A class for interacting with the file system."""

    def __init__(self):
        # The default folder path is along the lines of 2017-06-17_01-04-14-dsc_1234-some-title.jpg
        self.default_file_name_definition = {
            'date': '%Y-%m-%d_%H-%M-%S',
            'name': '%date-%original_name-%title.%extension',
        }
        # The default folder path is along the lines of 2015-01-Jan/Chicago
        self.default_folder_path_definition = {
            'date': '%Y-%m-%b',
            'location': '%city',
            'full_path': '%date/%album|%location|"{}"'.format(
                            geolocation.__DEFAULT_LOCATION__
                         ),
        }
        self.cached_file_name_definition = None
        self.cached_folder_path_definition = None
        # Python3 treats the regex \s differently than Python2.
        # It captures some additional characters like the unicode checkmark \u2713.
        # See build failures in Python3 here.
        #  https://travis-ci.org/jmathai/elodie/builds/483012902
        self.whitespace_regex = '[ \t\n\r\f\v]+'

        # Instantiate a plugins object
        self.plugins = Plugins()

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

    def get_all_files(self, path, extensions=None, exclude_regex_list=set()):
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

        # Create a list of compiled regular expressions to match against the file path
        compiled_regex_list = [re.compile(regex) for regex in exclude_regex_list]
        for dirname, dirnames, filenames in os.walk(path):
            for filename in filenames:
                # If file extension is in `extensions` 
                # And if file path is not in exclude regexes
                # Then append to the list
                filename_path = os.path.join(dirname, filename)
                if (
                        os.path.splitext(filename)[1][1:].lower() in extensions and
                        not self.should_exclude(filename_path, compiled_regex_list, False)
                    ):
                    yield filename_path

    def get_current_directory(self):
        """Get the current working directory.

        :returns: str
        """
        return os.getcwd()

    def get_file_name(self, metadata):
        """Generate file name for a photo or video using its metadata.

        Originally we hardcoded the file name to include an ISO date format.
        We use an ISO8601-like format for the file name prefix. Instead of
        colons as the separator for hours, minutes and seconds we use a hyphen.
        https://en.wikipedia.org/wiki/ISO_8601#General_principles

        PR #225 made the file name customizable and fixed issues #107 #110 #111.
        https://github.com/jmathai/elodie/pull/225

        :param media: A Photo or Video instance
        :type media: :class:`~elodie.media.photo.Photo` or
            :class:`~elodie.media.video.Video`
        :returns: str or None for non-photo or non-videos
        """
        if(metadata is None):
            return None

        # Get the name template and definition.
        # Name template is in the form %date-%original_name-%title.%extension
        # Definition is in the form
        #  [
        #    [('date', '%Y-%m-%d_%H-%M-%S')],
        #    [('original_name', '')], [('title', '')], // contains a fallback
        #    [('extension', '')]
        #  ]
        name_template, definition = self.get_file_name_definition()

        name = name_template
        for parts in definition:
            this_value = None
            for this_part in parts:
                part, mask = this_part
                if part in ('date', 'day', 'month', 'year'):
                    this_value = time.strftime(mask, metadata['date_taken'])
                    break
                elif part in ('location', 'city', 'state', 'country'):
                    place_name = geolocation.place_name(
                        metadata['latitude'],
                        metadata['longitude']
                    )

                    location_parts = re.findall('(%[^%]+)', mask)
                    this_value = self.parse_mask_for_location(
                        mask,
                        location_parts,
                        place_name,
                    )
                    break
                elif part in ('album', 'extension', 'title'):
                    if metadata[part]:
                        this_value = re.sub(self.whitespace_regex, '-', metadata[part].strip())
                        break
                elif part in ('original_name'):
                    # First we check if we have metadata['original_name'].
                    # We have to do this for backwards compatibility because
                    #   we original did not store this back into EXIF.
                    if metadata[part]:
                        this_value = os.path.splitext(metadata['original_name'])[0]
                    else:
                        # We didn't always store original_name so this is 
                        #  for backwards compatability.
                        # We want to remove the hardcoded date prefix we used 
                        #  to add to the name.
                        # This helps when re-running the program on file 
                        #  which were already processed.
                        this_value = re.sub(
                            '^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-',
                            '',
                            metadata['base_name']
                        )
                        if(len(this_value) == 0):
                            this_value = metadata['base_name']

                    # Lastly we want to sanitize the name
                    this_value = re.sub(self.whitespace_regex, '-', this_value.strip())
                elif part.startswith('"') and part.endswith('"'):
                    this_value = part[1:-1]
                    break

            # Here we replace the placeholder with it's corresponding value.
            # Check if this_value was not set so that the placeholder
            #  can be removed completely.
            # For example, %title- will be replaced with ''
            # Else replace the placeholder (i.e. %title) with the value.
            if this_value is None:
                name = re.sub(
                    #'[^a-z_]+%{}'.format(part),
                    '[^a-zA-Z0-9_]+%{}'.format(part),
                    '',
                    name,
                )
            else:
                name = re.sub(
                    '%{}'.format(part),
                    this_value,
                    name,
                )

        config = load_config()

        if('File' in config and 'capitalization' in config['File'] and config['File']['capitalization'] == 'upper'):
            return name.upper()
        else:
            return name.lower()

    def get_file_name_definition(self):
        """Returns a list of folder definitions.

        Each element in the list represents a folder.
        Fallback folders are supported and are nested lists.
        Return values take the following form.
        [
            ('date', '%Y-%m-%d'),
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
        if self.cached_file_name_definition is not None:
            return self.cached_file_name_definition

        config = load_config()

        # If File is in the config we assume name and its
        #  corresponding values are also present
        config_file = self.default_file_name_definition
        if('File' in config):
            config_file = config['File']

        # Find all subpatterns of name that map to the components of the file's
        #  name.
        #  I.e. %date-%original_name-%title.%extension => ['date', 'original_name', 'title', 'extension'] #noqa
        path_parts = re.findall(
                         '(\%[a-z_]+)',
                         config_file['name']
                     )

        if not path_parts or len(path_parts) == 0:
            return (config_file['name'], self.default_file_name_definition)

        self.cached_file_name_definition = []
        for part in path_parts:
            if part in config_file:
                part = part[1:]
                self.cached_file_name_definition.append(
                    [(part, config_file[part])]
                )
            else:
                this_part = []
                for p in part.split('|'):
                    p = p[1:]
                    this_part.append(
                        (p, config_file[p] if p in config_file else '')
                    )
                self.cached_file_name_definition.append(this_part)

        self.cached_file_name_definition = (config_file['name'], self.cached_file_name_definition)
        return self.cached_file_name_definition

    def get_folder_path_definition(self):
        """Returns a list of folder definitions.

        Each element in the list represents a folder.
        Fallback folders are supported and are nested lists.
        Return values take the following form.
        [
            ('date', '%Y-%m-%d'),
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
        if self.cached_folder_path_definition is not None:
            return self.cached_folder_path_definition

        config = load_config()

        # If Directory is in the config we assume full_path and its
        #  corresponding values (date, location) are also present
        config_directory = self.default_folder_path_definition
        if('Directory' in config):
            config_directory = config['Directory']

        # Find all subpatterns of full_path that map to directories.
        #  I.e. %foo/%bar => ['foo', 'bar']
        #  I.e. %foo/%bar|%example|"something" => ['foo', 'bar|example|"something"']
        path_parts = re.findall(
                         '(\%[^/]+)',
                         config_directory['full_path']
                     )

        if not path_parts or len(path_parts) == 0:
            return self.default_folder_path_definition

        self.cached_folder_path_definition = []
        for part in path_parts:
            part = part.replace('%', '')
            if part in config_directory:
                self.cached_folder_path_definition.append(
                    [(part, config_directory[part])]
                )
            else:
                this_part = []
                for p in part.split('|'):
                    this_part.append(
                        (p, config_directory[p] if p in config_directory else '')
                    )
                self.cached_folder_path_definition.append(this_part)

        return self.cached_folder_path_definition

    def get_folder_path(self, metadata, path_parts=None):
        """Given a media's metadata this function returns the folder path as a string.

        :param dict metadata: Metadata dictionary.
        :returns: str
        """
        if path_parts is None:
            path_parts = self.get_folder_path_definition()
        path = []
        for path_part in path_parts:
            # We support fallback values so that
            #  'album|city|"Unknown Location"
            #  %album|%city|"Unknown Location" results in
            #  My Album - when an album exists
            #  Sunnyvale - when no album exists but a city exists
            #  Unknown Location - when neither an album nor location exist
            for this_part in path_part:
                part, mask = this_part
                this_path = self.get_dynamic_path(part, mask, metadata)
                if this_path:
                    path.append(this_path.strip())
                    # We break as soon as we have a value to append
                    # Else we continue for fallbacks
                    break
        return os.path.join(*path)

    def get_dynamic_path(self, part, mask, metadata):
        """Parse a specific folder's name given a mask and metadata.

        :param part: Name of the part as defined in the path (i.e. date from %date)
        :param mask: Mask representing the template for the path (i.e. %city %state
        :param metadata: Metadata dictionary.
        :returns: str
        """

        # Each part has its own custom logic and we evaluate a single part and return
        #  the evaluated string.
        if part in ('custom'):
            custom_parts = re.findall('(%[a-z_]+)', mask)
            folder = mask
            for i in custom_parts:
                folder = folder.replace(
                    i,
                    self.get_dynamic_path(i[1:], i, metadata)
                )
            return folder
        elif part in ('date'):
            config = load_config()
            # If Directory is in the config we assume full_path and its
            #  corresponding values (date, location) are also present
            config_directory = self.default_folder_path_definition
            if('Directory' in config):
                config_directory = config['Directory']
            date_mask = ''
            if 'date' in config_directory:
                date_mask = config_directory['date']
            return time.strftime(date_mask, metadata['date_taken'])
        elif part in ('day', 'month', 'year'):
            return time.strftime(mask, metadata['date_taken'])
        elif part in ('location', 'city', 'state', 'country'):
            place_name = geolocation.place_name(
                metadata['latitude'],
                metadata['longitude']
            )

            location_parts = re.findall('(%[^%]+)', mask)
            parsed_folder_name = self.parse_mask_for_location(
                mask,
                location_parts,
                place_name,
            )
            return parsed_folder_name
        elif part in ('album', 'camera_make', 'camera_model'):
            if metadata[part]:
                return metadata[part]
        elif part.startswith('"') and part.endswith('"'):
            # Fallback string
            return part[1:-1]

        return ''

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

    def process_checksum(self, _file, allow_duplicate):
        db = Db()
        checksum = db.checksum(_file)
        if(checksum is None):
            log.info('Could not get checksum for %s.' % _file)
            return None

        # If duplicates are not allowed then we check if we've seen this file
        #  before via checksum. We also check that the file exists at the
        #   location we believe it to be.
        # If we find a checksum match but the file doesn't exist where we
        #  believe it to be then we write a debug log and proceed to import.
        checksum_file = db.get_hash(checksum)
        if(allow_duplicate is False and checksum_file is not None):
            if(os.path.isfile(checksum_file)):
                log.info('%s already at %s.' % (
                    _file,
                    checksum_file
                ))
                return None
            else:
                log.info('%s matched checksum but file not found at %s.' % (  # noqa
                    _file,
                    checksum_file
                ))
        return checksum

    def process_file(self, _file, destination, media, **kwargs):
        move = False
        if('move' in kwargs):
            move = kwargs['move']

        allow_duplicate = False
        if('allowDuplicate' in kwargs):
            allow_duplicate = kwargs['allowDuplicate']

        stat_info_original = os.stat(_file)
        metadata = media.get_metadata()

        if(not media.is_valid()):
            print('%s is not a valid media file. Skipping...' % _file)
            return

        checksum = self.process_checksum(_file, allow_duplicate)
        if(checksum is None):
            log.info('Original checksum returned None for %s. Skipping...' %
                     _file)
            return

        # Run `before()` for every loaded plugin and if any of them raise an exception
        #  then we skip importing the file and log a message.
        plugins_run_before_status = self.plugins.run_all_before(_file, destination)
        if(plugins_run_before_status == False):
            log.warn('At least one plugin pre-run failed for %s' % _file)
            return

        directory_name = self.get_folder_path(metadata)
        dest_directory = os.path.join(destination, directory_name)
        file_name = self.get_file_name(metadata)
        dest_path = os.path.join(dest_directory, file_name)        

        media.set_original_name()

        # If source and destination are identical then
        #  we should not write the file. gh-210
        if(_file == dest_path):
            print('Final source and destination path should not be identical')
            return

        self.create_directory(dest_directory)

        # exiftool renames the original file by appending '_original' to the
        # file name. A new file is written with new tags with the initial file
        # name. See exiftool man page for more details.
        exif_original_file = _file + '_original'

        # Check if the source file was processed by exiftool and an _original
        # file was created.
        exif_original_file_exists = False
        if(os.path.exists(exif_original_file)):
            exif_original_file_exists = True

        if(move is True):
            stat = os.stat(_file)
            # Move the processed file into the destination directory
            shutil.move(_file, dest_path)

            if(exif_original_file_exists is True):
                # We can remove it as we don't need the initial file.
                os.remove(exif_original_file)
            os.utime(dest_path, (stat.st_atime, stat.st_mtime))
        else:
            if(exif_original_file_exists is True):
                # Move the newly processed file with any updated tags to the
                # destination directory
                shutil.move(_file, dest_path)
                # Move the exif _original back to the initial source file
                shutil.move(exif_original_file, _file)
            else:
                compatability._copyfile(_file, dest_path)

            # Set the utime based on what the original file contained 
            #  before we made any changes.
            # Then set the utime on the destination file based on metadata.
            os.utime(_file, (stat_info_original.st_atime, stat_info_original.st_mtime))
            self.set_utime_from_metadata(metadata, dest_path)

        db = Db()
        db.add_hash(checksum, dest_path)
        db.update_hash_db()

        # Run `after()` for every loaded plugin and if any of them raise an exception
        #  then we skip importing the file and log a message.
        plugins_run_after_status = self.plugins.run_all_after(_file, destination, dest_path, metadata)
        if(plugins_run_after_status == False):
            log.warn('At least one plugin pre-run failed for %s' % _file)
            return


        return dest_path

    def set_utime_from_metadata(self, metadata, file_path):
        """ Set the modification time on the file based on the file name.
        """

        # Initialize date taken to what's returned from the metadata function.
        # If the folder and file name follow a time format of
        #   YYYY-MM-DD_HH-MM-SS-IMG_0001.JPG then we override the date_taken
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

    def should_exclude(self, path, regex_list=set(), needs_compiled=False):
        if(len(regex_list) == 0):
            return False

        if(needs_compiled):
            compiled_list = []
            for regex in regex_list:
                compiled_list.append(re.compile(regex))
            regex_list = compiled_list

        return any(regex.search(path) for regex in regex_list)
