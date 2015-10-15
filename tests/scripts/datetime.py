#!/usr/bin/env python

import os
import shutil
import sys

from elodie import arguments
from elodie.media.photo import Photo
from elodie.media.video import Video

def main(argv):
    args = arguments.parse(argv, None, ['file=','type='], './import.py --type=<photo or video> --file=<path to file>')

    if('file' not in args):
        print 'No file specified'
        sys.exit(1)

    if('type' in args and args['type'] == 'video'):
        media_type = Video
    else:
        media_type = Photo

    media = media_type(args['file'])
    metadata = media.get_metadata()

    print '%r' % metadata

    output = {'date_taken': metadata['date_taken']}
    print '%r' % output


if __name__ == '__main__':
    main(sys.argv[1:])
    sys.exit(0)
