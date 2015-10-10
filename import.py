#!/usr/bin/env python

import os
import shutil
import sys

from elodie import arguments
from elodie.media.photo import Photo
from elodie.media.video import Video
from elodie.filesystem import FileSystem
from elodie.localstorage import Db

def main(argv):
    args = arguments.parse(argv, None, ['type=','source=','destination='], './import.py --type=<photo or video> --source=<source directory> -destination=<destination directory>')

    db = Db()

    source = args['source']
    destination = args['destination']

    filesystem = FileSystem()
    if(args['type'] == 'photo'):
        media_type = Photo
    else:
        media_type = Video

    write_counter = 0
    for current_file in filesystem.get_all_files(source, media_type.get_valid_extensions()):
        checksum = db.checksum(current_file)
        if(checksum == None):
            print 'Could not get checksum for %s. Skipping...' % current_file
            continue

        if(db.check_hash(checksum) == True):
            print '%s already exists at %s. Skipping...' % (current_file, db.get_hash(checksum))
            continue

        media = media_type(current_file)

        if(media_type.__name__ == 'Video'):
            filesystem.set_date_from_path_video(media)

        metadata = media.get_metadata()

        directory_name = filesystem.get_folder_path(date=metadata['date_taken'], latitude=metadata['latitude'], longitude=metadata['longitude'])
        #directory_name = filesystem.get_folder_path(date=metadata['date_taken'])
        dest_directory = '%s/%s' % (destination, directory_name)
        # TODO remove the day prefix of the file that was there prior to the crawl
        file_name = filesystem.get_file_name(media)
        dest_path = '%s/%s' % (dest_directory, file_name)

        filesystem.create_directory(dest_directory)

        print '%s -> %s' % (current_file, dest_path)
        shutil.copy2(current_file, dest_path)
        #shutil.move(current_file, dest_path)
        db.add_hash(checksum, dest_path)

        # Write to the hash database every 10 iterations
        write_counter += 1
        if(write_counter % 10 == 0):
            db.update_hash_db()



    # If there's anything we haven't written to the hash database then write it now
    if(write_counter % 10 != 10):
        db.update_hash_db()

if __name__ == '__main__':
    main(sys.argv[1:])
