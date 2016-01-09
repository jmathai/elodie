"""
Helpers for checking for an interacting with external dependencies. These are
things that Elodie requires, but aren't installed automatically for the user.
"""

import os
import sys
from distutils.spawn import find_executable


#: Error to print when exiftool can't be found.
EXIFTOOL_ERROR = u"""
It looks like you don't have exiftool installed, which Elodie requires.
Please take a look at the installation steps in the readme:

https://github.com/jmathai/elodie#install-everything-you-need
""".lstrip()

#: Template for the error to print when pyexiv2 can't be found.
PYEXIV2_ERROR = u"""
{error_class_name}: {error}

It looks like you don't have pyexiv2 installed, which Elodie requires for
geolocation. Please take a look at the installation steps in the readme:

https://github.com/jmathai/elodie#install-everything-you-need
""".lstrip()


def get_exiftool():
    """Get path to executable exiftool binary.

    We wrap this since we call it in a few places and we do a fallback.

    :returns: str or None
    """
    path = find_executable('exiftool')
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
        print >>sys.stderr, EXIFTOOL_ERROR
        return False

    try:
        import pyexiv2
    except ImportError as e:
        print >>sys.stderr, PYEXIV2_ERROR.format(
            error_class_name=e.__class__.__name__, error=e)
        return False

    return True
