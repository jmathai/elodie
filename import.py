#!/usr/bin/env python

import os
import shutil
import sys

from elodie import arguments
from elodie.media.photo import Photo
from elodie.media.video import Video
from elodie.filesystem import FileSystem
from elodie.localstorage import Db

def help():
    return """
    usage: ./import.py --type=photo --source=/path/to/photos --destination=/path/to/destination

    --type          Valid values are 'photo' or 'video'. Only files of *type* are imported.
    --file          Full path to a photo or video to be imported. The --type argument should match the file type of the file.
                    @TODO: Automatically determine *type* from *file*
    --source        Full path to a directory which will be recursively crawled for files of *type*.
    --destination   Full path to a directory where organized photos will be placed.
    """

def parse_arguments(args):
    config = {
        'type': 'photo',
        'file': None,
        'source': None,
        'destination': None
    }

    if('destination' not in args):
        help()
        sys.exit(2)
    
    config.update(args)
    return config

def process_file(_file, destination, media):
    checksum = db.checksum(_file)
    if(checksum == None):
        print 'Could not get checksum for %s. Skipping...' % _file
        return

    if(db.check_hash(checksum) == True):
        print '%s already exists at %s. Skipping...' % (_file, db.get_hash(checksum))
        return

    metadata = media.get_metadata()

    directory_name = filesystem.get_folder_path(date=metadata['date_taken'], latitude=metadata['latitude'], longitude=metadata['longitude'])

    dest_directory = '%s/%s' % (destination, directory_name)
    # TODO remove the day prefix of the file that was there prior to the crawl
    file_name = filesystem.get_file_name(media)
    dest_path = '%s/%s' % (dest_directory, file_name)

    filesystem.create_directory(dest_directory)

    print '%s -> %s' % (_file, dest_path)
    #shutil.copy2(_file, dest_path)
    shutil.move(_file, dest_path)
    db.add_hash(checksum, dest_path)

def main(argv):

    destination = config['destination']
    if(config['type'] == 'photo'):
        media_type = Photo
    else:
        media_type = Video

    if(config['source'] is not None):
        source = config['source']

        write_counter = 0
        for current_file in filesystem.get_all_files(source, media_type.get_valid_extensions()):
            media = media_type(current_file)

            if(media_type.__name__ == 'Video'):
                filesystem.set_date_from_path_video(media)

            dest_path = filesystem.process_file(current_file, destination, media, allowDuplicate=False, move=False)
            print '%s -> %s' % (current_file, dest_path)
            # Write to the hash database every 10 iterations
            write_counter += 1
            if(write_counter % 10 == 0):
                db.update_hash_db()

        # If there's anything we haven't written to the hash database then write it now
        if(write_counter % 10 != 10):
            db.update_hash_db()
    elif(config['file'] is not None):
        media = media_type(config['file'])
        if(media_type.__name__ == 'Video'):
            filesystem.set_date_from_path_video(media)

        dest_path = process_file(config['file'], destination, media, allowDuplicate=False, move=False)
        print '%s -> %s' % (current_file, dest_path)
        db.update_hash_db()
    else:
        help()

db = Db()
filesystem = FileSystem()
args = arguments.parse(sys.argv[1:], None, ['file=','type=','source=','destination='], help())
config = parse_arguments(args)

if __name__ == '__main__':
    main(config)
    sys.exit(0)
