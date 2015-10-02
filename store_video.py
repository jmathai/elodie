#!/usr/bin/env python

import os
import shutil
import sys

from elodie.media.video import Video
from elodie.filesystem import FileSystem

print 'Running with arguments %r' % sys.argv

destination = '%s/Dropbox/Videos' % os.path.expanduser('~')

if __name__ == '__main__':
    if(len(sys.argv) < 2):
        print "No arguments passed"
        sys.exit(0)

    file_path = sys.argv[1]

    filesystem = FileSystem()
    video = Video(file_path)

    # check if the file is valid else exit
    if(not video.is_valid()):
        print "File is not valid"
        sys.exit(0)

    metadata = video.get_metadata()

    directory_name = filesystem.get_folder_name_by_date(metadata['date_taken'])
    dest_directory = '%s/%s' % (destination, directory_name)
    file_name = filesystem.get_file_name_for_video(video)

    dest = '%s/%s' % (dest_directory, file_name)

    if not os.path.exists(dest_directory):
        os.makedirs(dest_directory)

    shutil.copy2(file_path, dest)
