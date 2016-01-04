"""
Author: Jaisen Mathai <jaisen@jmathai.com>
Audio package that handles all audio operations
Inherits from Video package
"""

from video import Video


class Audio(Video):
    __name__ = 'Audio'
    extensions = ('m4a')

    """
    @param, source, string, The fully qualified path to the audio file
    """
    def __init__(self, source=None):
        super(Audio, self).__init__(source)
