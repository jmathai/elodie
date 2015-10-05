#!/usr/bin/env python

import os
import shutil
import sys

from elodie.media.video import Video
from elodie.filesystem import FileSystem

destination = '%s/tmp' % os.path.expanduser('~')

filesystem = FileSystem()

for video_file in filesystem.get_all_files('/Users/jaisenmathai/Pictures/Videos/', Video.get_valid_extensions()):
    video = Video(video_file)
    metadata = video.get_metadata()

    directory_name = filesystem.get_folder_name_by_date(metadata['date_taken'])
    dest_directory = '%s/%s' % (destination, directory_name)
    file_name = filesystem.get_file_name_for_video(video)

    print '%s *** %s' % (video_file, file_name)
    #print '%s/%s' % (directory_name, file_name)
