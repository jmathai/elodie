"""
Parse OS X plists.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""

# load modules
from os import path

import plistlib


class Plist(object):

    """Parse and interact with a plist file.

    This class wraps the `plistlib module`_ from the standard library.

    .. _plistlib module: https://docs.python.org/3/library/plistlib.html

    :param str source: Source to read the plist from.
    """

    def __init__(self, source):
        if not path.isfile(source):
            raise IOError('Could not load plist file %s' % source)
        self.source = source
        self.plist = plistlib.readPlist(self.source)

    def update_key(self, key, value):
        """Update a value in the plist.

        :param str key: Key to modify.
        :param value: New value.
        """
        self.plist[key] = value

    def write_file(self, destination):
        """Save the plist.

        :param destination: Write the plist here.
        :type destination: str or file object
        """
        plistlib.writePlist(self.plist, destination)
