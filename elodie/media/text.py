"""
The text module provides a base :class:`Text` class for text files that
are tracked by Elodie.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""

from json import dumps, loads
import os
from shutil import copy2, copyfileobj
import time

# load modules
from elodie import log
from elodie.media.base import Base


class Text(Base):

    """The class for all text files.

    :param str source: The fully qualified path to the text file.
    """

    __name__ = 'Text'

    #: Valid extensions for text files.
    extensions = ('txt',)

    def __init__(self, source=None):
        super(Text, self).__init__(source)
        self.reset_cache()

    def get_album(self):
        self.parse_metadata_line()
        if(not isinstance(self.metadata_line, dict) or
                'album' not in self.metadata_line):
            return None

        return self.metadata_line['album']

    def get_coordinate(self, type='latitude'):
        self.parse_metadata_line()
        if not self.metadata_line:
            return None
        elif type in self.metadata_line:
            if type == 'latitude':
                return self.metadata_line['latitude'] or None
            elif type == 'longitude':
                return self.metadata_line['longitude'] or None

        return None

    def get_date_taken(self):
        source = self.source
        self.parse_metadata_line()

        # We return the value if found in metadata
        if(isinstance(self.metadata_line, dict) and
                'date_taken' in self.metadata_line):
            return time.gmtime(self.metadata_line['date_taken'])

        # If there's no date_taken in the metadata we return
        #   from the filesystem
        seconds_since_epoch = min(
            os.path.getmtime(source),
            os.path.getctime(source)
        )
        return time.gmtime(seconds_since_epoch)

    def get_metadata(self):
        self.parse_metadata_line()
        return super(Text, self).get_metadata()

    def get_original_name(self):
        self.parse_metadata_line()

        # We return the value if found in metadata
        if(isinstance(self.metadata_line, dict) and
                'original_name' in self.metadata_line):
            return self.metadata_line['original_name']

        return super(Text, self).get_original_name()

    def get_title(self):
        self.parse_metadata_line()

        if(not isinstance(self.metadata_line, dict) or
                'title' not in self.metadata_line):
            return None

        return self.metadata_line['title']

    def reset_cache(self):
        """Resets any internal cache
        """
        self.metadata_line = None
        super(Text, self).reset_cache()

    def set_album(self, name):
        status = self.write_metadata(album=name)
        self.reset_cache()
        return status

    def set_date_taken(self, passed_in_time):
        if(time is None):
            return False

        seconds_since_epoch = time.mktime(passed_in_time.timetuple())
        status = self.write_metadata(date_taken=seconds_since_epoch)
        self.reset_cache()
        return status

    def set_original_name(self, name=None):
        """Sets the original name if not already set.

        :returns: True, False, None
        """
        if(not self.is_valid()):
            return None

        # If EXIF original name tag is set then we return.
        if self.get_original_name() is not None:
            return None

        source = self.source

        if not name:
            name = os.path.basename(source)

        status = self.write_metadata(original_name=name)
        self.reset_cache()
        return status

    def set_location(self, latitude, longitude):
        status = self.write_metadata(latitude=latitude, longitude=longitude)
        self.reset_cache()
        return status

    def parse_metadata_line(self):
        if isinstance(self.metadata_line, dict):
            return self.metadata_line

        source = self.source
        if source is None:
            return None

        try:
            with open(source, 'r') as f:
                first_line = f.readline().strip()
        except UnicodeDecodeError:
            # Handle non-UTF-8 files by reading with error handling
            with open(source, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()

        try:
            parsed_json = loads(first_line)
            if isinstance(parsed_json, dict):
                self.metadata_line = parsed_json
        except ValueError:
            log.error('Could not parse JSON from first line: %s' % first_line)
            pass

    def write_metadata(self, **kwargs):
        if len(kwargs) == 0:
            return False

        source = self.source

        self.parse_metadata_line()

        # Set defaults for a file without metadata
        # Check if self.metadata_line is set and use that instead
        metadata_line = {}
        has_metadata = False
        if isinstance(self.metadata_line, dict):
            metadata_line = self.metadata_line
            has_metadata = True

        for name in kwargs:
            metadata_line[name] = kwargs[name]

        metadata_as_json = dumps(metadata_line)
        
        # Create an _original copy just as we do with exiftool
        # This is to keep all file processing logic in line with exiftool
        copy2(source, source + '_original')

        if has_metadata:
            # Update the first line of this file in place
            # http://stackoverflow.com/a/14947384
            with open(source, 'r') as f_read:
                f_read.readline()
                with open(source, 'w') as f_write:
                    f_write.write("{}\n".format(metadata_as_json))
                    copyfileobj(f_read, f_write)
        else:
            # Prepend the metadata to the file
            with open(source, 'r') as f_read:
                original_contents = f_read.read()
                with open(source, 'w') as f_write:
                    f_write.write("{}\n{}".format(
                        metadata_as_json,
                        original_contents)
                    )

        self.reset_cache()
        return True
