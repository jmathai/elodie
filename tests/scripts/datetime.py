#!/usr/bin/env python

import os
import shutil
import sys

from elodie import arguments
from elodie.media.photo import Media
from elodie.media.photo import Photo
from elodie.media.video import Video

def main(argv):
    args = arguments.parse(argv, None, ['file='], './import.py --file=<path to file>')

    if('file' not in args):
        print 'No file specified'
        sys.exit(1)

    media = Media.get_class_by_file(args['file'], [Photo, Video])

    if(media is None):
        print 'Not a valid file'
        sys.exit(1)

    metadata = media.get_metadata()
    output = {'date_taken': metadata['date_taken']}
    print '%r' % output


if __name__ == '__main__':
    main(sys.argv[1:])
    sys.exit(0)
