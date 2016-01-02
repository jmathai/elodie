"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Parse OS X plists.
Wraps standard lib plistlib (https://docs.python.org/3/library/plistlib.html)
Plist class to parse and interact with a plist file.
"""

# load modules
from os import path

import plistlib


class Plist(object):
    def __init__(self, source):
        if(path.isfile(source) == False):
            raise IOError('Could not load plist file %s' % source)

        self.source = source
        self.plist = plistlib.readPlist(self.source)

    def update_key(self, key, value):
        self.plist[key] = value

    def write_file(self, destination):
        plistlib.writePlist(self.plist, destination)
