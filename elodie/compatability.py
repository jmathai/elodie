import os
import shutil
import sys

from . import constants


def _decode(string, encoding=sys.getfilesystemencoding()):
    """Return a utf8 encoded unicode string.

    Python2 and Python3 differ in how they handle strings.
    So we do a few checks to see if the string is ascii or unicode.
    Then we decode it if needed.
    """
    if hasattr(string, 'decode'):
        # If the string is already unicode we return it.
        try:
            if isinstance(string, unicode):
                return string
        except NameError:
            pass

        return string.decode(encoding)

    return string


def _copyfile(src, dst):
    # shutil.copy seems slow, changing to streaming according to
    # http://stackoverflow.com/questions/22078621/python-how-to-copy-files-fast  # noqa
    # Python 3 hangs using open/write method so we proceed with shutil.copy
    #  and only perform the optimized write for Python 2.
    if (constants.python_version == 3):
        # Do not use copy2(), it will have an issue when copying to a
        #  network/mounted drive.
        # Using copy and manual set_date_from_filename gets the job done.
        # The calling function is responsible for setting the time.
        shutil.copy(src, dst)
        return

    try:
        O_BINARY = os.O_BINARY
    except:
        O_BINARY = 0

    READ_FLAGS = os.O_RDONLY | O_BINARY
    WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
    TEN_MEGABYTES = 10485760
    BUFFER_SIZE = min(TEN_MEGABYTES, os.path.getsize(src))

    try:
        fin = os.open(src, READ_FLAGS)
        stat = os.fstat(fin)
        fout = os.open(dst, WRITE_FLAGS, stat.st_mode)
        for x in iter(lambda: os.read(fin, BUFFER_SIZE), ""):
            os.write(fout, x)
    finally:
        try:
            os.close(fin)
        except:
            pass
        try:
            os.close(fout)
        except:
            pass


# If you want cross-platform overwriting of the destination, 
# use os.replace() instead of rename().
# https://docs.python.org/3/library/os.html#os.rename
def _rename(src, dst):
    if (constants.python_version == 3):
        return os.replace(src, dst)
    else:
        return os.rename(src, dst)
