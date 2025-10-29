"""
Helpers for checking for an interacting with external dependencies. These are
things that Elodie requires, but aren't installed automatically for the user.
"""
from __future__ import print_function

import os
import sys
import shutil


#: Error to print when exiftool can't be found.
EXIFTOOL_ERROR = u"""
It looks like you don't have exiftool installed, which Elodie requires.
Please take a look at the installation steps in the readme:

https://github.com/jmathai/elodie#install-everything-you-need
""".lstrip()


def get_exiftool():
    """Get path to executable exiftool binary.

    We wrap this since we call it in a few places and we do a fallback.

    :returns: str or None
    """
    path = shutil.which('exiftool')
    # If exiftool wasn't found we try to brute force the homebrew location
    if path is None:
        path = '/usr/local/bin/exiftool'
        if not os.path.isfile(path) or not os.access(path, os.X_OK):
            return None
    return path


def verify_dependencies():
    """Verify that external dependencies are installed.

    Prints a message to stderr and returns False if any dependencies are
    missing.

    :returns: bool
    """
    exiftool = get_exiftool()
    if exiftool is None:
        print(EXIFTOOL_ERROR, file=sys.stderr)
        return False

    return True
