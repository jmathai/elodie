"""
The photo module contains the :class:`Photo` class, which is used to track
image objects (JPG, DNG, etc.).

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function
from __future__ import absolute_import

import imghdr
import os
import re
import time
from datetime import datetime
from re import compile

from elodie import log
from .media import Media


class Photo(Media):

    """A photo object.

    :param str source: The fully qualified path to the photo file
    """

    __name__ = 'Photo'

    #: Valid extensions for photo files.
    extensions = ('arw', 'cr2', 'dng', 'gif', 'heic', 'jpeg', 'jpg', 'nef', 'png', 'rw2')

    def __init__(self, source=None):
        super(Photo, self).__init__(source)

        # We only want to parse EXIF once so we store it here
        self.exif = None

        # Optionally import Pillow - see gh-325
        # https://github.com/jmathai/elodie/issues/325
        self.pillow = None
        try:
            from PIL import Image
            self.pillow = Image
        except ImportError:
            pass

    def get_date_taken(self):
        """Get the date which the photo was taken.

        The date value returned is defined by the min() of mtime and ctime.

        :returns: time object or None for non-photo files or 0 timestamp
        """
        if(not self.is_valid()):
            return None

        source = self.source
        seconds_since_epoch = min(os.path.getmtime(source), os.path.getctime(source))  # noqa

        exif = self.get_exiftool_attributes()
        if not exif:
            return seconds_since_epoch

        # We need to parse a string from EXIF into a timestamp.
        # EXIF DateTimeOriginal and EXIF DateTime are both stored
        #   in %Y:%m:%d %H:%M:%S format
        # we split on a space and then r':|-' -> convert to int -> .timetuple()
        #   the conversion in the local timezone
        # EXIF DateTime is already stored as a timestamp
        # Sourced from https://github.com/photo/frontend/blob/master/src/libraries/models/Photo.php#L500  # noqa
        for key in self.exif_map['date_taken']:
            try:
                if(key in exif):
                    if(re.match('\d{4}(-|:)\d{2}(-|:)\d{2}', exif[key]) is not None):  # noqa
                        dt, tm = exif[key].split(' ')
                        dt_list = compile(r'-|:').split(dt)
                        dt_list = dt_list + compile(r'-|:').split(tm)
                        dt_list = map(int, dt_list)
                        time_tuple = datetime(*dt_list).timetuple()
                        seconds_since_epoch = time.mktime(time_tuple)
                        break
            except BaseException as e:
                log.error(e)
                pass

        if(seconds_since_epoch == 0):
            return None

        return time.gmtime(seconds_since_epoch)

    def is_valid(self):
        """Check the file extension against valid file extensions.

        The list of valid file extensions come from self.extensions. This
        also checks whether the file is an image.

        :returns: bool
        """
        source = self.source

        # HEIC is not well supported yet so we special case it.
        # https://github.com/python-pillow/Pillow/issues/2806
        extension = os.path.splitext(source)[1][1:].lower()
        if(extension != 'heic'):
            # gh-4 This checks if the source file is an image.
            # It doesn't validate against the list of supported types.
            # We check with imghdr and pillow.
            if(imghdr.what(source) is None):
                # Pillow is used as a fallback and if it's not available we trust
                #   what imghdr returned.
                if(self.pillow is None):
                    return False
                else:
                    # imghdr won't detect all variants of images (https://bugs.python.org/issue28591)
                    # see https://github.com/jmathai/elodie/issues/281
                    # before giving up, we use `pillow` imaging library to detect file type
                    #
                    # It is important to note that the library doesn't decode or load the
                    # raster data unless it really has to. When you open a file,
                    # the file header is read to determine the file format and extract
                    # things like mode, size, and other properties required to decode the file,
                    # but the rest of the file is not processed until later.
                    try:
                        im = self.pillow.open(source)
                    except IOError:
                        return False

                    if(im.format is None):
                        return False
        
        return extension in self.extensions
