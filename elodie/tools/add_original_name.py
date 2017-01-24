from __future__ import print_function

import os
import re
import sys

from elodie import constants
from elodie import geolocation
from elodie import log
from elodie.compatability import _decode
from elodie.filesystem import FileSystem
from elodie.localstorage import Db
from elodie.media.base import Base, get_all_subclasses
from elodie.media.media import Media
from elodie.media.text import Text
from elodie.media.audio import Audio
from elodie.media.photo import Photo
from elodie.media.video import Video
from elodie.result import Result

def main(argv):
    filesystem = FileSystem()
    result = Result()
    subclasses = get_all_subclasses()

    paths = argv[1:]

    for path in paths:
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            for source in filesystem.get_all_files(path, None):
                status = add_original_name(source, subclasses)
                result.append((_decode(source), status))
        else:
            status = add_original_name(path, subclasses)
            result.append((_decode(path), status))

    result.write()

def add_original_name(source, subclasses):
    media = Media.get_class_by_file(source, subclasses)
    if media is None:
        print('{} is not a valid media object'.format(source))
        return

    metadata = media.get_metadata()
    if metadata['original_name'] is not None:
        print('{} already has OriginalFileName...Skipping'.format(source))
        return

    original_name = parse_original_name_from_media(metadata)
    return media.set_original_name(original_name)

def parse_original_name_from_media(metadata):
    # 2015-07-23_04-31-12-img_9414-test3.jpg
    base_name = metadata['base_name']
    title = metadata['title']
    extension = metadata['extension']
    date_regex = r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-'
    if not re.match(date_regex, base_name):
        print("File name did not match date pattern...Skipping")
        return

    trimmed_base_name = re.sub(date_regex, '', base_name)
    if title:
        normalized_title = re.sub(r'\W+', '-', title.lower())
        trimmed_base_name = trimmed_base_name.replace(
            '-{}'.format(normalized_title), 
            ''
        )

    return '{}.{}'.format(trimmed_base_name, extension)

if __name__ == "__main__":
    main(sys.argv)
